import asyncio
from datetime import datetime

from app.domain.exceptions.stats_exceptions import ServiceUnavailableError
from app.domain.model.dashboard import DashboardStats, SubjectSummary, TaskSummary
from app.domain.ports.in_.dashboard_use_case import DashboardUseCase
from app.domain.ports.out_.stats_snapshot_port import StatsSnapshotPort
from app.infrastructure.external.academic_client import AcademicClient
from app.infrastructure.external.task_client import TaskClient

_PASSING_THRESHOLD = 3.0  # Minimum passing grade (Colombian scale 0–5)
_AT_RISK_THRESHOLD = 3.5  # Below this value a subject is considered at risk
_TREND_THRESHOLD = (
    0.2  # Minimum difference to classify a trend as improving or declining
)


def _classify_status(average: float) -> str:
    if average >= _AT_RISK_THRESHOLD:
        return "passing"
    if average >= _PASSING_THRESHOLD:
        return "at_risk"
    return "failing"


def _weighted_average(evaluations: list[dict]) -> float:
    graded = [e for e in evaluations if e.get("grade") is not None]
    if not graded:
        return 0.0
    weight_sum = sum(e["weight"] for e in graded)
    if weight_sum == 0:
        return 0.0
    return round(sum(e["grade"] * e["weight"] for e in graded) / weight_sum, 2)


def _compute_overall_gpa(subjects: list[dict]) -> float:
    if not subjects:
        return 0.0
    total_credits = sum(s.get("credits", 0) for s in subjects)
    if total_credits == 0:
        return 0.0
    weighted = sum(s["_avg"] * s.get("credits", 0) for s in subjects)
    return round(weighted / total_credits, 2)


def _compute_gpa_trend(subjects: list[dict]) -> str:
    """Compares the average of early vs recent graded evaluations across all subjects."""
    all_graded = [
        e
        for s in subjects
        for e in s.get("evaluations", [])
        if e.get("grade") is not None and e.get("date")
    ]
    all_graded.sort(key=lambda e: e["date"])

    if len(all_graded) < 4:
        return "stable"

    mid = len(all_graded) // 2
    early_avg = sum(e["grade"] for e in all_graded[:mid]) / mid
    recent_avg = sum(e["grade"] for e in all_graded[mid:]) / len(all_graded[mid:])

    diff = recent_avg - early_avg
    if diff > _TREND_THRESHOLD:
        return "improving"
    if diff < -_TREND_THRESHOLD:
        return "declining"
    return "stable"


class DashboardService(DashboardUseCase):
    def __init__(
        self,
        academic_client: AcademicClient,
        task_client: TaskClient,
        repo: StatsSnapshotPort | None = None,
    ):
        self._academic = academic_client
        self._tasks = task_client
        self._repo = repo

    async def get_dashboard(self, user_id: str, token: str) -> DashboardStats:
        try:
            subjects_data, tasks_data = await asyncio.gather(
                self._academic.get_subjects(user_id, token),
                self._tasks.get_tasks(user_id, token),
            )
        except ServiceUnavailableError:
            if self._repo:
                cached = await self._repo.get_latest_dashboard_snapshot(user_id)
                if cached:
                    return cached
            raise

        for subject in subjects_data:
            subject["_avg"] = _weighted_average(subject.get("evaluations", []))

        overall_gpa = _compute_overall_gpa(subjects_data)
        gpa_trend = _compute_gpa_trend(subjects_data)

        subject_summaries: list[SubjectSummary] = []
        passing = at_risk = failing = 0

        for s in subjects_data:
            status = _classify_status(s["_avg"])
            if status == "passing":
                passing += 1
            elif status == "at_risk":
                at_risk += 1
            else:
                failing += 1

            subject_summaries.append(
                SubjectSummary(
                    subject_id=s["id"],
                    name=s["name"],
                    code=s["code"],
                    credits=s.get("credits", 0),
                    current_average=s["_avg"],
                    status=status,
                )
            )

        active_tasks = [t for t in tasks_data if t.get("status") != "CANCELLED"]
        completed = sum(1 for t in active_tasks if t.get("status") == "COMPLETED")
        pending = sum(
            1 for t in active_tasks if t.get("status") in ("PENDING", "IN_PROGRESS")
        )
        overdue = sum(1 for t in active_tasks if t.get("status") == "OVERDUE")
        total_tasks = len(active_tasks)
        completion_rate = round(
            (completed / total_tasks * 100) if total_tasks > 0 else 0.0, 2
        )

        subject_summaries.sort(key=lambda s: s.current_average, reverse=True)

        stats = DashboardStats(
            user_id=user_id,
            overall_gpa=overall_gpa,
            gpa_trend=gpa_trend,
            total_subjects=len(subjects_data),
            passing_subjects=passing,
            at_risk_subjects=at_risk,
            failing_subjects=failing,
            subjects=subject_summaries,
            tasks=TaskSummary(
                total=total_tasks,
                completed=completed,
                pending=pending,
                overdue=overdue,
                completion_rate=completion_rate,
            ),
            generated_at=datetime.utcnow(),
        )

        if self._repo:
            await self._repo.save_dashboard_snapshot(stats)

        await self._publish_events(user_id, stats)

        return stats

    async def _publish_events(self, user_id: str, stats: DashboardStats) -> None:
        from app.config import settings as cfg
        from app.infrastructure.messaging.events import (
            AcademicOverloadAlertEvent,
            AcademicPerformanceAlertEvent,
        )
        from app.infrastructure.messaging.kafka_producer import publish_event

        if stats.at_risk_subjects > 0 or stats.failing_subjects > 0:
            subjects_at_risk = [
                {
                    "subject_id": s.subject_id,
                    "subject_name": s.name,
                    "status": s.status,
                    "current_average": s.current_average,
                }
                for s in stats.subjects
                if s.status in ("at_risk", "failing")
            ]
            await publish_event(
                cfg.kafka_topic_performance,
                AcademicPerformanceAlertEvent(
                    user_id=user_id,
                    overall_gpa=stats.overall_gpa,
                    failing_subjects=stats.failing_subjects,
                    at_risk_subjects=stats.at_risk_subjects,
                    subjects_at_risk=subjects_at_risk,
                ),
            )

        if stats.gpa_trend == "declining" and stats.tasks.overdue > 0:
            await publish_event(
                cfg.kafka_topic_overload,
                AcademicOverloadAlertEvent(
                    user_id=user_id,
                    overdue_tasks=stats.tasks.overdue,
                    gpa_trend=stats.gpa_trend,
                    failing_subjects=stats.failing_subjects,
                ),
            )
