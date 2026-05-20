import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from com.aibert.dosw.config import settings
from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError

_SERVICE = "task-service"


class TaskClient:
    """
    Cliente HTTP para task-service.
    Equivalente a un @FeignClient en Spring Cloud, pero para Python con httpx.

    Endpoints esperados en task-service:
      GET /api/tasks/user/{userId}                            → list[TaskDto]
      GET /api/tasks/user/{userId}?subjectId={subjectId}     → list[TaskDto]
    """

    def __init__(self) -> None:
        self._base_url = settings.task_service_url
        self._timeout = settings.http_timeout

    def _auth_headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def get_tasks(self, user_id: str, token: str) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/api/tasks/user/{user_id}",
                    headers=self._auth_headers(token),
                )
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise ServiceUnavailableError(_SERVICE) from exc
        except httpx.RequestError as exc:
            raise ServiceUnavailableError(_SERVICE) from exc

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def get_tasks_by_subject(
        self, user_id: str, subject_id: str, token: str
    ) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/api/tasks/user/{user_id}",
                    headers=self._auth_headers(token),
                    params={"subjectId": subject_id},
                )
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise ServiceUnavailableError(_SERVICE) from exc
        except httpx.RequestError as exc:
            raise ServiceUnavailableError(_SERVICE) from exc
