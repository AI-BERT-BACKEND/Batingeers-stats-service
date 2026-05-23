from datetime import datetime
from pydantic import BaseModel, Field


class SubjectSummaryDto(BaseModel):
    subject_id: str = Field(..., example="b2c3d4e5-f6a7-8901-bcde-f12345678901")
    name: str = Field(..., example="Cálculo Diferencial")
    code: str = Field(..., example="MAT-101")
    credits: int = Field(..., example=4)
    current_average: float = Field(
        ..., description="Current average on a 0.0 – 5.0 scale", example=4.2
    )
    status: str = Field(..., description="Passing | At Risk | Failing", example="Passing")
    teacher_name: str | None = Field(
        None,
        description="Teacher name if registered in academic-service",
        example="Dr. García",
    )


class TaskSummaryDto(BaseModel):
    total: int = Field(..., example=12)
    completed: int = Field(..., example=8)
    pending: int = Field(..., example=3)
    overdue: int = Field(..., example=1)
    completion_rate: float = Field(
        ..., description="Completion rate as a percentage (0.0 – 100.0)", example=66.7
    )


class DashboardResponseDto(BaseModel):
    user_id: str = Field(..., example="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    overall_gpa: int = Field(
        ...,
        description="Weighted academic GPA rounded to integer (0 – 5)",
        example=4,
    )
    gpa_trend: str = Field(
        ..., description="improving | declining | stable", example="stable"
    )
    total_subjects: int = Field(..., example=5)
    passing_subjects: int = Field(..., example=3)
    at_risk_subjects: int = Field(..., example=1)
    failing_subjects: int = Field(..., example=1)
    subjects: list[SubjectSummaryDto]
    tasks: TaskSummaryDto
    generated_at: datetime = Field(..., example="2026-05-22T16:52:39.763Z")

    model_config = {"from_attributes": True}
