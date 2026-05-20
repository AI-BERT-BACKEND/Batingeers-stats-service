import pytest
from datetime import date

from com.aibert.dosw.application.utility.chart_generator import (
    generate_weekly_evolution,
)
from com.aibert.dosw.domain.model.subject_stats import GradeEntry


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
    _entry("e1", 0.3, 4.5, "2026-03-15"),  # Week 2026-W11
    _entry("e2", 0.3, 3.0, "2026-04-15"),  # Week 2026-W16
    _entry("e3", 0.4, None, None),  # No date — must not appear in chart
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
    assert result[0].accumulated_grade == 4.0


def test_single_entry_week_is_integer():
    history = [_entry("e1", 1.0, 4.0, "2026-03-15")]
    result = generate_weekly_evolution(history)
    assert isinstance(result[0].week, int)
    assert result[0].week == 11


def test_single_entry_registered_date():
    history = [_entry("e1", 1.0, 4.0, "2026-03-15")]
    result = generate_weekly_evolution(history)
    assert result[0].registered_date == date(2026, 3, 15)


def test_two_entries_same_week_produce_one_point():
    history = [
        _entry("e1", 0.5, 4.0, "2026-03-16"),
        _entry("e2", 0.5, 2.0, "2026-03-17"),  # same week
    ]
    result = generate_weekly_evolution(history)
    assert len(result) == 1
    assert result[0].accumulated_grade == pytest.approx(3.0, rel=0.01)


def test_two_entries_same_week_registered_date_is_last():
    history = [
        _entry("e1", 0.5, 4.0, "2026-03-16"),
        _entry("e2", 0.5, 2.0, "2026-03-17"),
    ]
    result = generate_weekly_evolution(history)
    assert result[0].registered_date == date(2026, 3, 17)


def test_two_different_weeks_produce_two_points():
    result = generate_weekly_evolution(_HISTORY)
    assert len(result) == 2


def test_points_are_sorted_by_week_ascending():
    result = generate_weekly_evolution(_HISTORY)
    assert result[0].week < result[1].week


def test_running_average_is_cumulative():
    result = generate_weekly_evolution(_HISTORY)
    # Week 1: 4.5 (only e1, weight 0.3 over 0.3 graded)
    assert result[0].accumulated_grade == pytest.approx(4.5, rel=0.01)
    # Week 2: (4.5*0.3 + 3.0*0.3) / (0.3+0.3) = 3.75
    assert result[1].accumulated_grade == pytest.approx(3.75, rel=0.01)


def test_entry_without_date_is_ignored():
    history = [
        _entry("e1", 0.5, 4.0, "2026-03-15"),
        _entry("e2", 0.5, 2.0, None),  # no date — ignored
    ]
    result = generate_weekly_evolution(history)
    assert len(result) == 1
