import asyncio
from datetime import date

import pytest
from unittest.mock import AsyncMock, MagicMock

from com.aibert.dosw.application.service.subject_stats_service import (
    SubjectStatsService,
    _build_grade_history,
    _classify_status,
    _compute_trend,
    _current_average,
    _max_possible_grade,
    _minimum_needed,
    _parse_date,
    _projected_grade,
)

# ── _parse_date ───────────────────────────────────────────────────────────────


def test_parse_date_valid_iso():
    assert _parse_date("2026-03-15") == date(2026, 3, 15)


def test_parse_date_none():
    assert _parse_date(None) is None


def test_parse_date_empty_string():
    assert _parse_date("") is None


def test_parse_date_invalid_format():
    assert _parse_date("not-a-date") is None


def test_parse_date_partial_date():
    assert _parse_date("2026-03") is None


# ── _current_average ──────────────────────────────────────────────────────────


def test_current_average_empty():
    assert _current_average([]) == 0.0


def test_current_average_no_grades():
    evals = [{"weight": 0.5, "grade": None}]
    assert _current_average(evals) == 0.0


def test_current_average_single():
    assert _current_average([{"weight": 1.0, "grade": 4.0}]) == pytest.approx(4.0)


def test_current_average_two_equal_weights():
    evals = [{"weight": 0.5, "grade": 4.0}, {"weight": 0.5, "grade": 2.0}]
    assert _current_average(evals) == pytest.approx(3.0, rel=0.01)


def test_current_average_ignores_ungraded():
    evals = [{"weight": 0.5, "grade": 4.0}, {"weight": 0.5, "grade": None}]
    assert _current_average(evals) == pytest.approx(4.0, rel=0.01)


def test_current_average_zero_weight():
    assert _current_average([{"weight": 0.0, "grade": 5.0}]) == 0.0


def test_current_average_unequal_weights():
    evals = [{"weight": 0.3, "grade": 4.5}, {"weight": 0.3, "grade": 3.0}]
    # (4.5*0.3 + 3.0*0.3) / 0.6 = 2.25/0.6 = 3.75
    assert _current_average(evals) == pytest.approx(3.75, rel=0.01)


# ── _max_possible_grade ───────────────────────────────────────────────────────


def test_max_possible_no_pending_returns_current():
    evals = [{"weight": 1.0, "grade": 4.0}]
    assert _max_possible_grade(evals) == pytest.approx(4.0, rel=0.01)


def test_max_possible_all_pending():
    evals = [{"weight": 1.0, "grade": None}]
    assert _max_possible_grade(evals) == pytest.approx(5.0, rel=0.01)


def test_max_possible_mixed():
    evals = [{"weight": 0.5, "grade": 3.0}, {"weight": 0.5, "grade": None}]
    # earned=1.5, max_remaining=2.5, total=(1.5+2.5)/1.0=4.0
    assert _max_possible_grade(evals) == pytest.approx(4.0, rel=0.01)


def test_max_possible_zero_weight():
    assert _max_possible_grade([]) == 0.0


# ── _minimum_needed ───────────────────────────────────────────────────────────


def test_minimum_needed_no_pending():
    assert _minimum_needed([{"weight": 1.0, "grade": 4.0}]) is None


def test_minimum_needed_achievable():
    evals = [
        {"weight": 0.6, "grade": 4.5},
        {"weight": 0.4, "grade": None},
    ]
    # min = (3.0*1.0 - 4.5*0.6) / 0.4 = (3.0 - 2.7) / 0.4 = 0.75
    assert _minimum_needed(evals) == pytest.approx(0.75, rel=0.01)


def test_minimum_needed_already_passing():
    # If min_needed <= 0, return 0.0
    evals = [
        {"weight": 0.9, "grade": 5.0},
        {"weight": 0.1, "grade": None},
    ]
    # min = (3.0*1.0 - 5.0*0.9) / 0.1 = (3.0 - 4.5) / 0.1 = -15 → 0.0
    assert _minimum_needed(evals) == pytest.approx(0.0)


