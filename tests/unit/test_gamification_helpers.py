import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.service.gamification_service import (
    GamificationService,
    _calculate_badges,
    _calculate_level,
    _calculate_points,
    _calculate_progress,
    _is_on_time,
)

# ── _is_on_time ───────────────────────────────────────────────────────────────


def test_is_on_time_completed_before_due():
    assert _is_on_time({"completedAt": "2026-01-10", "dueDate": "2026-01-20"}) is True


def test_is_on_time_completed_exactly_on_due():
    assert _is_on_time({"completedAt": "2026-01-15", "dueDate": "2026-01-15"}) is True


def test_is_late_when_completed_after_due():
    assert _is_on_time({"completedAt": "2026-01-20", "dueDate": "2026-01-15"}) is False


def test_is_on_time_no_completed_at_returns_true():
    assert _is_on_time({"dueDate": "2026-01-15"}) is True


def test_is_on_time_no_due_date_returns_true():
    assert _is_on_time({"completedAt": "2026-01-15"}) is True


def test_is_on_time_empty_dict_returns_true():
    assert _is_on_time({}) is True


def test_is_on_time_snake_case_on_time():
    assert _is_on_time({"completed_at": "2026-01-10", "due_date": "2026-01-20"}) is True


def test_is_on_time_snake_case_late():
    assert (
        _is_on_time({"completed_at": "2026-01-25", "due_date": "2026-01-20"}) is False
    )


# ── _calculate_points ─────────────────────────────────────────────────────────


def test_calculate_points_empty_list():
    assert _calculate_points([]) == 0


def test_calculate_points_on_time_task_gives_10():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-15"}
    ]
    assert _calculate_points(tasks) == 10


def test_calculate_points_late_task_gives_3():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-20", "dueDate": "2026-01-15"}
    ]
    assert _calculate_points(tasks) == 3


def test_calculate_points_pending_not_counted():
    assert _calculate_points([{"status": "PENDING"}]) == 0


def test_calculate_points_in_progress_not_counted():
    assert _calculate_points([{"status": "IN_PROGRESS"}]) == 0


def test_calculate_points_mixed_tasks():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-15"},
        {"status": "COMPLETED", "completedAt": "2026-01-20", "dueDate": "2026-01-15"},
        {"status": "PENDING"},
    ]
    assert _calculate_points(tasks) == 13


def test_calculate_points_multiple_on_time():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-20"}
        for _ in range(5)
    ]
    assert _calculate_points(tasks) == 50


# ── _calculate_level ──────────────────────────────────────────────────────────


def test_level_1_at_0_points():
    assert _calculate_level(0) == 1


def test_level_1_at_99_points():
    assert _calculate_level(99) == 1


def test_level_2_at_100_points():
    assert _calculate_level(100) == 2


def test_level_2_at_299_points():
    assert _calculate_level(299) == 2


def test_level_3_at_300_points():
    assert _calculate_level(300) == 3


def test_level_3_at_599_points():
    assert _calculate_level(599) == 3


def test_level_4_at_600_points():
    assert _calculate_level(600) == 4


def test_level_4_above_600():
    assert _calculate_level(1000) == 4


# ── _calculate_progress ───────────────────────────────────────────────────────


def test_progress_zero_points_is_zero():
    assert _calculate_progress(0, 1) == 0.0


def test_progress_50_points_in_level_1():
    assert _calculate_progress(50, 1) == pytest.approx(50.0, rel=0.01)


def test_progress_at_max_level_is_100():
    assert _calculate_progress(600, 4) == 100.0


def test_progress_above_max_level_is_100():
    assert _calculate_progress(900, 4) == 100.0


def test_progress_level_2_midpoint():
    # Level 2: thresholds 100-300 → (200-100)/(300-100)*100 = 50%
    assert _calculate_progress(200, 2) == pytest.approx(50.0, rel=0.01)


def test_progress_level_3_quarter():
    # Level 3: thresholds 300-600 → (375-300)/(600-300)*100 = 25%
    assert _calculate_progress(375, 3) == pytest.approx(25.0, rel=0.01)


