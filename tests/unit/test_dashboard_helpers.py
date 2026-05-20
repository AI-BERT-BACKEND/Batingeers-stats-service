import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock

from com.aibert.dosw.application.service.dashboard_service import (
    DashboardService,
    _classify_status,
    _compute_gpa_trend,
    _compute_overall_gpa,
    _weighted_average,
)

# ── _classify_status ──────────────────────────────────────────────────────────


def test_classify_status_passing_above_threshold():
    assert _classify_status(3.5) == "passing"


def test_classify_status_passing_well_above():
    assert _classify_status(5.0) == "passing"


def test_classify_status_at_risk_just_below_3_5():
    assert _classify_status(3.4) == "at_risk"


def test_classify_status_at_risk_at_3_0():
    assert _classify_status(3.0) == "at_risk"


def test_classify_status_failing_below_3():
    assert _classify_status(2.9) == "failing"


def test_classify_status_failing_zero():
    assert _classify_status(0.0) == "failing"


def test_classify_status_exactly_3_5_is_passing():
    assert _classify_status(3.5) == "passing"


# ── _weighted_average ─────────────────────────────────────────────────────────


def test_weighted_average_empty_list():
    assert _weighted_average([]) == 0.0


def test_weighted_average_no_grades():
    evals = [{"weight": 0.5, "grade": None}, {"weight": 0.5, "grade": None}]
    assert _weighted_average(evals) == 0.0


def test_weighted_average_single_grade():
    evals = [{"weight": 1.0, "grade": 4.0}]
    assert _weighted_average(evals) == pytest.approx(4.0, rel=0.01)


def test_weighted_average_two_equal_weights():
    evals = [{"weight": 0.5, "grade": 4.0}, {"weight": 0.5, "grade": 2.0}]
    assert _weighted_average(evals) == pytest.approx(3.0, rel=0.01)


def test_weighted_average_ignores_ungraded():
    evals = [{"weight": 0.5, "grade": 4.0}, {"weight": 0.5, "grade": None}]
    assert _weighted_average(evals) == pytest.approx(4.0, rel=0.01)


def test_weighted_average_zero_weight_graded():
    evals = [{"weight": 0.0, "grade": 5.0}]
    assert _weighted_average(evals) == 0.0


def test_weighted_average_unequal_weights():
    evals = [{"weight": 0.4, "grade": 5.0}, {"weight": 0.6, "grade": 2.0}]
    # (5.0*0.4 + 2.0*0.6) / (0.4+0.6) = (2.0 + 1.2) / 1.0 = 3.2
    assert _weighted_average(evals) == pytest.approx(3.2, rel=0.01)


# ── _compute_overall_gpa ──────────────────────────────────────────────────────


def test_gpa_no_subjects():
    assert _compute_overall_gpa([]) == 0.0


def test_gpa_zero_credits():
    assert _compute_overall_gpa([{"_avg": 4.0, "credits": 0}]) == 0.0


def test_gpa_single_subject():
    subjects = [{"_avg": 3.5, "credits": 4}]
    assert _compute_overall_gpa(subjects) == pytest.approx(3.5, rel=0.01)


def test_gpa_equal_credits():
    subjects = [{"_avg": 4.0, "credits": 3}, {"_avg": 2.0, "credits": 3}]
    assert _compute_overall_gpa(subjects) == pytest.approx(3.0, rel=0.01)


def test_gpa_weighted_by_credits():
    subjects = [{"_avg": 5.0, "credits": 4}, {"_avg": 1.0, "credits": 1}]
    # (5.0*4 + 1.0*1) / (4+1) = 21/5 = 4.2
    assert _compute_overall_gpa(subjects) == pytest.approx(4.2, rel=0.01)


# ── _compute_gpa_trend ────────────────────────────────────────────────────────


def test_trend_no_subjects():
    assert _compute_gpa_trend([]) == "stable"


def test_trend_stable_with_few_evals():
    subjects = [{"evaluations": [{"grade": 4.0, "date": "2026-01-01"}]}]
    assert _compute_gpa_trend(subjects) == "stable"


def test_trend_stable_exactly_3_evals():
    subjects = [
        {
            "evaluations": [
                {"grade": 3.0, "date": "2026-01-01"},
                {"grade": 3.5, "date": "2026-02-01"},
                {"grade": 3.2, "date": "2026-03-01"},
            ]
        }
    ]
    assert _compute_gpa_trend(subjects) == "stable"


def test_trend_improving():
    subjects = [
        {
            "evaluations": [
                {"grade": 2.0, "date": "2026-01-01"},
                {"grade": 2.0, "date": "2026-01-15"},
                {"grade": 4.5, "date": "2026-02-01"},
                {"grade": 5.0, "date": "2026-02-15"},
            ]
        }
    ]
    assert _compute_gpa_trend(subjects) == "improving"


