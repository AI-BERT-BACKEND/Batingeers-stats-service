from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.response.dashboard_response import DashboardResponseDto
from app.application.mapper.stats_mapper import dashboard_to_dto
from app.application.service.dashboard_service import DashboardService
from app.dependencies import get_current_user
from app.infrastructure.db import get_db
from app.infrastructure.external.academic_client import AcademicClient
from app.infrastructure.external.task_client import TaskClient

router = APIRouter(prefix="/api/stats", tags=["Dashboard"])


async def _get_dashboard_service(
    db: AsyncSession | None = Depends(get_db),
) -> DashboardService:
    repo = None
    if db is not None:
        from app.infrastructure.adapters.persistence.repository.stats_repository import (
            StatsSnapshotRepository,
        )

        repo = StatsSnapshotRepository(db)
    return DashboardService(AcademicClient(), TaskClient(), repo)


@router.get(
    "/dashboard",
    response_model=DashboardResponseDto,
    summary="R20 — Academic statistics dashboard",
    description=(
        "Returns the full dashboard with academic statistics for the authenticated user: "
        "overall GPA, trend, subject summary, and task status. "
        "Aggregates data from **academic-service** and **task-service** in a single response. "
        "If external services are unavailable, returns the last snapshot cached in the DB."
    ),
    responses={
        401: {"description": "Invalid or expired JWT token"},
        503: {"description": "Dependent services unavailable and no cached data in DB"},
    },
)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(_get_dashboard_service),
) -> DashboardResponseDto:
    stats = await service.get_dashboard(
        user_id=current_user["user_id"],
        token=current_user["token"],
    )
    return dashboard_to_dto(stats)
