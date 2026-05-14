from datetime import datetime

from app.domain.model.gamification import Badge, GamificationProfile
from app.domain.ports.in_.gamification_use_case import GamificationUseCase
from app.infrastructure.external.task_client import TaskClient

# Level thresholds: index = level-1, value = min points for that level
_LEVEL_THRESHOLDS = [0, 100, 300, 600]

_ALL_BADGES: list[dict] = [
    {
        "badge_id": "first_steps",
        "name": "First Steps",
        "icon": "🎯",
        "description": "Complete your first task",
    },
    {
        "badge_id": "punctual",
        "name": "Punctual",
        "icon": "⏰",
        "description": "Complete 5 tasks on or before the due date",
    },
    {
        "badge_id": "consistent",
        "name": "Consistent",
        "icon": "🔥",
        "description": "Complete 10 tasks",
    },
    {
        "badge_id": "overachiever",
        "name": "Overachiever",
        "icon": "🏆",
        "description": "Reach Level 3 (300+ points)",
    },
]


def _is_on_time(task: dict) -> bool:
    completed_at = task.get("completedAt") or task.get("completed_at")
    due_date = task.get("dueDate") or task.get("due_date")
    if not completed_at or not due_date:
        return True  # benefit of the doubt when dates are missing
    try:
        return completed_at[:10] <= due_date[:10]
    except (TypeError, IndexError):
        return True


def _calculate_points(tasks: list[dict]) -> int:
    points = 0
    for task in tasks:
        if task.get("status") != "COMPLETED":
            continue
        points += 10 if _is_on_time(task) else 3
    return points


def _calculate_level(points: int) -> int:
    level = 1
    for i, threshold in enumerate(_LEVEL_THRESHOLDS):
        if points >= threshold:
            level = i + 1
    return level


def _calculate_progress(points: int, level: int) -> float:
    if level >= len(_LEVEL_THRESHOLDS):
        return 100.0
    current_threshold = _LEVEL_THRESHOLDS[level - 1]
    next_threshold = _LEVEL_THRESHOLDS[level]
    points_in_level = points - current_threshold
    points_needed = next_threshold - current_threshold
    return round(min(points_in_level / points_needed * 100, 100.0), 2)


def _calculate_badges(tasks: list[dict], points: int) -> list[Badge]:
    completed = [t for t in tasks if t.get("status") == "COMPLETED"]
    on_time_count = sum(1 for t in completed if _is_on_time(t))

    earned: list[Badge] = []
    for cfg in _ALL_BADGES:
        badge_id = cfg["badge_id"]
        unlocked = False
        if badge_id == "first_steps" and len(completed) >= 1:
            unlocked = True
        elif badge_id == "punctual" and on_time_count >= 5:
            unlocked = True
        elif badge_id == "consistent" and len(completed) >= 10:
            unlocked = True
        elif badge_id == "overachiever" and points >= 300:
            unlocked = True
        if unlocked:
            earned.append(Badge(**cfg))
    return earned


class GamificationService(GamificationUseCase):
    def __init__(self, task_client: TaskClient) -> None:
        self._tasks = task_client

    async def get_gamification_profile(
        self, user_id: str, token: str
    ) -> GamificationProfile:
        tasks = await self._tasks.get_tasks(user_id, token)
        active = [t for t in tasks if t.get("status") != "CANCELLED"]

        points = _calculate_points(active)
        level = _calculate_level(points)
        progress = _calculate_progress(points, level)
        badges = _calculate_badges(active, points)

        return GamificationProfile(
            user_id=user_id,
            total_points=points,
            current_level=level,
            badges=badges,
            progress_to_next=progress,
            generated_at=datetime.utcnow(),
        )
