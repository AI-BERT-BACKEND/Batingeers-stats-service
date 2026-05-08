from datetime import date
from pydantic import BaseModel, Field


class GradeEntryDto(BaseModel):
    evaluation_id: str
    evaluation_name: str
    weight: float = Field(..., description="Peso de la evaluación (0.0 – 1.0)")
    grade: float | None = Field(None, description="Nota obtenida (0.0 – 5.0), null si aún no se registró")
    date: date | None = None
    contribution: float = Field(..., description="Aporte al promedio final (grade × weight)")


class ChartPointDto(BaseModel):
    week_label: str = Field(..., description="Semana en formato ISO: YYYY-WNN")
    average: float = Field(..., description="Promedio ponderado acumulado hasta esta semana (0.0 – 5.0)")
    evaluations_count: int = Field(..., description="Número acumulado de evaluaciones calificadas")


class SubjectStatsResponseDto(BaseModel):
    subject_id: str
    subject_name: str
    subject_code: str
    credits: int
    grade_history: list[GradeEntryDto]
    current_average: float = Field(..., description="Promedio actual (0.0 – 5.0)")
    max_possible_grade: float = Field(
        ..., description="Nota máxima alcanzable si el estudiante saca 5.0 en todo lo pendiente"
    )
    minimum_needed: float | None = Field(
        None,
        description="Nota mínima necesaria en evaluaciones pendientes para pasar. Null si ya pasó o es imposible",
    )
    trend: str = Field(..., description="improving | declining | stable")
    tasks_total: int
    tasks_completed: int
    tasks_pending: int
    tasks_overdue: int
    task_completion_rate: float = Field(..., description="Tasa de completitud de tareas (0.0 – 100.0)")
    status: str = Field(..., description="passing | at_risk | failing")
    chart_data: list[ChartPointDto] = Field(
        default_factory=list,
        description="Puntos de evolución semanal del promedio para gráficas de rendimiento",
    )

    model_config = {"from_attributes": True}
