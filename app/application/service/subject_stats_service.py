import asyncio
from datetime import date

from app.domain.exceptions.stats_exceptions import SubjectNotFoundError
from app.domain.model.subject_stats import GradeEntry, SubjectStats
from app.domain.ports.in_.subject_stats_use_case import SubjectStatsUseCase
from app.infrastructure.external.academic_client import AcademicClient
from app.infrastructure.external.task_client import TaskClient

_PASSING_GRADE = 3.0
_AT_RISK_THRESHOLD = 3.5
_MAX_GRADE = 5.0
_TREND_THRESHOLD = 0.3


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except (ValueError, TypeError):
        return None


def _build_grade_history(evaluations: list[dict]) -> list[GradeEntry]:
    entries = []
    for e in evaluations:
        grade = e.get("grade")
        contribution = round(grade * e["weight"], 4) if grade is not None else 0.0
        entries.append(GradeEntry(
            evaluation_id=e["id"],
            evaluation_name=e["name"],
            weight=e["weight"],
            grade=grade,
            date=_parse_date(e.get("date")),
            contribution=contribution,
        ))
    return sorted(entries, key=lambda x: (x.date or date.min))


def _current_average(evaluations: list[dict]) -> float:
    graded = [e for e in evaluations if e.get("grade") is not None]
    if not graded:
        return 0.0
    weight_sum = sum(e["weight"] for e in graded)
    if weight_sum == 0:
        return 0.0
    return round(sum(e["grade"] * e["weight"] for e in graded) / weight_sum, 2)


def _max_possible_grade(evaluations: list[dict]) -> float:
    """Nota máxima alcanzable si el estudiante saca 5.0 en todas las evaluaciones pendientes."""
    graded = [e for e in evaluations if e.get("grade") is not None]
    pending = [e for e in evaluations if e.get("grade") is None]

    if not pending:
        return _current_average(evaluations)

    total_weight = sum(e["weight"] for e in evaluations)
    if total_weight == 0:
        return 0.0

    earned = sum(e["grade"] * e["weight"] for e in graded)
    max_remaining = _MAX_GRADE * sum(e["weight"] for e in pending)
    return round((earned + max_remaining) / total_weight, 2)


def _minimum_needed(evaluations: list[dict]) -> float | None:
    """Nota mínima requerida en evaluaciones pendientes para aprobar con _PASSING_GRADE."""
    graded = [e for e in evaluations if e.get("grade") is not None]
    pending = [e for e in evaluations if e.get("grade") is None]

    if not pending:
        return None

    total_weight = sum(e["weight"] for e in evaluations)
    pending_weight = sum(e["weight"] for e in pending)
    earned = sum(e["grade"] * e["weight"] for e in graded)

    if pending_weight == 0:
        return None

    # Despejando: _PASSING_GRADE = (earned + min_needed * pending_weight) / total_weight
    min_needed = (_PASSING_GRADE * total_weight - earned) / pending_weight

    if min_needed <= 0:
        return 0.0
    if min_needed > _MAX_GRADE:
        return None  # Imposible pasar
    return round(min_needed, 2)


def _compute_trend(evaluations: list[dict]) -> str:
    graded = sorted(
        [e for e in evaluations if e.get("grade") is not None and e.get("date")],
        key=lambda e: e["date"],
    )
    if len(graded) < 3:
        return "stable"

    mid = len(graded) // 2
    early_avg = sum(e["grade"] for e in graded[:mid]) / mid
    recent_avg = sum(e["grade"] for e in graded[mid:]) / len(graded[mid:])

    diff = recent_avg - early_avg
    if diff > _TREND_THRESHOLD:
        return "improving"
    if diff < -_TREND_THRESHOLD:
        return "declining"
    return "stable"


def _classify_status(average: float) -> str:
    if average >= _AT_RISK_THRESHOLD:
        return "passing"
    if average >= _PASSING_GRADE:
        return "at_risk"
    return "failing"


def _build_subject_stats(subject: dict, subject_tasks: list[dict]) -> SubjectStats:
    evaluations = subject.get("evaluations", [])
    avg = _current_average(evaluations)

    active = [t for t in subject_tasks if t.get("status") != "CANCELLED"]
    completed = sum(1 for t in active if t.get("status") == "COMPLETED")
    pending = sum(1 for t in active if t.get("status") in ("PENDING", "IN_PROGRESS"))
    overdue = sum(1 for t in active if t.get("status") == "OVERDUE")
    total = len(active)
    rate = round((completed / total * 100) if total > 0 else 0.0, 2)

    return SubjectStats(
        subject_id=subject["id"],
        subject_name=subject["name"],
        subject_code=subject["code"],
        credits=subject.get("credits", 0),
        grade_history=_build_grade_history(evaluations),
        current_average=avg,
        max_possible_grade=_max_possible_grade(evaluations),
        minimum_needed=_minimum_needed(evaluations),
        trend=_compute_trend(evaluations),
        tasks_total=total,
        tasks_completed=completed,
        tasks_pending=pending,
        tasks_overdue=overdue,
        task_completion_rate=rate,
        status=_classify_status(avg),
    )


class SubjectStatsService(SubjectStatsUseCase):
    def __init__(self, academic_client: AcademicClient, task_client: TaskClient):
        self._academic = academic_client
        self._tasks = task_client

    async def get_all_subjects_stats(self, user_id: str, token: str) -> list[SubjectStats]:
        subjects_data, tasks_data = await asyncio.gather(
            self._academic.get_subjects(user_id, token),
            self._tasks.get_tasks(user_id, token),
        )
        return [
            _build_subject_stats(
                subject,
                [t for t in tasks_data if t.get("subject_id") == subject["id"]],
            )
            for subject in subjects_data
        ]

    async def get_subject_stats(
        self, user_id: str, subject_id: str, token: str
    ) -> SubjectStats:
        subject_data, tasks_data = await asyncio.gather(
            self._academic.get_subject(user_id, subject_id, token),
            self._tasks.get_tasks_by_subject(user_id, subject_id, token),
        )
        if subject_data is None:
            raise SubjectNotFoundError(subject_id)
        return _build_subject_stats(subject_data, tasks_data)
