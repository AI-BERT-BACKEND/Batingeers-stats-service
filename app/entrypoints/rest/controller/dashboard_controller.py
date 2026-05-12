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
    summary="R20 — Dashboard de estadísticas académicas",
    description=(
        "Retorna el dashboard completo con estadísticas académicas del usuario autenticado: "
        "promedio general (GPA), tendencia, resumen por materia y estado de tareas. "
        "Agrega datos de **academic-service** y **task-service** en una sola respuesta. "
        "Si los servicios externos no están disponibles, retorna el último snapshot cacheado en BD."
    ),
    responses={
        401: {"description": "Token JWT inválido o expirado"},
        503: {"description": "Servicios dependientes no disponibles y sin caché en BD"},
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