def test_minimum_needed_impossible():
    evals = [
        {"weight": 0.9, "grade": 1.0},
        {"weight": 0.1, "grade": None},
    ]
    # min = (3.0*1.0 - 1.0*0.9) / 0.1 = (3.0 - 0.9) / 0.1 = 21 → None
    assert _minimum_needed(evals) is None


def test_minimum_needed_zero_pending_weight():
    # pending_weight = 0 → None
    assert _minimum_needed([{"weight": 0.0, "grade": None}]) is None


# ── _compute_trend ────────────────────────────────────────────────────────────


def test_compute_trend_stable_too_few():
    evals = [{"grade": 4.0, "date": "2026-01-01"}, {"grade": 3.0, "date": "2026-02-01"}]
    assert _compute_trend(evals) == "stable"


def test_compute_trend_stable_no_dates():
    evals = [{"grade": 4.0, "date": None} for _ in range(5)]
    assert _compute_trend(evals) == "stable"


def test_compute_trend_improving():
    evals = [
        {"grade": 2.0, "date": "2026-01-01"},
        {"grade": 2.0, "date": "2026-01-15"},
        {"grade": 4.5, "date": "2026-02-01"},
        {"grade": 5.0, "date": "2026-02-15"},
        {"grade": 5.0, "date": "2026-03-01"},
    ]
    assert _compute_trend(evals) == "improving"


def test_compute_trend_declining():
    evals = [
        {"grade": 5.0, "date": "2026-01-01"},
        {"grade": 5.0, "date": "2026-01-15"},
        {"grade": 2.0, "date": "2026-02-01"},
        {"grade": 1.5, "date": "2026-02-15"},
        {"grade": 1.0, "date": "2026-03-01"},
    ]
    assert _compute_trend(evals) == "declining"


def test_compute_trend_stable_within_threshold():
    evals = [
        {"grade": 3.5, "date": "2026-01-01"},
        {"grade": 3.6, "date": "2026-01-15"},
        {"grade": 3.6, "date": "2026-02-01"},
        {"grade": 3.5, "date": "2026-02-15"},
        {"grade": 3.6, "date": "2026-03-01"},
    ]
    assert _compute_trend(evals) == "stable"


# ── _projected_grade ──────────────────────────────────────────────────────────


def test_projected_grade_all_graded():
    evals = [{"weight": 0.5, "grade": 4.0}, {"weight": 0.5, "grade": 2.0}]
    assert _projected_grade(evals) == pytest.approx(3.0, rel=0.01)


def test_projected_grade_with_pending_assumes_zero():
    evals = [{"weight": 0.5, "grade": 4.0}, {"weight": 0.5, "grade": None}]
    # (4.0*0.5 + 0) / 1.0 = 2.0
    assert _projected_grade(evals) == pytest.approx(2.0, rel=0.01)


def test_projected_grade_all_pending():
    assert _projected_grade([{"weight": 1.0, "grade": None}]) == 0.0


def test_projected_grade_empty():
    assert _projected_grade([]) == 0.0


# ── _classify_status ──────────────────────────────────────────────────────────


def test_subject_classify_passing():
    assert _classify_status(3.5) == "passing"


def test_subject_classify_at_risk():
    assert _classify_status(3.2) == "at_risk"


def test_subject_classify_failing():
    assert _classify_status(2.9) == "failing"


# ── _build_grade_history ──────────────────────────────────────────────────────


def test_build_grade_history_sorted_by_date():
    evals = [
        {
            "id": "e2",
            "name": "Final",
            "weight": 0.5,
            "grade": 3.0,
            "date": "2026-04-01",
        },
        {
            "id": "e1",
            "name": "Parcial",
            "weight": 0.5,
            "grade": 4.0,
            "date": "2026-03-01",
        },
        {"id": "e3", "name": "Pending", "weight": 0.3, "grade": None, "date": None},
    ]
    history = _build_grade_history(evals)
    dated = [g for g in history if g.date is not None]
    assert dated[0].evaluation_id == "e1"
    assert dated[1].evaluation_id == "e2"


def test_build_grade_history_contribution_graded():
    evals = [{"id": "e1", "name": "P1", "weight": 0.5, "grade": 4.0, "date": None}]
    history = _build_grade_history(evals)
    assert history[0].contribution == pytest.approx(2.0, rel=0.01)


