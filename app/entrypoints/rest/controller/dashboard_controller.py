from fastapi import APIRouter, Depends

from app.application.dto.response.dashboard_response import DashboardResponseDto
from app.application.mapper.stats_mapper import dashboard_to_dto
from app.application.service.dashboard_service import DashboardService
from app.dependencies import get_current_user
from app.infrastructure.external.academic_client import AcademicClient
from app.infrastructure.external.task_client import TaskClient

router = APIRouter(prefix="/api/stats", tags=["Dashboard"])


def _get_dashboard_service() -> DashboardService:
    return DashboardService(AcademicClient(), TaskClient())


@router.get(
    "/dashboard",
    response_model=DashboardResponseDto,
    summary="R20 — Dashboard de estadísticas académicas",
    description=(
        "Retorna el dashboard completo con estadísticas académicas del usuario autenticado: "
        "promedio general (GPA), tendencia, resumen por materia y estado de tareas. "
        "Agrega datos de **academic-service** y **task-service** en una sola respuesta."
    ),
    responses={
        401: {"description": "Token JWT inválido o expirado"},
        503: {"description": "Uno de los servicios dependientes no está disponible"},
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
