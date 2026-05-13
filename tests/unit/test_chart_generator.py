import pytest
from datetime import date

from app.application.utility.chart_generator import generate_weekly_evolution
from app.domain.model.subject_stats import GradeEntry


def _entry(
    eval_id: str, weight: float, grade: float | None, iso_date: str | None
) -> GradeEntry:
    return GradeEntry(
        evaluation_id=eval_id,
        evaluation_name=eval_id,
        weight=weight,
        grade=grade,
        date=date.fromisoformat(iso_date) if iso_date else None,
        contribution=round(grade * weight, 4) if grade is not None else 0.0,
    )


_HISTORY = [
    _entry("e1", 0.3, 4.5, "2026-03-15"),  # Semana 2026-W11
    _entry("e2", 0.3, 3.0, "2026-04-15"),  # Semana 2026-W16
    _entry("e3", 0.4, None, None),  # Sin fecha — no debe aparecer en chart
]


def test_empty_history_returns_empty_list():
    result = generate_weekly_evolution([])
    assert result == []


def test_no_graded_entries_returns_empty_list():
    history = [_entry("e1", 1.0, None, None)]
    result = generate_weekly_evolution(history)
    assert result == []


def test_single_graded_entry_returns_one_point():
    history = [_entry("e1", 1.0, 4.0, "2026-03-15")]
    result = generate_weekly_evolution(history)
    assert len(result) == 1
    assert result[0].average == 4.0
    assert result[0].evaluations_count == 1


def test_two_entries_same_week_produce_one_point():
    history = [
        _entry("e1", 0.5, 4.0, "2026-03-16"),
        _entry("e2", 0.5, 2.0, "2026-03-17"),  # misma semana
    ]
    result = generate_weekly_evolution(history)
    assert len(result) == 1
    assert result[0].evaluations_count == 2
    assert result[0].average == pytest.approx(3.0, rel=0.01)


def test_two_different_weeks_produce_two_points():
    result = generate_weekly_evolution(_HISTORY)
    # Solo e1 y e2 tienen fecha y nota
    assert len(result) == 2


def test_points_are_sorted_by_week_ascending():
    result = generate_weekly_evolution(_HISTORY)
    assert result[0].week_label < result[1].week_label


def test_running_average_is_cumulative():
    result = generate_weekly_evolution(_HISTORY)
    # Primera semana: 4.5 (solo e1, peso 0.3 sobre 0.3 evaluado)
    assert result[0].average == pytest.approx(4.5, rel=0.01)
    # Segunda semana: (4.5*0.3 + 3.0*0.3) / (0.3+0.3) = 3.75
    assert result[1].average == pytest.approx(3.75, rel=0.01)


def test_evaluations_count_increases_cumulatively():
    result = generate_weekly_evolution(_HISTORY)
    assert result[0].evaluations_count == 1
    assert result[1].evaluations_count == 2


def test_week_label_format_is_iso():
    history = [_entry("e1", 1.0, 3.5, "2026-03-15")]
    result = generate_weekly_evolution(history)
    label = result[0].week_label
    # Debe ser "YYYY-WNN"
    assert label.startswith("2026-W")
    week_num = int(label.split("W")[1])
    assert 1 <= week_num <= 53


def test_entry_without_date_is_ignored():
    history = [
        _entry("e1", 0.5, 4.0, "2026-03-15"),
        _entry("e2", 0.5, 2.0, None),  # sin fecha — ignorado
    ]
    result = generate_weekly_evolution(history)
    assert len(result) == 1
    assert result[0].evaluations_count == 1
