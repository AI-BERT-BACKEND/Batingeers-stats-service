from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.response.subject_stats_response import SubjectStatsResponseDto
from app.application.mapper.stats_mapper import subject_stats_to_dto
from app.application.service.subject_stats_service import SubjectStatsService
from app.dependencies import get_current_user
from app.infrastructure.db import get_db
from app.infrastructure.external.academic_client import AcademicClient
from app.infrastructure.external.task_client import TaskClient

router = APIRouter(prefix="/api/stats", tags=["Subject Statistics"])


async def _get_subject_stats_service(
    db: AsyncSession | None = Depends(get_db),
) -> SubjectStatsService:
    repo = None
    if db is not None:
        from app.infrastructure.adapters.persistence.repository.stats_repository import (
            StatsSnapshotRepository,
        )
        repo = StatsSnapshotRepository(db)
    return SubjectStatsService(AcademicClient(), TaskClient(), repo)


@router.get(
    "/subjects",
    response_model=list[SubjectStatsResponseDto],
    summary="R21 — Statistics for all subjects",
    description=(
        "Returns detailed statistics and evolution curve for all subjects "
        "of the authenticated user: current average, maximum achievable grade, minimum grade "
        "to pass, trend, task status, and weekly evolution points for charts."
    ),
    responses={
        401: {"description": "Invalid or expired JWT token"},
        503: {"description": "One of the dependent services is unavailable"},
    },
)
async def get_all_subjects_stats(
    current_user: dict = Depends(get_current_user),
    service: SubjectStatsService = Depends(_get_subject_stats_service),
) -> list[SubjectStatsResponseDto]:
    stats_list = await service.get_all_subjects_stats(
        user_id=current_user["user_id"],
        token=current_user["token"],
    )
    return [subject_stats_to_dto(s) for s in stats_list]


@router.get(
    "/subjects/{subject_id}",
    response_model=SubjectStatsResponseDto,
    summary="R21 — Statistics for a specific subject",
    description=(
        "Returns detailed statistics for a single subject: grade history sorted "
        "chronologically, trend, minimum grade needed to pass, task metrics, "
        "and weekly evolution points for charts. "
        "If the external service fails, returns the last snapshot cached in the DB."
    ),
    responses={
        401: {"description": "Invalid or expired JWT token"},
        404: {"description": "Subject not found"},
        503: {"description": "External service unavailable and no cached data in DB"},
    },
)
async def get_subject_stats(
    subject_id: str,
    current_user: dict = Depends(get_current_user),
    service: SubjectStatsService = Depends(_get_subject_stats_service),
) -> SubjectStatsResponseDto:
    stats = await service.get_subject_stats(
        user_id=current_user["user_id"],
        subject_id=subject_id,
        token=current_user["token"],
    )
    return subject_stats_to_dto(stats)
