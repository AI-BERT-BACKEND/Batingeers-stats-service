from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from com.aibert.dosw.application.dto.response.subject_stats_response import (
    SubjectStatsResponseDto,
)
from com.aibert.dosw.application.mapper.stats_mapper import subject_stats_to_dto
from com.aibert.dosw.application.service.subject_stats_service import (
    SubjectStatsService,
)
from com.aibert.dosw.dependencies import get_current_user
from com.aibert.dosw.infrastructure.db import get_db
from com.aibert.dosw.infrastructure.external.academic_client import AcademicClient
from com.aibert.dosw.infrastructure.external.task_client import TaskClient

router = APIRouter(prefix="/api/stats", tags=["Subject Statistics"])


def _get_subject_stats_service(
    db: Annotated[AsyncSession | None, Depends(get_db)],
) -> SubjectStatsService:
    repo = None
    if db is not None:
        from com.aibert.dosw.infrastructure.adapters.persistence.repository.stats_repository import (
            StatsSnapshotRepository,
        )

        repo = StatsSnapshotRepository(db)
    return SubjectStatsService(AcademicClient(), TaskClient(), repo)


@router.get(
    "/subjects",
    summary="Statistics for all subjects (R21)",
    description=(
        "Returns detailed statistics for every subject belonging to the authenticated student. "
        "Each entry contains the full grade breakdown, projection calculations, task metrics, "
        "and chart data.\n\n"
        "**Fields per subject:**\n"
        "- `grades_by_period` — each evaluation period with its weight, obtained grade, "
        "contribution to final grade, and the projected final grade\n"
        "- `current_average` — weighted average computed only from graded evaluations so far\n"
        "- `max_possible_grade` — best achievable final grade if the student scores 5.0 "
        "on every remaining evaluation\n"
        "- `minimum_needed` — minimum grade required in pending evaluations to reach the "
        "passing threshold (3.0); `null` if already passing or mathematically impossible\n"
        "- `projected_grade` — expected final grade assuming 0.0 on all ungraded evaluations\n"
        "- `trend` — performance direction: `improving`, `stable`, or `declining`\n"
        "- `grade_evolution` — weekly cumulative grade chart points; populated only when "
        "at least 2 periods have a recorded grade (RN-02)\n"
        "- `related_tasks` — tasks associated with this subject, sorted by due date descending"
    ),
    responses={
        401: {"description": "Invalid or expired JWT token"},
        503: {"description": "One of the upstream services is unavailable"},
    },
)
async def get_all_subjects_stats(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[SubjectStatsService, Depends(_get_subject_stats_service)],
) -> list[SubjectStatsResponseDto]:
    stats_list = await service.get_all_subjects_stats(
        user_id=current_user["user_id"],
        token=current_user["token"],
    )
    return [subject_stats_to_dto(s) for s in stats_list]


@router.get(
    "/subjects/{subject_id}",
    summary="Statistics for a specific subject (R21)",
    description=(
        "Returns the full analytics profile for a single subject. Equivalent to one item "
        "from `GET /api/stats/subjects`, but fetches only the requested subject — "
        "more efficient when the frontend only needs to display one subject detail view.\n\n"
        "**Grade evolution rule (RN-02):** `grade_evolution` is only populated when at least "
        "2 evaluation periods have a recorded grade. If the student has fewer graded periods, "
        "the array is returned empty and should be treated as 'not enough data yet'.\n\n"
        "**Kafka events published:**\n"
        "- `stats.study-suggestion` — when the subject's grade trend is `declining`\n\n"
        "**Fallback behavior:** if the upstream service fails, the last cached snapshot "
        "is returned. A 503 is raised only when no cached data exists at all."
    ),
    responses={
        401: {"description": "Invalid or expired JWT token"},
        404: {"description": "Subject not found"},
        503: {
            "description": "Upstream service unreachable and no cached snapshot available"
        },
    },
)
async def get_subject_stats(
    subject_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[SubjectStatsService, Depends(_get_subject_stats_service)],
) -> SubjectStatsResponseDto:
    stats = await service.get_subject_stats(
        user_id=current_user["user_id"],
        subject_id=subject_id,
        token=current_user["token"],
    )
    return subject_stats_to_dto(stats)
