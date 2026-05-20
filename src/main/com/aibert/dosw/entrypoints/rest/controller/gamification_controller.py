from fastapi import APIRouter, Depends

from com.aibert.dosw.application.dto.response.gamification_response import (
    BadgeDto,
    GamificationResponseDto,
)
from com.aibert.dosw.application.service.gamification_service import GamificationService
from com.aibert.dosw.dependencies import get_current_user
from com.aibert.dosw.infrastructure.external.task_client import TaskClient

router = APIRouter(prefix="/api/stats", tags=["Gamification"])


def _get_gamification_service() -> GamificationService:
    return GamificationService(TaskClient())


@router.get(
    "/gamification",
    response_model=GamificationResponseDto,
    summary="Student gamification profile (R24)",
    description=(
        "Returns the full gamification profile for the authenticated student, computed "
        "in real time from their task completion history retrieved from task-service.\n\n"
        "**Point system:**\n"
        "- **+10 points** for each task completed on or before its due date\n"
        "- **+3 points** for each task completed after its due date\n"
        "- Cancelled tasks are fully excluded from all calculations\n\n"
        "**Level table:**\n"
        "| Level | Points required |\n"
        "|---|---|\n"
        "| 1 | 0 – 99 |\n"
        "| 2 | 100 – 299 |\n"
        "| 3 | 300 – 599 |\n"
        "| 4 | 600+ |\n\n"
        "**Badges (all 4 are always returned):**\n"
        "| Badge ID | Name | Unlock condition |\n"
        "|---|---|---|\n"
        "| `first_steps` | 🎯 First Steps | Complete at least 1 task |\n"
        "| `punctual` | ⏰ Punctual | Complete 5 or more tasks on or before the due date |\n"
        "| `consistent` | 🔥 Consistent | Complete 10 or more tasks (any timing) |\n"
        "| `overachiever` | 🏆 Overachiever | Accumulate 300 or more points (reach Level 3) |\n\n"
        "Each badge object includes an `unlocked` boolean (`true` = earned, `false` = locked) "
        "and an `unlocked_date` that is set when the badge was earned.\n\n"
        "**`progress_to_next`** represents progress toward the next level as a percentage "
        "(0.0 – 100.0). Returns 100.0 when the student is already at the maximum level (4).\n\n"
        "**Default state:** a student with no task activity receives 0 points, level 1, "
        "0% progress, and all 4 badges locked."
    ),
    responses={
        401: {"description": "Invalid or expired JWT token"},
        503: {"description": "task-service is unreachable"},
    },
)
async def get_gamification_profile(
    current_user: dict = Depends(get_current_user),
    service: GamificationService = Depends(_get_gamification_service),
) -> GamificationResponseDto:
    profile = await service.get_gamification_profile(
        user_id=current_user["user_id"],
        token=current_user["token"],
    )
    return GamificationResponseDto(
        user_id=profile.user_id,
        total_points=profile.total_points,
        current_level=profile.current_level,
        badges=[
            BadgeDto(
                badge_id=b.badge_id,
                badge_name=b.name,
                icon=b.icon,
                description=b.description,
                unlocked=b.unlocked,
                unlocked_date=b.unlocked_date,
            )
            for b in profile.badges
        ],
        progress_to_next=profile.progress_to_next,
        generated_at=profile.generated_at,
    )
