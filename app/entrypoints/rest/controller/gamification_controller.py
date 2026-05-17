from fastapi import APIRouter, Depends

from app.application.dto.response.gamification_response import (
    BadgeDto,
    GamificationResponseDto,
)
from app.application.service.gamification_service import GamificationService
from app.dependencies import get_current_user
from app.infrastructure.external.task_client import TaskClient

router = APIRouter(prefix="/api/stats", tags=["Gamification"])


def _get_gamification_service() -> GamificationService:
    return GamificationService(TaskClient())


@router.get(
    "/gamification",
    response_model=GamificationResponseDto,
    summary="R24 — Student gamification profile",
    description=(
        "Returns the gamification profile of the authenticated student: "
        "total accumulated points, current level, earned badges, and progress toward "
        "the next level. Points are awarded automatically upon task completion: "
        "+10 points for tasks completed on or before the due date, +3 points for late completions. "
        "If the student has no prior activity, returns level 1 with 0 points."
    ),
    responses={
        401: {"description": "Invalid or expired JWT token"},
        503: {"description": "task-service unavailable"},
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
