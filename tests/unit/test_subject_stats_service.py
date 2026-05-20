import pytest
from unittest.mock import AsyncMock, MagicMock

from com.aibert.dosw.application.service.subject_stats_service import (
    SubjectStatsService,
)
from com.aibert.dosw.domain.exceptions.stats_exceptions import SubjectNotFoundError

_SUBJECT = {
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
            "grade": 3.0,
            "date": "2026-04-15",
        },
        {"id": "e3", "name": "Final", "weight": 0.4, "grade": None, "date": None},
    ],
}

_TASKS = [
    {"id": "t1", "subject_id": "sub-1", "status": "COMPLETED"},
    {"id": "t2", "subject_id": "sub-1", "status": "OVERDUE"},
    {"id": "t3", "subject_id": "sub-1", "status": "PENDING"},
    {"id": "t4", "subject_id": "sub-1", "status": "CANCELLED"},
]


@pytest.fixture
def service():
    academic = MagicMock()
    academic.get_subjects = AsyncMock(return_value=[_SUBJECT])
    academic.get_subject = AsyncMock(return_value=_SUBJECT)
    task = MagicMock()
    task.get_tasks = AsyncMock(return_value=_TASKS)
    task.get_tasks_by_subject = AsyncMock(return_value=_TASKS)
    return SubjectStatsService(academic, task)


@pytest.mark.asyncio
async def test_get_all_subjects_returns_list(service):
    result = await service.get_all_subjects_stats("user-1", "token")
    assert len(result) == 1
    assert result[0].subject_id == "sub-1"


@pytest.mark.asyncio
async def test_current_average_weighted_correctly(service):
    result = await service.get_subject_stats("user-1", "sub-1", "token")
    # Solo e1 y e2 tienen nota; pesos iguales (0.3 cada uno)
    # avg = (4.5 * 0.3 + 3.0 * 0.3) / (0.3 + 0.3) = 2.25 / 0.6 = 3.75
    assert result.current_average == 3.75


@pytest.mark.asyncio
async def test_max_possible_grade_above_current(service):
    result = await service.get_subject_stats("user-1", "sub-1", "token")
    assert result.max_possible_grade > result.current_average
    assert result.max_possible_grade <= 5.0


@pytest.mark.asyncio
async def test_minimum_needed_computed_for_pending_evaluations(service):
    result = await service.get_subject_stats("user-1", "sub-1", "token")
    # earned = 4.5*0.3 + 3.0*0.3 = 2.25
    # min_needed = (3.0 * 1.0 - 2.25) / 0.4 = 0.75 / 0.4 = 1.875
    assert result.minimum_needed is not None
    assert abs(result.minimum_needed - 1.875) < 0.01


@pytest.mark.asyncio
async def test_task_counts_exclude_cancelled(service):
    result = await service.get_subject_stats("user-1", "sub-1", "token")
    assert result.tasks_total == 3  # t4 (CANCELLED) excluido
    assert result.tasks_completed == 1
    assert result.tasks_overdue == 1
    assert result.tasks_pending == 1


@pytest.mark.asyncio
async def test_task_completion_rate(service):
    result = await service.get_subject_stats("user-1", "sub-1", "token")
    assert result.task_completion_rate == pytest.approx(33.33, rel=0.01)


@pytest.mark.asyncio
async def test_grade_history_sorted_chronologically(service):
    result = await service.get_subject_stats("user-1", "sub-1", "token")
    dated = [g for g in result.grade_history if g.date is not None]
    assert dated == sorted(dated, key=lambda g: g.date)


@pytest.mark.asyncio
async def test_status_is_valid_value(service):
    result = await service.get_subject_stats("user-1", "sub-1", "token")
    assert result.status in ("passing", "at_risk", "failing")


@pytest.mark.asyncio
async def test_subject_not_found_raises_exception():
    academic = MagicMock()
    academic.get_subject = AsyncMock(return_value=None)
    task = MagicMock()
    task.get_tasks_by_subject = AsyncMock(return_value=[])
    svc = SubjectStatsService(academic, task)

    with pytest.raises(SubjectNotFoundError):
        await svc.get_subject_stats("user-1", "nonexistent-id", "token")


@pytest.mark.asyncio
async def test_no_grades_returns_zero_average():
    subject_no_grades = {
        **_SUBJECT,
        "evaluations": [
            {
                "id": "e1",
                "name": "Parcial 1",
                "weight": 0.5,
                "grade": None,
                "date": None,
            },
            {"id": "e2", "name": "Final", "weight": 0.5, "grade": None, "date": None},
        ],
    }
    academic = MagicMock()
    academic.get_subject = AsyncMock(return_value=subject_no_grades)
    task = MagicMock()
    task.get_tasks_by_subject = AsyncMock(return_value=[])
    svc = SubjectStatsService(academic, task)

    result = await svc.get_subject_stats("user-1", "sub-1", "token")

    assert result.current_average == 0.0
    assert result.minimum_needed is not None  # Aún hay evaluaciones pendientes
