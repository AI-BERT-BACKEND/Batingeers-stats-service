import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from com.aibert.dosw.config import settings
from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError

_SERVICE = "task-service"


def _user_headers(user_id: str) -> dict[str, str]:
    return {"X-User-Id": user_id}


def _normalize_task(raw: dict) -> dict:
    """Adapts a TaskResponse (task-service) to the internal dict shape
    expected by the domain services in stats-service.

    Mapping:
      subjectId  (camelCase String) -> subject_id  (snake_case)
      deadline   (LocalDateTime)    -> dueDate / due_date
    """
    due = raw.get("deadline") or raw.get("dueDate") or raw.get("due_date")
    return {
        **raw,
        "subject_id": raw.get("subjectId") or raw.get("subject_id", ""),
        "dueDate": due,
        "due_date": due,
    }


class TaskClient:
    """
    Cliente HTTP para task-service.
    Equivalente a un @FeignClient en Spring Cloud, pero para Python con httpx.

    Endpoints reales en task-service:
      GET /api/tasks/student/{studentId}         header X-User-Id  -> List<TaskResponse>
      GET /api/tasks?view=calendar&subjectId={}  header X-User-Id  -> List<TaskResponse>
    """

    def __init__(self) -> None:
        self._base_url = settings.task_service_url
        self._timeout = settings.http_timeout

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def get_tasks(self, user_id: str, token: str) -> list[dict]:  # noqa: ARG002
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/api/tasks/student/{user_id}",
                    headers=_user_headers(user_id),
                )
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                return [_normalize_task(t) for t in (response.json() or [])]
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
        self, user_id: str, subject_id: str, token: str  # noqa: ARG002
    ) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/api/tasks",
                    headers=_user_headers(user_id),
                    params={"view": "calendar", "subjectId": subject_id},
                )
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                return [_normalize_task(t) for t in (response.json() or [])]
        except httpx.HTTPStatusError as exc:
            raise ServiceUnavailableError(_SERVICE) from exc
        except httpx.RequestError as exc:
            raise ServiceUnavailableError(_SERVICE) from exc
