from fastapi import APIRouter, Depends

from app.application.dto.response.subject_stats_response import SubjectStatsResponseDto
from app.application.mapper.stats_mapper import subject_stats_to_dto
from app.application.service.subject_stats_service import SubjectStatsService
from app.dependencies import get_current_user
from app.infrastructure.external.academic_client import AcademicClient
from app.infrastructure.external.task_client import TaskClient

router = APIRouter(prefix="/api/stats", tags=["Estadísticas por Materia"])


def _get_subject_stats_service() -> SubjectStatsService:
    return SubjectStatsService(AcademicClient(), TaskClient())


@router.get(
    "/subjects",
    response_model=list[SubjectStatsResponseDto],
    summary="R21 — Estadísticas de todas las materias",
    description=(
        "Retorna estadísticas detalladas y curva de evolución de todas las materias "
        "del usuario autenticado: promedio actual, nota máxima alcanzable, nota mínima "
        "para pasar, tendencia y estado de tareas por materia."
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
        "cronológicamente, tendencia, nota mínima necesaria para aprobar y métricas de tareas."
    ),
    responses={
        401: {"description": "Token JWT inválido o expirado"},
        404: {"description": "Materia no encontrada"},
        503: {"description": "Uno de los servicios dependientes no está disponible"},
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
