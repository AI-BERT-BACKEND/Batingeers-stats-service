import pytest
from unittest.mock import AsyncMock, MagicMock

from com.aibert.dosw.application.service.dashboard_service import DashboardService

_SUBJECTS = [
    {
        "id": "sub-1",
        "name": "Cálculo I",
        "code": "MAT101",
        "credits": 4,
        "evaluations": [
            {
                "id": "e1",
                "name": "Parcial 1",
                "weight": 0.3,
                "grade": 4.5,
                "date": "2026-03-15",
            },
            {
                "id": "e2",
                "name": "Parcial 2",
                "weight": 0.3,
                "grade": 3.8,
                "date": "2026-04-15",
            },
            {"id": "e3", "name": "Final", "weight": 0.4, "grade": None, "date": None},
        ],
    },
    {
        "id": "sub-2",
        "name": "Programación I",
        "code": "INF101",
        "credits": 3,
        "evaluations": [
            {
                "id": "e4",
                "name": "Taller 1",
                "weight": 0.25,
                "grade": 5.0,
                "date": "2026-03-10",
            },
            {
                "id": "e5",
                "name": "Taller 2",
                "weight": 0.25,
                "grade": 4.8,
                "date": "2026-04-10",
            },
            {
                "id": "e6",
                "name": "Proyecto",
                "weight": 0.5,
                "grade": None,
                "date": None,
            },
        ],
    },
]

_TASKS = [
    {"id": "t1", "subject_id": "sub-1", "status": "COMPLETED"},
    {"id": "t2", "subject_id": "sub-1", "status": "TODO"},
    {"id": "t3", "subject_id": "sub-2", "status": "COMPLETED"},
    {"id": "t4", "subject_id": "sub-2", "status": "IN_PROGRESS"},
    {"id": "t5", "subject_id": "sub-1", "status": "COMPLETED"},
    {"id": "t6", "subject_id": "sub-1", "status": "CANCELLED"},  # no debe contarse
]


@pytest.fixture
def service():
    academic = MagicMock()
    academic.get_subjects = AsyncMock(return_value=_SUBJECTS)
    task = MagicMock()
    task.get_tasks = AsyncMock(return_value=_TASKS)
    return DashboardService(academic, task)


@pytest.mark.asyncio
async def test_gpa_is_within_valid_range(service):
    result = await service.get_dashboard("user-1", "token")
    assert 0.0 <= result.overall_gpa <= 5.0


@pytest.mark.asyncio
async def test_total_subjects_count(service):
    result = await service.get_dashboard("user-1", "token")
    assert result.total_subjects == 2


@pytest.mark.asyncio
async def test_subject_status_counts_sum_to_total(service):
    result = await service.get_dashboard("user-1", "token")
    total = result.passing_subjects + result.at_risk_subjects + result.failing_subjects
    assert total == result.total_subjects


@pytest.mark.asyncio
async def test_task_counts_exclude_cancelled(service):
    result = await service.get_dashboard("user-1", "token")
    assert result.tasks.total == 5  # t6 (CANCELLED) excluido
    assert result.tasks.completed == 3
    assert result.tasks.pending == 2
    assert result.tasks.overdue == 0


@pytest.mark.asyncio
async def test_completion_rate_calculation(service):
    result = await service.get_dashboard("user-1", "token")
    assert result.tasks.completion_rate == 60.0  # 3/5 * 100


@pytest.mark.asyncio
async def test_gpa_trend_is_valid_value(service):
    result = await service.get_dashboard("user-1", "token")
    assert result.gpa_trend in ("improving", "declining", "stable")


@pytest.mark.asyncio
async def test_empty_subjects_returns_zero_gpa():
    academic = MagicMock()
    academic.get_subjects = AsyncMock(return_value=[])
    task = MagicMock()
    task.get_tasks = AsyncMock(return_value=[])
    svc = DashboardService(academic, task)

    result = await svc.get_dashboard("user-1", "token")

    assert result.overall_gpa == 0.0
    assert result.total_subjects == 0
    assert result.gpa_trend == "stable"
    assert result.tasks.completion_rate == 0.0


@pytest.mark.asyncio
async def test_each_subject_summary_has_valid_status(service):
    result = await service.get_dashboard("user-1", "token")
    for subject in result.subjects:
        assert subject.status in ("passing", "at_risk", "failing")