def test_trend_declining():
    subjects = [
        {
            "evaluations": [
                {"grade": 5.0, "date": "2026-01-01"},
                {"grade": 4.8, "date": "2026-01-15"},
                {"grade": 2.0, "date": "2026-02-01"},
                {"grade": 1.5, "date": "2026-02-15"},
            ]
        }
    ]
    assert _compute_gpa_trend(subjects) == "declining"


def test_trend_stable_within_threshold():
    subjects = [
        {
            "evaluations": [
                {"grade": 3.5, "date": "2026-01-01"},
                {"grade": 3.6, "date": "2026-01-15"},
                {"grade": 3.6, "date": "2026-02-01"},
                {"grade": 3.5, "date": "2026-02-15"},
            ]
        }
    ]
    assert _compute_gpa_trend(subjects) == "stable"


def test_trend_ignores_ungraded_and_undated():
    subjects = [
        {
            "evaluations": [
                {"grade": None, "date": "2026-01-01"},
                {"grade": 3.0, "date": "2026-01-15"},
                {"grade": 4.0, "date": None},
            ]
        }
    ]
    # Only 1 graded+dated entry → stable
    assert _compute_gpa_trend(subjects) == "stable"


def test_trend_multiple_subjects():
    subjects = [
        {
            "evaluations": [
                {"grade": 2.0, "date": "2026-01-01"},
                {"grade": 2.0, "date": "2026-01-15"},
            ]
        },
        {
            "evaluations": [
                {"grade": 5.0, "date": "2026-02-01"},
                {"grade": 5.0, "date": "2026-02-15"},
            ]
        },
    ]
    # 4 total evals, mid=2: early [2.0,2.0] avg=2.0, recent [5.0,5.0] avg=5.0 → improving
    assert _compute_gpa_trend(subjects) == "improving"


# ── DashboardService (via asyncio.run) ────────────────────────────────────────


def _make_service(subjects, tasks, repo=None):
    academic = MagicMock()
    academic.get_subjects = AsyncMock(return_value=subjects)
    task = MagicMock()
    task.get_tasks = AsyncMock(return_value=tasks)
    return DashboardService(academic, task, repo)


_SUBJECTS = [
    {
        "id": "sub-1",
        "name": "Cálculo",
        "code": "MAT101",
        "credits": 4,
        "evaluations": [
            {
                "id": "e1",
                "name": "P1",
                "weight": 0.5,
                "grade": 4.0,
                "date": "2026-03-15",
            },
            {"id": "e2", "name": "P2", "weight": 0.5, "grade": None, "date": None},
        ],
    },
    {
        "id": "sub-2",
        "name": "Física",
        "code": "FIS101",
        "credits": 3,
        "evaluations": [
            {
                "id": "e3",
                "name": "P1",
                "weight": 1.0,
                "grade": 2.5,
                "date": "2026-03-20",
            },
        ],
    },
]

_TASKS = [
    {"id": "t1", "subject_id": "sub-1", "status": "COMPLETED"},
    {"id": "t2", "subject_id": "sub-1", "status": "TODO"},
    {"id": "t3", "subject_id": "sub-2", "status": "IN_PROGRESS"},
    {"id": "t4", "subject_id": "sub-1", "status": "IN_PROGRESS"},
    {"id": "t5", "subject_id": "sub-1", "status": "CANCELLED"},
]


def test_dashboard_returns_user_id():
    service = _make_service(_SUBJECTS, _TASKS)
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    assert result.user_id == "user-1"


def test_dashboard_total_subjects():
    service = _make_service(_SUBJECTS, _TASKS)
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    assert result.total_subjects == 2


def test_dashboard_subject_status_sum():
    service = _make_service(_SUBJECTS, _TASKS)
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    total = result.passing_subjects + result.at_risk_subjects + result.failing_subjects
    assert total == result.total_subjects


def test_dashboard_tasks_exclude_cancelled():
    service = _make_service(_SUBJECTS, _TASKS)
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    # t5 is CANCELLED → 4 active
    assert result.tasks.total == 4
    assert result.tasks.completed == 1
    assert result.tasks.overdue == 0
    assert result.tasks.pending == 3  # TODO + IN_PROGRESS + IN_PROGRESS


def test_dashboard_completion_rate():
    service = _make_service(_SUBJECTS, _TASKS)
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    # 1/4 = 25%
    assert result.tasks.completion_rate == pytest.approx(25.0, rel=0.01)


def test_dashboard_gpa_within_range():
    service = _make_service(_SUBJECTS, _TASKS)
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    assert 0.0 <= result.overall_gpa <= 5.0


