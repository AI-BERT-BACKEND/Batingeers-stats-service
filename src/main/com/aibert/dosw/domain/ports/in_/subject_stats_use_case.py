from abc import ABC, abstractmethod

from com.aibert.dosw.domain.model.subject_stats import SubjectStats


class SubjectStatsUseCase(ABC):
    @abstractmethod
    async def get_all_subjects_stats(
        self, user_id: str, token: str
    ) -> list[SubjectStats]:
        pass

    @abstractmethod
    async def get_subject_stats(
        self, user_id: str, subject_id: str, token: str
    ) -> SubjectStats:
        pass