def test_build_grade_history_contribution_ungraded():
    evals = [{"id": "e1", "name": "P1", "weight": 0.5, "grade": None, "date": None}]
    history = _build_grade_history(evals)
    assert history[0].contribution == 0.0


def test_build_grade_history_length():
    evals = [
        {"id": "e1", "name": "P1", "weight": 0.5, "grade": 4.0, "date": "2026-03-01"},
        {"id": "e2", "name": "P2", "weight": 0.5, "grade": None, "date": None},
    ]
    assert len(_build_grade_history(evals)) == 2


# ── SubjectStatsService (via asyncio.run) ─────────────────────────────────────

_SUBJECT = {
    "id": "sub-1",
    "name": "Cálculo I",
    "code": "MAT101",
    "credits": 4,
    "evaluations": [
        {"id": "e1", "name": "P1", "weight": 0.3, "grade": 4.5, "date": "2026-03-15"},
        {"id": "e2", "name": "P2", "weight": 0.3, "grade": 3.0, "date": "2026-04-15"},
        {"id": "e3", "name": "Final", "weight": 0.4, "grade": None, "date": None},
    ],
}

_TASKS = [
    {"id": "t1", "subject_id": "sub-1", "status": "COMPLETED"},
    {"id": "t2", "subject_id": "sub-1", "status": "OVERDUE"},
    {"id": "t3", "subject_id": "sub-1", "status": "PENDING"},
    {"id": "t4", "subject_id": "sub-1", "status": "CANCELLED"},
]


def _make_service(subject=_SUBJECT, tasks=_TASKS, repo=None):
    academic = MagicMock()
    academic.get_subject = AsyncMock(return_value=subject)
    academic.get_subjects = AsyncMock(return_value=[subject] if subject else [])
    task = MagicMock()
    task.get_tasks_by_subject = AsyncMock(return_value=tasks)
    task.get_tasks = AsyncMock(return_value=tasks)
    return SubjectStatsService(academic, task, repo)


def test_get_subject_stats_average():
    service = _make_service()
    result = asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))
    assert result.current_average == pytest.approx(3.75, rel=0.01)


def test_get_subject_stats_tasks_total():
    service = _make_service()
    result = asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))
    assert result.tasks_total == 3  # CANCELLED excluded


def test_get_subject_stats_task_completion():
    service = _make_service()
    result = asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))
    assert result.tasks_completed == 1
    assert result.tasks_overdue == 1
    assert result.tasks_pending == 1


def test_get_subject_stats_status_valid():
    service = _make_service()
    result = asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))
    assert result.status in ("passing", "at_risk", "failing")


def test_get_subject_stats_not_found_raises():
    from com.aibert.dosw.domain.exceptions.stats_exceptions import SubjectNotFoundError

    academic = MagicMock()
    academic.get_subject = AsyncMock(return_value=None)
    task_client = MagicMock()
    task_client.get_tasks_by_subject = AsyncMock(return_value=[])
    service = SubjectStatsService(academic, task_client)
    with pytest.raises(SubjectNotFoundError):
        asyncio.run(service.get_subject_stats("u1", "nonexistent", "tok"))


def test_get_subject_stats_service_unavailable_no_repo():
    from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError

    academic = MagicMock()
    academic.get_subject = AsyncMock(side_effect=ServiceUnavailableError("academic"))
    task_client = MagicMock()
    task_client.get_tasks_by_subject = AsyncMock(return_value=[])
    service = SubjectStatsService(academic, task_client, repo=None)
    with pytest.raises(ServiceUnavailableError):
        asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))


