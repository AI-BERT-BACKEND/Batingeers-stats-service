from abc import ABC, abstractmethod

from app.domain.model.dashboard import DashboardStats
from app.domain.model.subject_stats import SubjectStats


class StatsSnapshotPort(ABC):
    @abstractmethod
    async def save_dashboard_snapshot(self, stats: DashboardStats) -> None:
        pass

    @abstractmethod
    async def get_latest_dashboard_snapshot(
        self, user_id: str
    ) -> DashboardStats | None:
        pass

    @abstractmethod
    async def save_subject_snapshot(self, user_id: str, stats: SubjectStats) -> None:
        pass

    @abstractmethod
    async def get_latest_subject_snapshot(
        self, user_id: str, subject_id: str
    ) -> SubjectStats | None:
        pass
