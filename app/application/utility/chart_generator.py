from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from app.domain.model.subject_stats import GradeEntry


@dataclass
class ChartPoint:
    week_label: str
    average: float
    evaluations_count: int


def generate_weekly_evolution(grade_history: list[GradeEntry]) -> list[ChartPoint]:
    """
    Genera puntos de evolución semanal a partir del historial de notas.

    Agrupa las evaluaciones calificadas por semana ISO y calcula el promedio
    ponderado acumulado hasta cada semana, reflejando cómo ha evolucionado
    el rendimiento del estudiante a lo largo del semestre.
    """
    graded = [e for e in grade_history if e.grade is not None and e.date is not None]
    if not graded:
        return []

    weeks: dict[str, list[GradeEntry]] = defaultdict(list)
    for entry in sorted(graded, key=lambda e: e.date):
        iso = entry.date.isocalendar()
        week_key = f"{iso.year}-W{iso.week:02d}"
        weeks[week_key].append(entry)

    points: list[ChartPoint] = []
    cumulative: list[GradeEntry] = []

    for week_key in sorted(weeks.keys()):
        cumulative.extend(weeks[week_key])
        weight_sum = sum(e.weight for e in cumulative)
        avg = (
            sum(e.grade * e.weight for e in cumulative) / weight_sum
            if weight_sum > 0
            else 0.0
        )
        points.append(
            ChartPoint(
                week_label=week_key,
                average=round(avg, 2),
                evaluations_count=len(cumulative),
            )
        )

    return points