def test_get_subject_stats_service_unavailable_with_cache():
    from datetime import datetime
    from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError
    from com.aibert.dosw.domain.model.subject_stats import SubjectStats

    cached = SubjectStats(
        subject_id="sub-1",
        subject_name="Cálculo",
        subject_code="MAT101",
        credits=4,
        grade_history=[],
        current_average=4.0,
        max_possible_grade=4.0,
        minimum_needed=None,
        trend="stable",
        tasks_total=0,
        tasks_completed=0,
        tasks_pending=0,
        tasks_overdue=0,
        task_completion_rate=0.0,
        status="passing",
        generated_at=datetime(2026, 4, 1),
    )
    academic = MagicMock()
    academic.get_subject = AsyncMock(side_effect=ServiceUnavailableError("academic"))
    task_client = MagicMock()
    task_client.get_tasks_by_subject = AsyncMock(return_value=[])
    repo = MagicMock()
    repo.get_latest_subject_snapshot = AsyncMock(return_value=cached)
    service = SubjectStatsService(academic, task_client, repo=repo)
    result = asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))
    assert result.current_average == pytest.approx(4.0)


def test_get_subject_stats_service_unavailable_no_cache_raises():
    from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError

    academic = MagicMock()
    academic.get_subject = AsyncMock(side_effect=ServiceUnavailableError("academic"))
    task_client = MagicMock()
    task_client.get_tasks_by_subject = AsyncMock(return_value=[])
    repo = MagicMock()
    repo.get_latest_subject_snapshot = AsyncMock(return_value=None)
    service = SubjectStatsService(academic, task_client, repo=repo)
    with pytest.raises(ServiceUnavailableError):
        asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))


def test_get_subject_stats_with_repo_saves():
    repo = MagicMock()
    repo.save_subject_snapshot = AsyncMock()
    service = _make_service(repo=repo)
    result = asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))
    repo.save_subject_snapshot.assert_called_once_with("u1", result)


def test_get_all_subjects_stats_returns_list():
    service = _make_service()
    result = asyncio.run(service.get_all_subjects_stats("u1", "tok"))
    assert len(result) == 1
    assert result[0].subject_id == "sub-1"


def test_get_all_subjects_stats_with_repo_saves():
    repo = MagicMock()
    repo.save_subject_snapshot = AsyncMock()
    service = _make_service(repo=repo)
    asyncio.run(service.get_all_subjects_stats("u1", "tok"))
    repo.save_subject_snapshot.assert_called_once()


def test_get_all_subjects_stats_service_unavailable():
    from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError

    academic = MagicMock()
    academic.get_subjects = AsyncMock(side_effect=ServiceUnavailableError("academic"))
    task_client = MagicMock()
    task_client.get_tasks = AsyncMock(return_value=[])
    service = SubjectStatsService(academic, task_client)
    with pytest.raises(ServiceUnavailableError):
        asyncio.run(service.get_all_subjects_stats("u1", "tok"))


def test_get_subject_stats_projected_grade():
    subject = {
        **_SUBJECT,
        "evaluations": [
            {
                "id": "e1",
                "name": "P1",
                "weight": 0.4,
                "grade": 4.0,
                "date": "2026-03-15",
            },
            {"id": "e2", "name": "Final", "weight": 0.6, "grade": None, "date": None},
        ],
    }
    service = _make_service(subject=subject, tasks=[])
    result = asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))
    # projected = (4.0*0.4 + 0) / 1.0 = 1.6
    assert result.projected_grade == pytest.approx(1.6, rel=0.01)


def test_get_subject_stats_related_tasks_excludes_cancelled():
    service = _make_service()
    result = asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))
    statuses = [t.get("status") for t in result.related_tasks]
    assert "CANCELLED" not in statuses


def test_get_subject_stats_related_tasks_sorted_desc():
    tasks = [
        {
            "id": "t1",
            "subject_id": "sub-1",
            "status": "COMPLETED",
            "dueDate": "2026-04-01",
        },
        {
            "id": "t2",
            "subject_id": "sub-1",
            "status": "PENDING",
            "dueDate": "2026-03-01",
        },
    ]
    service = _make_service(tasks=tasks)
    result = asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))
    due_dates = [t.get("dueDate") or "" for t in result.related_tasks]
    assert due_dates == sorted(due_dates, reverse=True)


def test_get_subject_stats_max_possible_above_current():
    service = _make_service()
    result = asyncio.run(service.get_subject_stats("u1", "sub-1", "tok"))
    assert result.max_possible_grade >= result.current_average
