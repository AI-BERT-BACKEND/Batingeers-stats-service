import pytest
from unittest.mock import AsyncMock, MagicMock

from com.aibert.dosw.application.service.dashboard_service import DashboardService
from com.aibert.dosw.application.service.subject_stats_service import (
    SubjectStatsService,
)

# ── Fixtures de datos ─────────────────────────────────────────────────────────

_SUBJECT_MIXED = {
    "id": "sub-1",
    "name": "Cálculo I",
    "code": "MAT101",
    "credits": 4,
    "evaluations": [
        {
            "id": "e1",
            "name": "Parcial 1",
            "weight": 0.4,
            "grade": 4.0,
            "date": "2026-03-15",
        },
        {"id": "e2", "name": "Final", "weight": 0.6, "grade": None, "date": None},
    ],
}

_TASKS_WITH_DATES = [
    {"id": "t1", "subject_id": "sub-1", "status": "COMPLETED", "dueDate": "2026-04-01"},
    {"id": "t2", "subject_id": "sub-1", "status": "TODO", "dueDate": "2026-03-15"},
    {
        "id": "t3",
        "subject_id": "sub-1",
        "status": "IN_PROGRESS",
        "dueDate": "2026-02-28",
    },
    {"id": "t4", "subject_id": "sub-1", "status": "CANCELLED", "dueDate": "2026-04-10"},
]


def _make_subject_service(subject, tasks):
    academic = MagicMock()
    academic.get_subject = AsyncMock(return_value=subject)
    task = MagicMock()
    task.get_tasks_by_subject = AsyncMock(return_value=tasks)
    return SubjectStatsService(academic, task)


# ── R21: projected_grade ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_projected_grade_assumes_zero_on_pending():
    svc = _make_subject_service(_SUBJECT_MIXED, [])
    result = await svc.get_subject_stats("u1", "sub-1", "tok")
    # e1 calificada: 4.0 * 0.4 = 1.6; e2 pendiente: 0 * 0.6 = 0; total = 1.6 / 1.0 = 1.6
    assert result.projected_grade == pytest.approx(1.6, rel=0.01)


@pytest.mark.asyncio
async def test_projected_grade_equals_average_when_all_graded():
    subject_all_graded = {
        **_SUBJECT_MIXED,
        "evaluations": [
            {
                "id": "e1",
                "name": "P1",
                "weight": 0.5,
                "grade": 4.0,
                "date": "2026-03-15",
            },
            {
                "id": "e2",
                "name": "P2",
                "weight": 0.5,
                "grade": 3.0,
                "date": "2026-04-15",
            },
        ],
    }
    svc = _make_subject_service(subject_all_graded, [])
    result = await svc.get_subject_stats("u1", "sub-1", "tok")
    # Todos calificados: projected = current_average = (4.0*0.5 + 3.0*0.5) / 1.0 = 3.5
    assert result.projected_grade == pytest.approx(result.current_average, rel=0.01)


@pytest.mark.asyncio
async def test_projected_grade_is_zero_when_nothing_graded():
    subject_no_grades = {
        **_SUBJECT_MIXED,
        "evaluations": [
            {"id": "e1", "name": "P1", "weight": 0.5, "grade": None, "date": None},
            {"id": "e2", "name": "P2", "weight": 0.5, "grade": None, "date": None},
        ],
    }
    svc = _make_subject_service(subject_no_grades, [])
    result = await svc.get_subject_stats("u1", "sub-1", "tok")
    assert result.projected_grade == 0.0


@pytest.mark.asyncio
async def test_projected_grade_is_lower_than_current_average():
    svc = _make_subject_service(_SUBJECT_MIXED, [])
    result = await svc.get_subject_stats("u1", "sub-1", "tok")
    # projected asume 0 en pendientes, current_average ignora pendientes
    assert result.projected_grade < result.current_average


# ── R21: related_tasks ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_related_tasks_excludes_cancelled():
    svc = _make_subject_service(_SUBJECT_MIXED, _TASKS_WITH_DATES)
    result = await svc.get_subject_stats("u1", "sub-1", "tok")
    statuses = [t["status"] for t in result.related_tasks]
    assert "CANCELLED" not in statuses


@pytest.mark.asyncio
async def test_related_tasks_sorted_by_due_date_descending():
    svc = _make_subject_service(_SUBJECT_MIXED, _TASKS_WITH_DATES)
    result = await svc.get_subject_stats("u1", "sub-1", "tok")
    due_dates = [t.get("dueDate") or "" for t in result.related_tasks]
    assert due_dates == sorted(due_dates, reverse=True)


@pytest.mark.asyncio
async def test_related_tasks_count_excludes_cancelled():
    svc = _make_subject_service(_SUBJECT_MIXED, _TASKS_WITH_DATES)
    result = await svc.get_subject_stats("u1", "sub-1", "tok")
    # _TASKS_WITH_DATES tiene 4, 1 CANCELLED → 3 en related_tasks
    assert len(result.related_tasks) == 3


@pytest.mark.asyncio
async def test_related_tasks_empty_when_no_tasks():
    svc = _make_subject_service(_SUBJECT_MIXED, [])
    result = await svc.get_subject_stats("u1", "sub-1", "tok")
    assert result.related_tasks == []


# ── R20: subjects ordered by grade descending ─────────────────────────────────

_SUBJECTS_UNORDERED = [
    {
        "id": "sub-low",
        "name": "Materia Baja",
        "code": "LOW101",
        "credits": 3,
        "evaluations": [
            {
                "id": "e1",
                "name": "P1",
                "weight": 1.0,
                "grade": 2.0,
                "date": "2026-03-01",
            },
        ],
    },
    {
        "id": "sub-high",
        "name": "Materia Alta",
        "code": "HIGH101",
        "credits": 3,
        "evaluations": [
            {
                "id": "e2",
                "name": "P1",
                "weight": 1.0,
                "grade": 4.8,
                "date": "2026-03-01",
            },
        ],
    },
    {
        "id": "sub-mid",
        "name": "Materia Media",
        "code": "MID101",
        "credits": 3,
        "evaluations": [
            {
                "id": "e3",
                "name": "P1",
                "weight": 1.0,
                "grade": 3.5,
                "date": "2026-03-01",
            },
        ],
    },
]


@pytest.fixture
def dashboard_service():
    academic = MagicMock()
    academic.get_subjects = AsyncMock(return_value=_SUBJECTS_UNORDERED)
    task = MagicMock()
    task.get_tasks = AsyncMock(return_value=[])
    return DashboardService(academic, task)


@pytest.mark.asyncio
async def test_dashboard_subjects_ordered_by_grade_descending(dashboard_service):
    result = await dashboard_service.get_dashboard("u1", "tok")
    averages = [s.current_average for s in result.subjects]
    assert averages == sorted(averages, reverse=True)


@pytest.mark.asyncio
async def test_dashboard_first_subject_has_highest_grade(dashboard_service):
    result = await dashboard_service.get_dashboard("u1", "tok")
    assert result.subjects[0].subject_id == "sub-high"


@pytest.mark.asyncio
async def test_dashboard_last_subject_has_lowest_grade(dashboard_service):
    result = await dashboard_service.get_dashboard("u1", "tok")
    assert result.subjects[-1].subject_id == "sub-low"
