from abc import ABC, abstractmethod

from com.aibert.dosw.domain.model.gamification import GamificationProfile


class GamificationUseCase(ABC):
    @abstractmethod
    async def get_gamification_profile(
        self, user_id: str, token: str
    ) -> GamificationProfile:
        pass
