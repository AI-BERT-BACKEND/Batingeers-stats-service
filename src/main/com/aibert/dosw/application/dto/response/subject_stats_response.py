from datetime import date
from pydantic import BaseModel, Field


class TaskDetailDto(BaseModel):
    task_id: str = Field(..., example="c3d4e5f6-a7b8-9012-cdef-123456789012")
    task_name: str = Field(..., example="Taller de integrales")
    status: str = Field(..., description="Pending | Completed | Overdue", example="Pending")
    due_date: date | None = Field(
        None, description="Due date (YYYY-MM-DD)", example="2026-06-15"
    )
    priority: str | None = Field(
        None, description="High | Medium | Low", example="High"
    )
    estimated_hours: float | None = Field(
        None, description="Estimated hours to complete the task", example=3.5
    )


class GradeEntryDto(BaseModel):
    period_id: str = Field(..., example="d4e5f6a7-b8c9-0123-defa-234567890123")
    period_name: str = Field(..., example="Primer Parcial")
    weight_percentage: float = Field(
        ...,
        description="Period weight as a percentage (all periods sum to 100)",
        example=30.0,
    )
    obtained_grade: float | None = Field(
        None,
        description="Grade obtained (0.0 – 5.0), null if not yet recorded",
        example=4.5,
    )
    contribution: float = Field(
        ...,
        description="Contribution to the final grade (obtained_grade × weight_percentage / 100)",
        example=1.35,
    )
    projected_grade: float = Field(
        ...,
        description="Projected final grade assuming 0 on all ungraded periods",
        example=3.8,
    )


class GradeEvolutionPointDto(BaseModel):
    week: int = Field(..., description="Academic week number within the semester", example=4)
    accumulated_grade: float = Field(
        ...,
        description="Cumulative weighted average up to this week (0.0 – 5.0)",
        example=3.8,
    )
    registered_date: date = Field(
        ...,
        description="Date when this evolution point was registered (YYYY-MM-DD)",
        example="2026-03-15",
    )


class SubjectStatsResponseDto(BaseModel):
    subject_id: str = Field(..., example="b2c3d4e5-f6a7-8901-bcde-f12345678901")
    subject_name: str = Field(..., example="Cálculo Diferencial")
    subject_code: str = Field(..., example="MAT-101")
    credits: int = Field(..., example=4)
    grades_by_period: list[GradeEntryDto]
    current_average: float = Field(
        ..., description="Current average (0.0 – 5.0)", example=3.8
    )
    max_possible_grade: float = Field(
        ...,
        description="Maximum achievable grade if the student gets 5.0 on all pending evaluations",
        example=4.6,
    )
    minimum_needed: float | None = Field(
        None,
        description="Minimum grade needed in pending evaluations to pass. Null if already passing or impossible",
        example=2.5,
    )
    trend: str = Field(..., description="improving | declining | stable", example="stable")
    tasks_total: int = Field(..., example=6)
    tasks_completed: int = Field(..., example=4)
    tasks_pending: int = Field(..., example=1)
    tasks_overdue: int = Field(..., example=1)
    task_completion_rate: float = Field(
        ..., description="Task completion rate (0.0 – 100.0)", example=66.7
    )
    status: str = Field(..., description="passing | at_risk | failing", example="passing")
    projected_grade: float = Field(
        ...,
        description="Projected final grade assuming 0 on all ungraded evaluations",
        example=3.8,
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
