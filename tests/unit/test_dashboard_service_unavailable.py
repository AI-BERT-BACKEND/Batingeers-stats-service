import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from com.aibert.dosw.application.service.dashboard_service import DashboardService
from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError
from com.aibert.dosw.domain.model.dashboard import (
    DashboardStats,
    SubjectSummary,
    TaskSummary,
)


def _make_cached_dashboard(user_id: str = "user-1") -> DashboardStats:
    return DashboardStats(
        user_id=user_id,
        overall_gpa=3.8,
        gpa_trend="stable",
        total_subjects=2,
        passing_subjects=2,
        at_risk_subjects=0,
        failing_subjects=0,
        subjects=[
            SubjectSummary(
                subject_id="sub-1",
                name="Cálculo I",
                code="MAT101",
                credits=4,
                current_average=3.8,
                status="passing",
            )
        ],
        tasks=TaskSummary(
            total=5, completed=3, pending=1, overdue=1, completion_rate=60.0
        ),
        generated_at=datetime(2026, 4, 1, 10, 0, 0),
    )


@pytest.fixture
def academic_unavailable():
    client = MagicMock()
    client.get_subjects = AsyncMock(
        side_effect=ServiceUnavailableError("academic-service")
    )
    return client


@pytest.fixture
def task_unavailable():
    client = MagicMock()
    client.get_tasks = AsyncMock(side_effect=ServiceUnavailableError("task-service"))
    return client


@pytest.fixture
def ok_academic():
    client = MagicMock()
    client.get_subjects = AsyncMock(return_value=[])
    return client


@pytest.fixture
def ok_task():
    client = MagicMock()
    client.get_tasks = AsyncMock(return_value=[])
    return client


# ── R20: servicio externo no disponible ────────────────────────────────────────


@pytest.mark.asyncio
async def test_academic_unavailable_without_repo_raises(academic_unavailable, ok_task):
    svc = DashboardService(academic_unavailable, ok_task, repo=None)
    with pytest.raises(ServiceUnavailableError):
        await svc.get_dashboard("user-1", "token")


@pytest.mark.asyncio
async def test_task_unavailable_without_repo_raises(ok_academic, task_unavailable):
    svc = DashboardService(ok_academic, task_unavailable, repo=None)
    with pytest.raises(ServiceUnavailableError):
        await svc.get_dashboard("user-1", "token")


@pytest.mark.asyncio
async def test_academic_unavailable_returns_cached_snapshot(
    academic_unavailable, ok_task
):
    cached = _make_cached_dashboard("user-1")
    repo = MagicMock()
    repo.get_latest_dashboard_snapshot = AsyncMock(return_value=cached)

    svc = DashboardService(academic_unavailable, ok_task, repo=repo)
    result = await svc.get_dashboard("user-1", "token")

    assert result.overall_gpa == 3.8
    assert result.user_id == "user-1"
    repo.get_latest_dashboard_snapshot.assert_called_once_with("user-1")


@pytest.mark.asyncio
async def test_service_unavailable_no_cache_raises(academic_unavailable, ok_task):
    repo = MagicMock()
    repo.get_latest_dashboard_snapshot = AsyncMock(return_value=None)

    svc = DashboardService(academic_unavailable, ok_task, repo=repo)
    with pytest.raises(ServiceUnavailableError):
        await svc.get_dashboard("user-1", "token")


@pytest.mark.asyncio
async def test_successful_call_saves_snapshot_to_repo(ok_academic, ok_task):
    repo = MagicMock()
    repo.save_dashboard_snapshot = AsyncMock()

    svc = DashboardService(ok_academic, ok_task, repo=repo)
    await svc.get_dashboard("user-1", "token")

    repo.save_dashboard_snapshot.assert_called_once()
    saved: DashboardStats = repo.save_dashboard_snapshot.call_args[0][0]
    assert saved.user_id == "user-1"


@pytest.mark.asyncio
async def test_successful_call_without_repo_does_not_fail(ok_academic, ok_task):
    svc = DashboardService(ok_academic, ok_task, repo=None)
    result = await svc.get_dashboard("user-1", "token")
    assert result.user_id == "user-1"
