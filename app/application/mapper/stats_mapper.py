from datetime import date

from app.application.dto.response.dashboard_response import (
    DashboardResponseDto,
    SubjectSummaryDto,
    TaskSummaryDto,
)
from app.application.dto.response.subject_stats_response import (
    GradeEntryDto,
    GradeEvolutionPointDto,
    SubjectStatsResponseDto,
    TaskDetailDto,
)
from app.application.utility.chart_generator import ChartPoint
from app.domain.model.dashboard import DashboardStats, SubjectSummary, TaskSummary
from app.domain.model.subject_stats import GradeEntry, SubjectStats

_SUBJECT_STATUS_MAP: dict[str, str] = {
    "passing": "Passing",
    "at_risk": "At Risk",
    "failing": "Failing",
}

_TASK_STATUS_MAP: dict[str, str] = {
    "COMPLETED": "Completed",
    "PENDING": "Pending",
    "IN_PROGRESS": "In Progress",
    "OVERDUE": "Overdue",
}


def _subject_summary_to_dto(summary: SubjectSummary) -> SubjectSummaryDto:
    return SubjectSummaryDto(
        subject_id=summary.subject_id,
        name=summary.name,
        code=summary.code,
        credits=summary.credits,
        current_average=summary.current_average,
        status=_SUBJECT_STATUS_MAP.get(summary.status, summary.status),
        teacher_name=summary.teacher_name,
    )


def _task_summary_to_dto(task: TaskSummary) -> TaskSummaryDto:
    return TaskSummaryDto(
        total=task.total,
        completed=task.completed,
        pending=task.pending,
        overdue=task.overdue,
        completion_rate=task.completion_rate,
    )


def dashboard_to_dto(stats: DashboardStats) -> DashboardResponseDto:
    return DashboardResponseDto(
        user_id=stats.user_id,
        overall_gpa=int(round(stats.overall_gpa)),
        gpa_trend=stats.gpa_trend,
        total_subjects=stats.total_subjects,
        passing_subjects=stats.passing_subjects,
        at_risk_subjects=stats.at_risk_subjects,
        failing_subjects=stats.failing_subjects,
        subjects=[_subject_summary_to_dto(s) for s in stats.subjects],
        tasks=_task_summary_to_dto(stats.tasks),
        generated_at=stats.generated_at,
    )


def _grade_entry_to_dto(entry: GradeEntry, projected_grade: float) -> GradeEntryDto:
    return GradeEntryDto(
        period_id=entry.evaluation_id,
        period_name=entry.evaluation_name,
        weight_percentage=round(entry.weight * 100, 2),
        obtained_grade=entry.grade,
        contribution=entry.contribution,
        projected_grade=projected_grade,
    )


def _parse_due_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except (ValueError, TypeError):
        return None


def _task_detail_to_dto(task: dict) -> TaskDetailDto:
    raw_due = task.get("dueDate") or task.get("due_date")
    raw_status = task.get("status", "")
    return TaskDetailDto(
        task_id=task.get("id") or task.get("taskId", ""),
        task_name=task.get("title") or task.get("name") or task.get("taskName", ""),
        status=_TASK_STATUS_MAP.get(raw_status, raw_status),
        due_date=_parse_due_date(raw_due),
        priority=task.get("priority"),
        estimated_hours=task.get("estimatedHours") or task.get("estimated_hours"),
    )


def _chart_point_to_dto(cp: ChartPoint) -> GradeEvolutionPointDto:
    return GradeEvolutionPointDto(
        week=cp.week,
        accumulated_grade=cp.accumulated_grade,
        registered_date=cp.registered_date,
    )


def subject_stats_to_dto(stats: SubjectStats) -> SubjectStatsResponseDto:
    return SubjectStatsResponseDto(
        subject_id=stats.subject_id,
        subject_name=stats.subject_name,
        subject_code=stats.subject_code,
        credits=stats.credits,
        grades_by_period=[
            _grade_entry_to_dto(g, stats.projected_grade) for g in stats.grade_history
        ],
        current_average=stats.current_average,
        max_possible_grade=stats.max_possible_grade,
        minimum_needed=stats.minimum_needed,
        projected_grade=stats.projected_grade,
        trend=stats.trend,
        tasks_total=stats.tasks_total,
        tasks_completed=stats.tasks_completed,
        tasks_pending=stats.tasks_pending,
        tasks_overdue=stats.tasks_overdue,
        task_completion_rate=stats.task_completion_rate,
        status=stats.status,
        related_tasks=[_task_detail_to_dto(t) for t in stats.related_tasks],
        grade_evolution=[_chart_point_to_dto(cp) for cp in stats.chart_data],
    )