def test_dashboard_gpa_trend_valid():
    service = _make_service(_SUBJECTS, _TASKS)
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    assert result.gpa_trend in ("improving", "declining", "stable")


def test_dashboard_subjects_sorted_by_grade_desc():
    service = _make_service(_SUBJECTS, _TASKS)
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    averages = [s.current_average for s in result.subjects]
    assert averages == sorted(averages, reverse=True)


def test_dashboard_empty_subjects_zero_gpa():
    service = _make_service([], [])
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    assert result.overall_gpa == 0.0
    assert result.total_subjects == 0
    assert result.tasks.completion_rate == 0.0


def test_dashboard_with_repo_saves_snapshot():
    repo = MagicMock()
    repo.save_dashboard_snapshot = AsyncMock()
    service = _make_service([], [], repo=repo)
    asyncio.run(service.get_dashboard("user-1", "token"))
    repo.save_dashboard_snapshot.assert_called_once()


def test_dashboard_no_repo_does_not_fail():
    service = _make_service([], [], repo=None)
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    assert result is not None


def test_dashboard_service_unavailable_no_repo_raises():
    from com.aibert.dosw.domain.exceptions.stats_exceptions import (
        ServiceUnavailableError,
    )

    academic = MagicMock()
    academic.get_subjects = AsyncMock(side_effect=ServiceUnavailableError("academic"))
    task = MagicMock()
    task.get_tasks = AsyncMock(return_value=[])
    service = DashboardService(academic, task, repo=None)

    with pytest.raises(ServiceUnavailableError):
        asyncio.run(service.get_dashboard("user-1", "token"))


def test_dashboard_service_unavailable_with_cache_returns_cached():
    from datetime import datetime
    from com.aibert.dosw.domain.exceptions.stats_exceptions import (
        ServiceUnavailableError,
    )
    from com.aibert.dosw.domain.model.dashboard import (
        DashboardStats,
        SubjectSummary,
        TaskSummary,
    )

    cached = DashboardStats(
        user_id="user-1",
        overall_gpa=3.8,
        gpa_trend="stable",
        total_subjects=1,
        passing_subjects=1,
        at_risk_subjects=0,
        failing_subjects=0,
        subjects=[
            SubjectSummary(
                subject_id="sub-1",
                name="Cálculo",
                code="MAT101",
                credits=4,
                current_average=3.8,
                status="passing",
            )
        ],
        tasks=TaskSummary(
            total=2, completed=1, pending=1, overdue=0, completion_rate=50.0
        ),
        generated_at=datetime(2026, 4, 1),
    )
    academic = MagicMock()
    academic.get_subjects = AsyncMock(side_effect=ServiceUnavailableError("academic"))
    task = MagicMock()
    task.get_tasks = AsyncMock(return_value=[])
    repo = MagicMock()
    repo.get_latest_dashboard_snapshot = AsyncMock(return_value=cached)

    service = DashboardService(academic, task, repo=repo)
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    assert result.overall_gpa == 3.8


def test_dashboard_service_unavailable_no_cache_raises():
    from com.aibert.dosw.domain.exceptions.stats_exceptions import (
        ServiceUnavailableError,
    )

    academic = MagicMock()
    academic.get_subjects = AsyncMock(side_effect=ServiceUnavailableError("academic"))
    task = MagicMock()
    task.get_tasks = AsyncMock(return_value=[])
    repo = MagicMock()
    repo.get_latest_dashboard_snapshot = AsyncMock(return_value=None)

    service = DashboardService(academic, task, repo=repo)
    with pytest.raises(ServiceUnavailableError):
        asyncio.run(service.get_dashboard("user-1", "token"))


def test_dashboard_failing_subject_counted():
    subjects = [
        {
            "id": "sub-1",
            "name": "Baja",
            "code": "LOW",
            "credits": 3,
            "evaluations": [
                {
                    "id": "e1",
                    "name": "P1",
                    "weight": 1.0,
                    "grade": 1.5,
                    "date": "2026-03-01",
                }
            ],
        }
    ]
    service = _make_service(subjects, [])
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    assert result.failing_subjects == 1
    assert result.passing_subjects == 0


def test_dashboard_at_risk_subject_counted():
    subjects = [
        {
            "id": "sub-1",
            "name": "Media",
            "code": "MID",
            "credits": 3,
            "evaluations": [
                {
                    "id": "e1",
                    "name": "P1",
                    "weight": 1.0,
                    "grade": 3.2,
                    "date": "2026-03-01",
                }
            ],
        }
    ]
    service = _make_service(subjects, [])
    result = asyncio.run(service.get_dashboard("user-1", "token"))
    assert result.at_risk_subjects == 1
