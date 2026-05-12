from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.model.dashboard import DashboardStats
from app.domain.model.subject_stats import SubjectStats
from app.domain.ports.out_.stats_snapshot_port import StatsSnapshotPort
from app.infrastructure.adapters.persistence.entity.stats_snapshot_entity import (
    DashboardSnapshotEntity,
    SubjectSnapshotEntity,
)
from app.infrastructure.adapters.persistence.mapper.snapshot_mapper import (
    dashboard_to_entity,
    entity_to_dashboard,
    entity_to_subject,
    subject_to_entity,
)


class StatsSnapshotRepository(StatsSnapshotPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_dashboard_snapshot(self, stats: DashboardStats) -> None:
        entity = dashboard_to_entity(stats)
        self._session.add(entity)
        await self._session.commit()

    async def get_latest_dashboard_snapshot(
        self, user_id: str
    ) -> DashboardStats | None:
        result = await self._session.execute(
            select(DashboardSnapshotEntity)
            .where(DashboardSnapshotEntity.user_id == user_id)
            .order_by(desc(DashboardSnapshotEntity.generated_at))
            .limit(1)
        )
        entity = result.scalar_one_or_none()
        return entity_to_dashboard(entity) if entity else None

    async def save_subject_snapshot(self, user_id: str, stats: SubjectStats) -> None:
        entity = subject_to_entity(user_id, stats)
        self._session.add(entity)
        await self._session.commit()

    async def get_latest_subject_snapshot(
        self, user_id: str, subject_id: str
    ) -> SubjectStats | None:
        result = await self._session.execute(
            select(SubjectSnapshotEntity)
            .where(
                SubjectSnapshotEntity.user_id == user_id,
                SubjectSnapshotEntity.subject_id == subject_id,
            )
            .order_by(desc(SubjectSnapshotEntity.generated_at))
            .limit(1)
        )
        entity = result.scalar_one_or_none()
        return entity_to_subject(entity) if entity else None
