from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class GradeEntry:
    evaluation_id: str
    evaluation_name: str
    weight: float
    grade: float | None
    date: date | None
    contribution: float  # grade * weight sobre el total de peso evaluado


@dataclass
class SubjectStats:
    subject_id: str
    subject_name: str
    subject_code: str
    credits: int
    grade_history: list[GradeEntry]
    current_average: float
    max_possible_grade: float
    minimum_needed: (
        float | None
    )  # Nota mínima requerida en evaluaciones pendientes para pasar
    trend: str  # "improving" | "declining" | "stable"
    tasks_total: int
    tasks_completed: int
    tasks_pending: int
    tasks_overdue: int
    task_completion_rate: float
    status: str  # "passing" | "at_risk" | "failing"
    chart_data: list = field(
        default_factory=list
    )  # list[ChartPoint] — importación circular evitada
    generated_at: datetime = field(default_factory=datetime.utcnow)
