import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.domain.model.dashboard import DashboardStats, SubjectSummary, TaskSummary
from app.domain.model.subject_stats import GradeEntry, SubjectStats
from app.infrastructure.adapters.persistence.mapper.snapshot_mapper import (
    dashboard_to_entity,
    entity_to_dashboard,
    entity_to_subject,
    subject_to_entity,
)


def _make_dashboard() -> DashboardStats:
    return DashboardStats(
        user_id="u-1",
        overall_gpa=3.9,
        gpa_trend="improving",
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
                current_average=3.9,
                status="passing",
            )
        ],
        tasks=TaskSummary(
            total=3, completed=2, pending=1, overdue=0, completion_rate=66.67
        ),
        generated_at=datetime(2026, 4, 10, 12, 0, 0),
    )


def _make_subject_stats() -> SubjectStats:
    return SubjectStats(
        subject_id="sub-1",
        subject_name="Cálculo",
        subject_code="MAT101",
        credits=4,
        grade_history=[
            GradeEntry("e1", "Parcial 1", 0.3, 4.5, None, 1.35),
        ],
        current_average=4.5,
        max_possible_grade=4.5,
        minimum_needed=None,
        trend="stable",
        tasks_total=2,
        tasks_completed=1,
        tasks_pending=1,
        tasks_overdue=0,
        task_completion_rate=50.0,
        status="passing",
        generated_at=datetime(2026, 4, 10, 12, 0, 0),
    )


# ── Mapper: DashboardStats ↔ Entity ───────────────────────────────────────────


def test_dashboard_to_entity_preserves_user_id():
    entity = dashboard_to_entity(_make_dashboard())
    assert entity.user_id == "u-1"


def test_dashboard_to_entity_preserves_gpa():
    entity = dashboard_to_entity(_make_dashboard())
    assert entity.overall_gpa == pytest.approx(3.9, rel=0.001)


def test_dashboard_to_entity_subjects_data_is_list():
    entity = dashboard_to_entity(_make_dashboard())
    assert isinstance(entity.subjects_data, list)
    assert entity.subjects_data[0]["subject_id"] == "sub-1"


def test_dashboard_to_entity_tasks_data_is_dict():
    entity = dashboard_to_entity(_make_dashboard())
    assert entity.tasks_data["total"] == 3
    assert entity.tasks_data["completion_rate"] == pytest.approx(66.67, rel=0.01)


def test_entity_to_dashboard_roundtrip():
    original = _make_dashboard()
    entity = dashboard_to_entity(original)
    restored = entity_to_dashboard(entity)

    assert restored.user_id == original.user_id
    assert restored.overall_gpa == original.overall_gpa
    assert restored.gpa_trend == original.gpa_trend
    assert len(restored.subjects) == 1
    assert restored.subjects[0].subject_id == "sub-1"
    assert restored.tasks.total == 3


# ── Mapper: SubjectStats ↔ Entity ─────────────────────────────────────────────


def test_subject_to_entity_preserves_ids():
    entity = subject_to_entity("u-1", _make_subject_stats())
    assert entity.user_id == "u-1"
    assert entity.subject_id == "sub-1"


def test_subject_to_entity_grade_history_serialized():
    entity = subject_to_entity("u-1", _make_subject_stats())
    assert isinstance(entity.grade_history_data, list)
    assert entity.grade_history_data[0]["evaluation_id"] == "e1"
    assert entity.grade_history_data[0]["grade"] == pytest.approx(4.5)


def test_entity_to_subject_roundtrip():
    original = _make_subject_stats()
    entity = subject_to_entity("u-1", original)
    restored = entity_to_subject(entity)

    assert restored.subject_id == original.subject_id
    assert restored.current_average == original.current_average
    assert restored.trend == original.trend
    assert len(restored.grade_history) == 1
    assert restored.grade_history[0].evaluation_id == "e1"


def test_subject_to_entity_empty_chart_data():
    stats = _make_subject_stats()
    stats.chart_data = []
    entity = subject_to_entity("u-1", stats)
    assert entity.chart_data == []


def test_entity_to_subject_minimum_needed_none():
    entity = subject_to_entity("u-1", _make_subject_stats())
    restored = entity_to_subject(entity)
    assert restored.minimum_needed is None


# ── Repository: operaciones con sesión mockeada ───────────────────────────────


@pytest.mark.asyncio
async def test_repository_save_dashboard_adds_and_commits():
    from app.infrastructure.adapters.persistence.repository.stats_repository import (
        StatsSnapshotRepository,
    )

    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()

    repo = StatsSnapshotRepository(session)
    await repo.save_dashboard_snapshot(_make_dashboard())

    session.add.assert_called_once()
    session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_repository_get_dashboard_returns_none_when_not_found():
    from app.infrastructure.adapters.persistence.repository.stats_repository import (
        StatsSnapshotRepository,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    session = MagicMock()
    session.execute = AsyncMock(return_value=mock_result)

    repo = StatsSnapshotRepository(session)
    result = await repo.get_latest_dashboard_snapshot("user-nobody")

    assert result is None


@pytest.mark.asyncio
async def test_repository_save_subject_adds_and_commits():
    from app.infrastructure.adapters.persistence.repository.stats_repository import (
        StatsSnapshotRepository,
    )

    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()

    repo = StatsSnapshotRepository(session)
    await repo.save_subject_snapshot("u-1", _make_subject_stats())

    session.add.assert_called_once()
    session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_repository_get_subject_returns_none_when_not_found():
    from app.infrastructure.adapters.persistence.repository.stats_repository import (
        StatsSnapshotRepository,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    session = MagicMock()
    session.execute = AsyncMock(return_value=mock_result)

    repo = StatsSnapshotRepository(session)
    result = await repo.get_latest_subject_snapshot("u-nobody", "sub-x")

    assert result is None