# ── _calculate_badges ─────────────────────────────────────────────────────────


def test_badges_empty_tasks():
    assert _calculate_badges([], 0) == []


def test_badges_pending_only():
    assert _calculate_badges([{"status": "PENDING"}], 0) == []


def test_first_steps_badge_one_completed():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-15"}
    ]
    ids = [b.badge_id for b in _calculate_badges(tasks, 10)]
    assert "first_steps" in ids


def test_punctual_badge_five_on_time():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-20"}
        for _ in range(5)
    ]
    ids = [b.badge_id for b in _calculate_badges(tasks, 50)]
    assert "punctual" in ids


def test_punctual_badge_not_earned_with_four():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-20"}
        for _ in range(4)
    ]
    ids = [b.badge_id for b in _calculate_badges(tasks, 40)]
    assert "punctual" not in ids


def test_consistent_badge_ten_completed():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-20"}
        for _ in range(10)
    ]
    ids = [b.badge_id for b in _calculate_badges(tasks, 100)]
    assert "consistent" in ids


def test_consistent_badge_not_earned_with_nine():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-20"}
        for _ in range(9)
    ]
    ids = [b.badge_id for b in _calculate_badges(tasks, 90)]
    assert "consistent" not in ids


def test_overachiever_badge_300_points():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-20"}
        for _ in range(30)
    ]
    ids = [b.badge_id for b in _calculate_badges(tasks, 300)]
    assert "overachiever" in ids


def test_overachiever_not_earned_below_300():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-20"}
        for _ in range(29)
    ]
    ids = [b.badge_id for b in _calculate_badges(tasks, 290)]
    assert "overachiever" not in ids


def test_all_badges_earned():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-20"}
        for _ in range(30)
    ]
    ids = {b.badge_id for b in _calculate_badges(tasks, 300)}
    assert ids == {"first_steps", "punctual", "consistent", "overachiever"}


# ── GamificationService (via asyncio.run) ─────────────────────────────────────


def _make_client(tasks):
    client = MagicMock()
    client.get_tasks = AsyncMock(return_value=tasks)
    return client


def test_service_no_tasks_returns_zero():
    service = GamificationService(_make_client([]))
    result = asyncio.run(service.get_gamification_profile("u1", "tok"))
    assert result.total_points == 0
    assert result.current_level == 1
    assert result.user_id == "u1"
    assert result.generated_at is not None


def test_service_on_time_task_10_points():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-03-15", "dueDate": "2026-03-15"}
    ]
    service = GamificationService(_make_client(tasks))
    result = asyncio.run(service.get_gamification_profile("u1", "tok"))
    assert result.total_points == 10


def test_service_late_task_3_points():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-03-20", "dueDate": "2026-03-15"}
    ]
    service = GamificationService(_make_client(tasks))
    result = asyncio.run(service.get_gamification_profile("u1", "tok"))
    assert result.total_points == 3


def test_service_cancelled_tasks_excluded():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-15"},
        {"status": "CANCELLED", "completedAt": "2026-01-15", "dueDate": "2026-01-15"},
    ]
    service = GamificationService(_make_client(tasks))
    result = asyncio.run(service.get_gamification_profile("u1", "tok"))
    assert result.total_points == 10


def test_service_level_2_at_100_points():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-20"}
        for _ in range(10)
    ]
    service = GamificationService(_make_client(tasks))
    result = asyncio.run(service.get_gamification_profile("u1", "tok"))
    assert result.total_points == 100
    assert result.current_level == 2


def test_service_progress_50_percent():
    tasks = [
        {"status": "COMPLETED", "completedAt": "2026-01-15", "dueDate": "2026-01-20"}
        for _ in range(5)
    ]
    service = GamificationService(_make_client(tasks))
    result = asyncio.run(service.get_gamification_profile("u1", "tok"))
    assert result.total_points == 50
    assert result.progress_to_next == pytest.approx(50.0, rel=0.01)
