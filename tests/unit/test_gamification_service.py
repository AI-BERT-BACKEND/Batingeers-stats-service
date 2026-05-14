import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.service.gamification_service import GamificationService

# ── Helpers ───────────────────────────────────────────────────────────────────


def _task(task_id, status, completed_at=None, due_date=None):
    t = {"id": task_id, "status": status}
    if completed_at:
        t["completedAt"] = completed_at
    if due_date:
        t["dueDate"] = due_date
    return t


def _on_time(n):
    return [_task(f"t{i}", "COMPLETED", "2026-01-15", "2026-01-15") for i in range(n)]


def _late(n):
    return [_task(f"lt{i}", "COMPLETED", "2026-01-20", "2026-01-15") for i in range(n)]


def _make_service(tasks):
    client = MagicMock()
    client.get_tasks = AsyncMock(return_value=tasks)
    return GamificationService(client)


# ── Points ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_no_tasks_returns_zero_points():
    result = await _make_service([]).get_gamification_profile("u1", "tok")
    assert result.total_points == 0


@pytest.mark.asyncio
async def test_on_time_task_awards_10_points():
    tasks = [_task("t1", "COMPLETED", "2026-03-15", "2026-03-15")]
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.total_points == 10


@pytest.mark.asyncio
async def test_late_task_awards_3_points():
    tasks = [_task("t1", "COMPLETED", "2026-03-16", "2026-03-15")]
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.total_points == 3


@pytest.mark.asyncio
async def test_pending_task_awards_no_points():
    tasks = [_task("t1", "PENDING")]
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.total_points == 0


@pytest.mark.asyncio
async def test_cancelled_tasks_are_ignored():
    tasks = _on_time(3) + [_task("c1", "CANCELLED", "2026-01-15", "2026-01-15")]
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.total_points == 30  # solo las 3 on-time, la CANCELLED no cuenta


@pytest.mark.asyncio
async def test_mixed_on_time_and_late_points():
    tasks = _on_time(2) + _late(3)
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.total_points == 2 * 10 + 3 * 3  # 20 + 9 = 29


# ── Levels ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_zero_points_is_level_1():
    result = await _make_service([]).get_gamification_profile("u1", "tok")
    assert result.current_level == 1


@pytest.mark.asyncio
async def test_99_points_is_level_1():
    tasks = _on_time(9) + _late(3)  # 90 + 9 = 99 puntos
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.total_points == 99
    assert result.current_level == 1


@pytest.mark.asyncio
async def test_100_points_is_level_2():
    tasks = _on_time(10)  # 100 puntos
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.total_points == 100
    assert result.current_level == 2


@pytest.mark.asyncio
async def test_300_points_is_level_3():
    tasks = _on_time(30)  # 300 puntos
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.current_level == 3


@pytest.mark.asyncio
async def test_600_points_is_level_4():
    tasks = _on_time(60)  # 600 puntos
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.current_level == 4


# ── Progress ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_progress_at_zero_points_is_zero():
    result = await _make_service([]).get_gamification_profile("u1", "tok")
    assert result.progress_to_next == 0.0


@pytest.mark.asyncio
async def test_progress_at_50_points_is_50_percent():
    tasks = _on_time(5)  # 50 puntos → nivel 1, (50-0)/(100-0)*100 = 50%
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.progress_to_next == pytest.approx(50.0, rel=0.01)


@pytest.mark.asyncio
async def test_progress_at_max_level_is_100():
    tasks = _on_time(60)  # nivel 4 (máximo)
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert result.current_level == 4
    assert result.progress_to_next == 100.0


@pytest.mark.asyncio
async def test_progress_within_valid_range():
    tasks = _on_time(15)  # 150 puntos, nivel 2: (150-100)/(300-100)*100 = 25%
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    assert 0.0 <= result.progress_to_next <= 100.0


# ── Badges ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_no_tasks_no_badges():
    result = await _make_service([]).get_gamification_profile("u1", "tok")
    assert result.badges == []


@pytest.mark.asyncio
async def test_first_steps_badge_with_one_completed():
    tasks = [_task("t1", "COMPLETED", "2026-01-15", "2026-01-15")]
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    badge_ids = [b.badge_id for b in result.badges]
    assert "first_steps" in badge_ids


@pytest.mark.asyncio
async def test_first_steps_badge_not_earned_without_completed():
    tasks = [_task("t1", "PENDING"), _task("t2", "IN_PROGRESS")]
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    badge_ids = [b.badge_id for b in result.badges]
    assert "first_steps" not in badge_ids


@pytest.mark.asyncio
async def test_punctual_badge_requires_5_on_time():
    tasks = _on_time(5)
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    badge_ids = [b.badge_id for b in result.badges]
    assert "punctual" in badge_ids


@pytest.mark.asyncio
async def test_punctual_badge_not_earned_with_4_on_time():
    tasks = _on_time(4)
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    badge_ids = [b.badge_id for b in result.badges]
    assert "punctual" not in badge_ids


@pytest.mark.asyncio
async def test_consistent_badge_requires_10_completed():
    tasks = _on_time(10)
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    badge_ids = [b.badge_id for b in result.badges]
    assert "consistent" in badge_ids


@pytest.mark.asyncio
async def test_consistent_badge_not_earned_with_9_completed():
    tasks = _on_time(9)
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    badge_ids = [b.badge_id for b in result.badges]
    assert "consistent" not in badge_ids


@pytest.mark.asyncio
async def test_overachiever_badge_requires_300_points():
    tasks = _on_time(30)  # 300 puntos
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    badge_ids = [b.badge_id for b in result.badges]
    assert "overachiever" in badge_ids


@pytest.mark.asyncio
async def test_overachiever_badge_not_earned_below_300_points():
    tasks = _on_time(29)  # 290 puntos
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    badge_ids = [b.badge_id for b in result.badges]
    assert "overachiever" not in badge_ids


@pytest.mark.asyncio
async def test_all_badges_earned_with_enough_activity():
    # 30 on-time → 300 pts (overachiever), 30 completed (consistent), 5+ on-time (punctual), 1+ (first_steps)
    tasks = _on_time(30)
    result = await _make_service(tasks).get_gamification_profile("u1", "tok")
    badge_ids = {b.badge_id for b in result.badges}
    assert {"first_steps", "punctual", "consistent", "overachiever"} == badge_ids


# ── Profile metadata ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_user_id_is_preserved():
    result = await _make_service([]).get_gamification_profile("user-42", "tok")
    assert result.user_id == "user-42"


@pytest.mark.asyncio
async def test_generated_at_is_set():
    result = await _make_service([]).get_gamification_profile("u1", "tok")
    assert result.generated_at is not None
