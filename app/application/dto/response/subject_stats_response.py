from datetime import date
from pydantic import BaseModel, Field


class TaskDetailDto(BaseModel):
    task_id: str
    task_name: str
    status: str = Field(..., description="Pendiente | Completada | Vencida")
    due_date: date | None = Field(None, description="Due date (YYYY-MM-DD)")
    priority: str | None = Field(None, description="Alta | Media | Baja")
    estimated_hours: float | None = Field(
        None, description="Estimated hours to complete the task"
    )


class GradeEntryDto(BaseModel):
    period_id: str
    period_name: str
    weight_percentage: float = Field(
        ..., description="Period weight as a percentage (all periods sum to 100)"
    )
    obtained_grade: float | None = Field(
        None, description="Grade obtained (0.0 – 5.0), null if not yet recorded"
    )
    contribution: float = Field(
        ...,
        description="Contribution to the final grade (obtained_grade × weight_percentage / 100)",
    )
    projected_grade: float = Field(
        ..., description="Projected final grade assuming 0 on all ungraded periods"
    )


class GradeEvolutionPointDto(BaseModel):
    week: int = Field(..., description="Academic week number within the semester")
    accumulated_grade: float = Field(
        ..., description="Cumulative weighted average up to this week (0.0 – 5.0)"
    )
    registered_date: date = Field(
        ..., description="Date when this evolution point was registered (YYYY-MM-DD)"
    )


class SubjectStatsResponseDto(BaseModel):
    subject_id: str
    subject_name: str
    subject_code: str
    credits: int
    grades_by_period: list[GradeEntryDto]
    current_average: float = Field(..., description="Current average (0.0 – 5.0)")
    max_possible_grade: float = Field(
        ...,
        description="Maximum achievable grade if the student gets 5.0 on all pending evaluations",
    )
    minimum_needed: float | None = Field(
        None,
        description="Minimum grade needed in pending evaluations to pass. Null if already passing or impossible",
    )
    trend: str = Field(..., description="improving | declining | stable")
    tasks_total: int
    tasks_completed: int
    tasks_pending: int
    tasks_overdue: int
    task_completion_rate: float = Field(
        ..., description="Task completion rate (0.0 – 100.0)"
    )
    status: str = Field(..., description="passing | at_risk | failing")
    projected_grade: float = Field(
        ..., description="Projected final grade assuming 0 on all ungraded evaluations"
    )
    related_tasks: list[TaskDetailDto] = Field(
        default_factory=list,
        description="Tasks for this subject sorted by due date descending",
    )
    grade_evolution: list[GradeEvolutionPointDto] = Field(
        default_factory=list,
        description="Weekly accumulated grade evolution. Populated only when at least 2 periods have a grade (RN-02)",
    )

    model_config = {"from_attributes": True}
