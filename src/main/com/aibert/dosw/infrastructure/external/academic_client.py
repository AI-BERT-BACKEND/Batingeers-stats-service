import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from com.aibert.dosw.config import settings
from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError

_SERVICE = "academic-service"


def _student_headers(user_id: str) -> dict[str, str]:

    return {"X-Student-Id": user_id}


def _normalize_subject(raw: dict) -> dict:
    """Adapts a SubjectResponseDTO (academic-service) to the internal dict shape
    expected by the domain services in stats-service.

    Mapping:
      subjectName       -> name
      evaluationCuts    -> evaluations  (each cut: cutName->name, cutPercentage->weight)
      id (Long/int)     -> id as str    (task-service uses String subjectId)
      code              -> semester     (SubjectResponseDTO has no code field)
      date              -> None         (EvaluationCutResponseDTO has no date field)
    """
    cuts = raw.get("evaluationCuts") or []
    evaluations = [
        {
            "id": str(cut.get("id", "")),
            "name": cut.get("cutName", ""),
            "weight": (cut.get("cutPercentage") or 0) / 100,
            "grade": cut.get("grade"),
            "date": None,
        }
        for cut in cuts
    ]
    return {
        "id": str(raw.get("id", "")),
        "name": raw.get("subjectName", ""),
        "code": raw.get("semester", ""),
        "credits": raw.get("credits", 0),
        "evaluations": evaluations,
        "overallAverage": raw.get("overallAverage"),
        "studentId": raw.get("studentId"),
        "teacherName": raw.get("teacherName"),
        "semester": raw.get("semester", ""),
        "schedule": raw.get("schedule", ""),
    }


class AcademicClient:
    """
    Cliente HTTP para academic-service.
    Equivalente a un @FeignClient en Spring Cloud, pero para Python con httpx.

    Endpoints reales en academic-service:
      GET /api/v1/subjects                  header X-Student-Id  -> ApiResponse<List<SubjectResponseDTO>>
      GET /api/v1/subjects/{subjectId}      header X-Student-Id  -> ApiResponse<SubjectResponseDTO>
    """

    def __init__(self) -> None:
        self._base_url = settings.academic_service_url
        self._timeout = settings.http_timeout

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def get_subjects(self, user_id: str, token: str) -> list[dict]:  # noqa: ARG002
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/api/v1/subjects",
                    headers=_student_headers(user_id),
                )
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                body = response.json()
                raw_list: list[dict] = (
                    body.get("data") if isinstance(body, dict) else body
                )
                return [_normalize_subject(s) for s in (raw_list or [])]
        except httpx.HTTPStatusError as exc:
            raise ServiceUnavailableError(_SERVICE) from exc
        except httpx.RequestError as exc:
            raise ServiceUnavailableError(_SERVICE) from exc

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def get_subject(
        self,
        user_id: str,
        subject_id: str,
        token: str,  # noqa: ARG002
    ) -> dict | None:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/api/v1/subjects/{subject_id}",
                    headers=_student_headers(user_id),
                )
                if response.status_code in (404, 403):
                    return None
                response.raise_for_status()
                body = response.json()
                raw: dict = body.get("data") if isinstance(body, dict) else body
                return _normalize_subject(raw) if raw else None
        except httpx.HTTPStatusError as exc:
            raise ServiceUnavailableError(_SERVICE) from exc
        except httpx.RequestError as exc:
            raise ServiceUnavailableError(_SERVICE) from exc
