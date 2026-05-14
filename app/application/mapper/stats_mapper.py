from app.application.dto.response.dashboard_response import (
    DashboardResponseDto,
    SubjectSummaryDto,
    TaskSummaryDto,
)
from app.application.dto.response.subject_stats_response import (
    ChartPointDto,
    GradeEntryDto,
    SubjectStatsResponseDto,
    TaskDetailDto,
)
from app.application.utility.chart_generator import ChartPoint
from app.domain.model.dashboard import DashboardStats, SubjectSummary, TaskSummary
from app.domain.model.subject_stats import GradeEntry, SubjectStats


def _subject_summary_to_dto(summary: SubjectSummary) -> SubjectSummaryDto:
    return SubjectSummaryDto(
        subject_id=summary.subject_id,
        name=summary.name,
        code=summary.code,
        credits=summary.credits,
        current_average=summary.current_average,
        status=summary.status,
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
        overall_gpa=stats.overall_gpa,
        gpa_trend=stats.gpa_trend,
        total_subjects=stats.total_subjects,
        passing_subjects=stats.passing_subjects,
        at_risk_subjects=stats.at_risk_subjects,
        failing_subjects=stats.failing_subjects,
        subjects=[_subject_summary_to_dto(s) for s in stats.subjects],
        tasks=_task_summary_to_dto(stats.tasks),
        generated_at=stats.generated_at,
    )


def _grade_entry_to_dto(entry: GradeEntry) -> GradeEntryDto:
    return GradeEntryDto(
        evaluation_id=entry.evaluation_id,
        evaluation_name=entry.evaluation_name,
        weight=entry.weight,
        grade=entry.grade,
        evaluation_date=entry.date,
        contribution=entry.contribution,
    )


def _task_detail_to_dto(task: dict) -> TaskDetailDto:
    return TaskDetailDto(
        task_id=task.get("id") or task.get("taskId", ""),
        title=task.get("title", ""),
        status=task.get("status", ""),
        due_date=task.get("dueDate") or task.get("due_date"),
        subject_id=task.get("subjectId") or task.get("subject_id"),
    )


def _chart_point_to_dto(cp: ChartPoint) -> ChartPointDto:
    return ChartPointDto(
        week_label=cp.week_label,
        average=cp.average,
        evaluations_count=cp.evaluations_count,
    )


def subject_stats_to_dto(stats: SubjectStats) -> SubjectStatsResponseDto:
    return SubjectStatsResponseDto(
        subject_id=stats.subject_id,
        subject_name=stats.subject_name,
        subject_code=stats.subject_code,
        credits=stats.credits,
        grade_history=[_grade_entry_to_dto(g) for g in stats.grade_history],
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
        chart_data=[_chart_point_to_dto(cp) for cp in stats.chart_data],
    )
