from datetime import date

from app.application.utility.chart_generator import ChartPoint
from app.domain.model.dashboard import DashboardStats, SubjectSummary, TaskSummary
from app.domain.model.subject_stats import GradeEntry, SubjectStats
from app.infrastructure.adapters.persistence.entity.stats_snapshot_entity import (
    DashboardSnapshotEntity,
    SubjectSnapshotEntity,
)


# ── DashboardStats ↔ DashboardSnapshotEntity ──────────────────────────────────


def dashboard_to_entity(stats: DashboardStats) -> DashboardSnapshotEntity:
    return DashboardSnapshotEntity(
        user_id=stats.user_id,
        overall_gpa=stats.overall_gpa,
        gpa_trend=stats.gpa_trend,
        total_subjects=stats.total_subjects,
        passing_subjects=stats.passing_subjects,
        at_risk_subjects=stats.at_risk_subjects,
        failing_subjects=stats.failing_subjects,
        subjects_data=[
            {
                "subject_id": s.subject_id,
                "name": s.name,
                "code": s.code,
                "credits": s.credits,
                "current_average": s.current_average,
                "status": s.status,
            }
            for s in stats.subjects
        ],
        tasks_data={
            "total": stats.tasks.total,
            "completed": stats.tasks.completed,
            "pending": stats.tasks.pending,
            "overdue": stats.tasks.overdue,
            "completion_rate": stats.tasks.completion_rate,
        },
        generated_at=stats.generated_at,
    )


def entity_to_dashboard(entity: DashboardSnapshotEntity) -> DashboardStats:
    return DashboardStats(
        user_id=entity.user_id,
        overall_gpa=entity.overall_gpa,
        gpa_trend=entity.gpa_trend,
        total_subjects=entity.total_subjects,
        passing_subjects=entity.passing_subjects,
        at_risk_subjects=entity.at_risk_subjects,
        failing_subjects=entity.failing_subjects,
        subjects=[
            SubjectSummary(
                subject_id=s["subject_id"],
                name=s["name"],
                code=s["code"],
                credits=s["credits"],
                current_average=s["current_average"],
                status=s["status"],
            )
            for s in (entity.subjects_data or [])
        ],
        tasks=TaskSummary(
            total=entity.tasks_data.get("total", 0),
            completed=entity.tasks_data.get("completed", 0),
            pending=entity.tasks_data.get("pending", 0),
            overdue=entity.tasks_data.get("overdue", 0),
            completion_rate=entity.tasks_data.get("completion_rate", 0.0),
        ),
        generated_at=entity.generated_at,
    )


# ── SubjectStats ↔ SubjectSnapshotEntity ──────────────────────────────────────


def _grade_entry_to_dict(g: GradeEntry) -> dict:
    return {
        "evaluation_id": g.evaluation_id,
        "evaluation_name": g.evaluation_name,
        "weight": g.weight,
        "grade": g.grade,
        "date": g.date.isoformat() if g.date else None,
        "contribution": g.contribution,
    }


def _dict_to_grade_entry(d: dict) -> GradeEntry:
    raw_date = d.get("date")
    return GradeEntry(
        evaluation_id=d["evaluation_id"],
        evaluation_name=d["evaluation_name"],
        weight=d["weight"],
        grade=d.get("grade"),
        date=date.fromisoformat(raw_date) if raw_date else None,
        contribution=d.get("contribution", 0.0),
    )


def _chart_point_to_dict(cp: ChartPoint) -> dict:
    return {
        "week_label": cp.week_label,
        "average": cp.average,
        "evaluations_count": cp.evaluations_count,
    }


def _dict_to_chart_point(d: dict) -> ChartPoint:
    return ChartPoint(
        week_label=d["week_label"],
        average=d["average"],
        evaluations_count=d["evaluations_count"],
    )


def subject_to_entity(user_id: str, stats: SubjectStats) -> SubjectSnapshotEntity:
    return SubjectSnapshotEntity(
        user_id=user_id,
        subject_id=stats.subject_id,
        subject_name=stats.subject_name,
        subject_code=stats.subject_code,
        credits=stats.credits,
        current_average=stats.current_average,
        max_possible_grade=stats.max_possible_grade,
        minimum_needed=stats.minimum_needed,
        trend=stats.trend,
        tasks_total=stats.tasks_total,
        tasks_completed=stats.tasks_completed,
        tasks_pending=stats.tasks_pending,
        tasks_overdue=stats.tasks_overdue,
        task_completion_rate=stats.task_completion_rate,
        status=stats.status,
        grade_history_data=[_grade_entry_to_dict(g) for g in stats.grade_history],
        chart_data=[_chart_point_to_dict(cp) for cp in stats.chart_data],
        generated_at=stats.generated_at,
    )


def entity_to_subject(entity: SubjectSnapshotEntity) -> SubjectStats:
    return SubjectStats(
        subject_id=entity.subject_id,
        subject_name=entity.subject_name,
        subject_code=entity.subject_code,
        credits=entity.credits,
        current_average=entity.current_average,
        max_possible_grade=entity.max_possible_grade,
        minimum_needed=entity.minimum_needed,
        trend=entity.trend,
        tasks_total=entity.tasks_total,
        tasks_completed=entity.tasks_completed,
        tasks_pending=entity.tasks_pending,
        tasks_overdue=entity.tasks_overdue,
        task_completion_rate=entity.task_completion_rate,
        status=entity.status,
        grade_history=[
            _dict_to_grade_entry(d) for d in (entity.grade_history_data or [])
        ],
        chart_data=[_dict_to_chart_point(d) for d in (entity.chart_data or [])],
        generated_at=entity.generated_at,
    )
