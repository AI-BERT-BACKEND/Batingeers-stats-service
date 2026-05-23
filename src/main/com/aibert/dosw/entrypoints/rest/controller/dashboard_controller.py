from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from com.aibert.dosw.application.dto.response.dashboard_response import (
    DashboardResponseDto,
)
from com.aibert.dosw.application.mapper.stats_mapper import dashboard_to_dto
from com.aibert.dosw.application.service.dashboard_service import DashboardService
from com.aibert.dosw.dependencies import get_current_user
from com.aibert.dosw.infrastructure.db import get_db
from com.aibert.dosw.infrastructure.external.academic_client import AcademicClient
from com.aibert.dosw.infrastructure.external.task_client import TaskClient

router = APIRouter(prefix="/api/stats", tags=["Dashboard"])


def _get_dashboard_service(
    db: Annotated[AsyncSession | None, Depends(get_db)],
) -> DashboardService:
    repo = None
    if db is not None:
        from com.aibert.dosw.infrastructure.adapters.persistence.repository.stats_repository import (
            StatsSnapshotRepository,
        )

        repo = StatsSnapshotRepository(db)
    return DashboardService(AcademicClient(), TaskClient(), repo)


@router.get(
    "/dashboard",
    summary="Academic statistics dashboard (R20)",
    description=(
        "Returns the complete academic dashboard for the authenticated student, "
        "aggregating data from **academic-service** and **task-service** in a single response.\n\n"
        "**What is included:**\n"
        "- `overall_gpa` — weighted GPA across all active subjects (credits used as weights), "
        "rounded to the nearest integer\n"
        "- `gpa_trend` — direction of grade change: `improving`, `stable`, or `declining`, "
        "computed by comparing early vs recent evaluation scores\n"
        "- `subjects` — list of all subjects sorted by current average (descending), each with "
        "status: `Passing`, `At Risk`, or `Failing`\n"
        "- `tasks` — aggregated task metrics: total, completed, pending (includes in-progress), "
        "overdue, and completion rate as a percentage\n\n"
        "**Fallback behavior:** if either upstream service is unreachable, the last snapshot "
        "cached in the database is returned. A 503 is raised only when there is no cached "
        "data available at all.\n\n"
        "**Kafka events published after each call:**\n"
        "- `stats.academic-performance-alert` — when at least one subject is At Risk or Failing\n"
        "- `stats.academic-overload-alert` — when GPA trend is declining AND there are overdue tasks"
    ),
    responses={
        200: {
            "description": "Academic dashboard retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "overall_gpa": 4,
                        "gpa_trend": "stable",
                        "total_subjects": 5,
                        "passing_subjects": 3,
                        "at_risk_subjects": 1,
                        "failing_subjects": 1,
                        "subjects": [
                            {
                                "subject_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                                "name": "Cálculo Diferencial",
                                "code": "MAT-101",
                                "credits": 4,
                                "current_average": 4.2,
                                "status": "Passing",
                                "teacher_name": "Dr. García",
                            }
                        ],
                        "tasks": {
                            "total": 12,
                            "completed": 8,
                            "pending": 3,
                            "overdue": 1,
                            "completion_rate": 66.7,
                        },
                        "generated_at": "2026-05-22T16:52:39.763Z",
                    }
                }
            },
        },
        401: {"description": "Invalid or expired JWT token"},
        503: {
            "description": "Upstream services unreachable and no cached snapshot available"
        },
    },
)
async def get_dashboard(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[DashboardService, Depends(_get_dashboard_service)],
) -> DashboardResponseDto:
    stats = await service.get_dashboard(
        user_id=current_user["user_id"],
        token=current_user["token"],
    )
    return dashboard_to_dto(stats)
