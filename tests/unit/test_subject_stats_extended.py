import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from com.aibert.dosw.application.service.subject_stats_service import SubjectStatsService
from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError
from com.aibert.dosw.domain.model.subject_stats import GradeEntry, SubjectStats


_SUBJECT_SINGLE_GRADE = {
    "id": "sub-x",
    "name": "Física I",
    "code": "FIS101",
    "credits": 3,
    "evaluations": [
        {
            "id": "e1",
            "name": "Único corte",
            "weight": 1.0,
            "grade": 4.2,
            "date": "2026-03-20",
        },
    ],
}

_SUBJECT_NO_DATES = {
    "id": "sub-y",
    "name": "Historia",
    "code": "HIS101",
    "credits": 2,
    "evaluations": [
        {"id": "e1", "name": "Parcial", "weight": 0.5, "grade": 3.5, "date": None},
        {"id": "e2", "name": "Final", "weight": 0.5, "grade": None, "date": None},
    ],
}


def _make_cached_subject(subject_id: str = "sub-x") -> SubjectStats:
    return SubjectStats(
        subject_id=subject_id,
        subject_name="Física I",
        subject_code="FIS101",
        credits=3,
        grade_history=[GradeEntry("e1", "Único corte", 1.0, 4.2, None, 4.2)],
        current_average=4.2,
        max_possible_grade=4.2,
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


# ── R21: un solo corte registrado ──────────────────────────────────────────────


@pytest.fixture
def service_single_grade():
    academic = MagicMock()
    academic.get_subject = AsyncMock(return_value=_SUBJECT_SINGLE_GRADE)
    task = MagicMock()
    task.get_tasks_by_subject = AsyncMock(return_value=[])
    return SubjectStatsService(academic, task)


@pytest.mark.asyncio
async def test_single_grade_average_equals_that_grade(service_single_grade):
    result = await service_single_grade.get_subject_stats("u1", "sub-x", "tok")
    assert result.current_average == pytest.approx(4.2, rel=0.01)


@pytest.mark.asyncio
async def test_single_grade_max_possible_equals_current_when_fully_graded(
    service_single_grade,
):
    result = await service_single_grade.get_subject_stats("u1", "sub-x", "tok")
    # Solo hay una evaluación y ya está calificada → max = current
    assert result.max_possible_grade == pytest.approx(4.2, rel=0.01)


@pytest.mark.asyncio
async def test_single_grade_no_minimum_needed(service_single_grade):
    result = await service_single_grade.get_subject_stats("u1", "sub-x", "tok")
    # No hay evaluaciones pendientes → no hay nota mínima requerida
    assert result.minimum_needed is None


@pytest.mark.asyncio
async def test_single_grade_trend_is_stable(service_single_grade):
    result = await service_single_grade.get_subject_stats("u1", "sub-x", "tok")
    # Menos de 3 notas registradas → siempre stable
    assert result.trend == "stable"


@pytest.mark.asyncio
async def test_single_grade_generates_one_chart_point(service_single_grade):
    result = await service_single_grade.get_subject_stats("u1", "sub-x", "tok")
    assert len(result.chart_data) == 1
    assert result.chart_data[0].accumulated_grade == pytest.approx(4.2, rel=0.01)


@pytest.mark.asyncio
async def test_grade_without_date_generates_no_chart_points():
    academic = MagicMock()
    academic.get_subject = AsyncMock(return_value=_SUBJECT_NO_DATES)
    task = MagicMock()
    task.get_tasks_by_subject = AsyncMock(return_value=[])
    svc = SubjectStatsService(academic, task)

    result = await svc.get_subject_stats("u1", "sub-y", "tok")

    # e1 tiene nota pero no tiene fecha → no genera punto de evolución
    assert result.chart_data == []
    assert result.current_average == pytest.approx(3.5, rel=0.01)


# ── R21: servicio externo no disponible ───────────────────────────────────────


@pytest.mark.asyncio
async def test_service_unavailable_without_repo_raises():
    academic = MagicMock()
    academic.get_subject = AsyncMock(
        side_effect=ServiceUnavailableError("academic-service")
    )
    task = MagicMock()
    task.get_tasks_by_subject = AsyncMock(return_value=[])
    svc = SubjectStatsService(academic, task, repo=None)

    with pytest.raises(ServiceUnavailableError):
        await svc.get_subject_stats("u1", "sub-x", "tok")


@pytest.mark.asyncio
async def test_service_unavailable_returns_cached_snapshot():
    cached = _make_cached_subject("sub-x")
    academic = MagicMock()
    academic.get_subject = AsyncMock(
        side_effect=ServiceUnavailableError("academic-service")
    )
    task = MagicMock()
    task.get_tasks_by_subject = AsyncMock(return_value=[])
    repo = MagicMock()
    repo.get_latest_subject_snapshot = AsyncMock(return_value=cached)

    svc = SubjectStatsService(academic, task, repo=repo)
    result = await svc.get_subject_stats("u1", "sub-x", "tok")

    assert result.subject_id == "sub-x"
    assert result.current_average == pytest.approx(4.2, rel=0.01)
    repo.get_latest_subject_snapshot.assert_called_once_with("u1", "sub-x")


@pytest.mark.asyncio
async def test_service_unavailable_no_cache_raises():
    academic = MagicMock()
    academic.get_subject = AsyncMock(
        side_effect=ServiceUnavailableError("academic-service")
    )
    task = MagicMock()
    task.get_tasks_by_subject = AsyncMock(return_value=[])
    repo = MagicMock()
    repo.get_latest_subject_snapshot = AsyncMock(return_value=None)

    svc = SubjectStatsService(academic, task, repo=repo)
    with pytest.raises(ServiceUnavailableError):
        await svc.get_subject_stats("u1", "sub-x", "tok")


@pytest.mark.asyncio
async def test_successful_call_saves_snapshot():
    academic = MagicMock()
    academic.get_subject = AsyncMock(return_value=_SUBJECT_SINGLE_GRADE)
    task = MagicMock()
    task.get_tasks_by_subject = AsyncMock(return_value=[])
    repo = MagicMock()
    repo.save_subject_snapshot = AsyncMock()

    svc = SubjectStatsService(academic, task, repo=repo)
    result = await svc.get_subject_stats("u1", "sub-x", "tok")

    repo.save_subject_snapshot.assert_called_once_with("u1", result)
