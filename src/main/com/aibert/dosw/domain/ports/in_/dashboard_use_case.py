from abc import ABC, abstractmethod

from com.aibert.dosw.domain.model.dashboard import DashboardStats


class DashboardUseCase(ABC):
    @abstractmethod
    async def get_dashboard(self, user_id: str, token: str) -> DashboardStats:
        pass
