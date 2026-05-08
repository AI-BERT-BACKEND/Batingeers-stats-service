from datetime import datetime
from pydantic import BaseModel, Field


class SubjectSummaryDto(BaseModel):
    subject_id: str
    name: str
    code: str
    credits: int
    current_average: float = Field(..., description="Promedio actual en escala 0.0 – 5.0")
    status: str = Field(..., description="passing | at_risk | failing")


class TaskSummaryDto(BaseModel):
    total: int
    completed: int
    pending: int
    overdue: int
    completion_rate: float = Field(..., description="Tasa de completitud en porcentaje (0.0 – 100.0)")


class DashboardResponseDto(BaseModel):
    user_id: str
    overall_gpa: float = Field(..., description="Promedio académico ponderado (0.0 – 5.0)")
    gpa_trend: str = Field(..., description="improving | declining | stable")
    total_subjects: int
    passing_subjects: int
    at_risk_subjects: int
    failing_subjects: int
    subjects: list[SubjectSummaryDto]
    tasks: TaskSummaryDto
    generated_at: datetime

    model_config = {"from_attributes": True}
