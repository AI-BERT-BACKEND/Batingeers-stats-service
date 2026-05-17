from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from app.domain.model.subject_stats import GradeEntry


@dataclass
class ChartPoint:
    week: int
    accumulated_grade: float
    registered_date: date


def generate_weekly_evolution(grade_history: list[GradeEntry]) -> list[ChartPoint]:
    """
    Generates weekly evolution points from the grade history.

    Groups graded evaluations by ISO week and calculates the cumulative weighted
    average up to each week, reflecting how performance has evolved over the semester.
    Returns an empty list if fewer than 2 entries have both a grade and a date.
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
        week_entries = weeks[week_key]
        cumulative.extend(week_entries)
        weight_sum = sum(e.weight for e in cumulative)
        avg = (
            sum(e.grade * e.weight for e in cumulative) / weight_sum
            if weight_sum > 0
            else 0.0
        )
        iso_parts = week_key.split("-W")
        week_number = int(iso_parts[1])
        last_date = max(e.date for e in week_entries)
        points.append(
            ChartPoint(
                week=week_number,
                accumulated_grade=round(avg, 2),
                registered_date=last_date,
            )
        )

    return points
