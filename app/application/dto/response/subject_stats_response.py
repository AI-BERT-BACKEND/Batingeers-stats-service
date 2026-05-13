from datetime import date as Date
from pydantic import BaseModel, Field


class TaskDetailDto(BaseModel):
    task_id: str
    title: str
    status: str = Field(..., description="PENDING | IN_PROGRESS | COMPLETED | OVERDUE")
    due_date: str | None = Field(None, description="Due date in ISO format")
    subject_id: str | None = None


class GradeEntryDto(BaseModel):
    evaluation_id: str
    evaluation_name: str
    weight: float = Field(..., description="Evaluation weight (0.0 – 1.0)")
    grade: float | None = Field(None, description="Grade obtained (0.0 – 5.0), null if not yet recorded")
    date: date | None = None
    contribution: float = Field(..., description="Contribution to the final average (grade × weight)")


class ChartPointDto(BaseModel):
    week_label: str = Field(..., description="Week in ISO format: YYYY-WNN")
    average: float = Field(..., description="Cumulative weighted average up to this week (0.0 – 5.0)")
    evaluations_count: int = Field(..., description="Cumulative number of graded evaluations")


class SubjectStatsResponseDto(BaseModel):
    subject_id: str
    subject_name: str
    subject_code: str
    credits: int
    grade_history: list[GradeEntryDto]
    current_average: float = Field(..., description="Current average (0.0 – 5.0)")
    max_possible_grade: float = Field(
        ..., description="Maximum achievable grade if the student gets 5.0 on all pending evaluations"
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
    task_completion_rate: float = Field(..., description="Task completion rate (0.0 – 100.0)")
    status: str = Field(..., description="passing | at_risk | failing")
    projected_grade: float = Field(
        ..., description="Projected final grade assuming 0 on all ungraded evaluations"
    )
    related_tasks: list[TaskDetailDto] = Field(
        default_factory=list,
        description="Tasks for this subject sorted by due date descending",
    )
    chart_data: list[ChartPointDto] = Field(
        default_factory=list,
        description="Weekly average evolution points for performance charts",
    )

    model_config = {"from_attributes": True}
