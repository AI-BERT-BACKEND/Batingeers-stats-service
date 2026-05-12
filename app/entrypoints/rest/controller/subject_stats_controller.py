from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.response.subject_stats_response import SubjectStatsResponseDto
from app.application.mapper.stats_mapper import subject_stats_to_dto
from app.application.service.subject_stats_service import SubjectStatsService
from app.dependencies import get_current_user
from app.infrastructure.db import get_db
from app.infrastructure.external.academic_client import AcademicClient
from app.infrastructure.external.task_client import TaskClient

router = APIRouter(prefix="/api/stats", tags=["Estadísticas por Materia"])


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
    summary="R21 — Estadísticas de todas las materias",
    description=(
        "Retorna estadísticas detalladas y curva de evolución de todas las materias "
        "del usuario autenticado: promedio actual, nota máxima alcanzable, nota mínima "
        "para pasar, tendencia, estado de tareas y puntos de evolución semanal para gráficas."
    ),
    responses={
        401: {"description": "Token JWT inválido o expirado"},
        503: {"description": "Uno de los servicios dependientes no está disponible"},
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
    summary="R21 — Estadísticas de una materia específica",
    description=(
        "Retorna estadísticas detalladas de una sola materia: historial de notas ordenado "
        "cronológicamente, tendencia, nota mínima necesaria para aprobar, métricas de tareas "
        "y puntos de evolución semanal para gráficas. "
        "Si el servicio externo falla, retorna el último snapshot cacheado en BD."
    ),
    responses={
        401: {"description": "Token JWT inválido o expirado"},
        404: {"description": "Materia no encontrada"},
        503: {"description": "Servicio externo no disponible y sin caché en BD"},
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
