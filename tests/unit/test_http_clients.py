"""Tests for AcademicClient and TaskClient HTTP adapters."""

import pytest
import respx
import httpx
from unittest.mock import patch, AsyncMock

from com.aibert.dosw.infrastructure.external.academic_client import AcademicClient
from com.aibert.dosw.infrastructure.external.task_client import TaskClient
from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def academic_client():
    with patch("com.aibert.dosw.infrastructure.external.academic_client.settings") as s:
        s.academic_service_url = "http://academic"
        s.http_timeout = 5.0
        yield AcademicClient()


@pytest.fixture
def task_client():
    with patch("com.aibert.dosw.infrastructure.external.task_client.settings") as s:
        s.task_service_url = "http://tasks"
        s.http_timeout = 5.0
        yield TaskClient()


# ── AcademicClient.get_subjects ───────────────────────────────────────────────


async def test_get_subjects_success(academic_client):
    raw = [
        {
            "id": 1,
            "subjectName": "Math",
            "evaluationCuts": [],
            "credits": 4,
            "semester": "2026-1",
        }
    ]
    with respx.mock:
        respx.get("http://academic/api/v1/subjects").mock(
            return_value=httpx.Response(200, json={"data": raw})
        )
        result = await academic_client.get_subjects("u1", "tok")
    assert len(result) == 1
    assert result[0]["id"] == "1"
    assert result[0]["name"] == "Math"


async def test_get_subjects_sends_student_id_header(academic_client):
    with respx.mock:
        route = respx.get("http://academic/api/v1/subjects").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        await academic_client.get_subjects("u1", "my-token")
        assert route.calls[0].request.headers["x-student-id"] == "u1"


async def test_get_subjects_404_returns_empty_list(academic_client):
    with respx.mock:
        respx.get("http://academic/api/v1/subjects").mock(
            return_value=httpx.Response(404)
        )
        result = await academic_client.get_subjects("u1", "tok")
    assert result == []


async def test_get_subjects_server_error_raises_service_unavailable(academic_client):
    with respx.mock, patch("asyncio.sleep", new_callable=AsyncMock):
        respx.get("http://academic/api/v1/subjects").mock(
            return_value=httpx.Response(500)
        )
        with pytest.raises(ServiceUnavailableError):
            await academic_client.get_subjects("u1", "tok")


async def test_get_subjects_connection_error_raises_service_unavailable(
    academic_client,
):
    with respx.mock, patch("asyncio.sleep", new_callable=AsyncMock):
        respx.get("http://academic/api/v1/subjects").mock(
            side_effect=httpx.ConnectError("refused")
        )
        with pytest.raises(ServiceUnavailableError):
            await academic_client.get_subjects("u1", "tok")


# ── AcademicClient.get_subject ────────────────────────────────────────────────


async def test_get_subject_success(academic_client):
    raw = {"id": 1, "subjectName": "Math", "evaluationCuts": [], "credits": 4}
    with respx.mock:
        respx.get("http://academic/api/v1/subjects/s1").mock(
            return_value=httpx.Response(200, json={"data": raw})
        )
        result = await academic_client.get_subject("u1", "s1", "tok")
    assert result is not None
    assert result["id"] == "1"
    assert result["name"] == "Math"


async def test_get_subject_404_returns_none(academic_client):
    with respx.mock:
        respx.get("http://academic/api/v1/subjects/s1").mock(
            return_value=httpx.Response(404)
        )
        result = await academic_client.get_subject("u1", "s1", "tok")
    assert result is None


async def test_get_subject_server_error_raises_service_unavailable(academic_client):
    with respx.mock, patch("asyncio.sleep", new_callable=AsyncMock):
        respx.get("http://academic/api/v1/subjects/s1").mock(
            return_value=httpx.Response(503)
        )
        with pytest.raises(ServiceUnavailableError):
            await academic_client.get_subject("u1", "s1", "tok")


async def test_get_subject_connection_error_raises_service_unavailable(academic_client):
    with respx.mock, patch("asyncio.sleep", new_callable=AsyncMock):
        respx.get("http://academic/api/v1/subjects/s1").mock(
            side_effect=httpx.ConnectError("refused")
        )
        with pytest.raises(ServiceUnavailableError):
            await academic_client.get_subject("u1", "s1", "tok")


# ── TaskClient.get_tasks ──────────────────────────────────────────────────────


async def test_get_tasks_success(task_client):
    raw = [{"id": "t1", "status": "COMPLETED", "subjectId": "s1"}]
    with respx.mock:
        respx.get("http://tasks/api/tasks/student/u1").mock(
            return_value=httpx.Response(200, json=raw)
        )
        result = await task_client.get_tasks("u1", "tok")
    assert len(result) == 1
    assert result[0]["id"] == "t1"
    assert result[0]["subject_id"] == "s1"


async def test_get_tasks_sends_user_id_header(task_client):
    with respx.mock:
        route = respx.get("http://tasks/api/tasks/student/u1").mock(
            return_value=httpx.Response(200, json=[])
        )
        await task_client.get_tasks("u1", "my-token")
        assert route.calls[0].request.headers["x-user-id"] == "u1"


async def test_get_tasks_404_returns_empty(task_client):
    with respx.mock:
        respx.get("http://tasks/api/tasks/student/u1").mock(
            return_value=httpx.Response(404)
        )
        result = await task_client.get_tasks("u1", "tok")
    assert result == []


async def test_get_tasks_server_error_raises_service_unavailable(task_client):
    with respx.mock, patch("asyncio.sleep", new_callable=AsyncMock):
        respx.get("http://tasks/api/tasks/student/u1").mock(
            return_value=httpx.Response(500)
        )
        with pytest.raises(ServiceUnavailableError):
            await task_client.get_tasks("u1", "tok")


async def test_get_tasks_connection_error_raises_service_unavailable(task_client):
    with respx.mock, patch("asyncio.sleep", new_callable=AsyncMock):
        respx.get("http://tasks/api/tasks/student/u1").mock(
            side_effect=httpx.ConnectError("refused")
        )
        with pytest.raises(ServiceUnavailableError):
            await task_client.get_tasks("u1", "tok")


# ── TaskClient.get_tasks_by_subject ──────────────────────────────────────────


async def test_get_tasks_by_subject_success(task_client):
    raw = [{"id": "t1", "subjectId": "s1", "status": "COMPLETED"}]
    with respx.mock:
        respx.get(
            "http://tasks/api/tasks", params={"view": "calendar", "subjectId": "s1"}
        ).mock(return_value=httpx.Response(200, json=raw))
        result = await task_client.get_tasks_by_subject("u1", "s1", "tok")
    assert len(result) == 1
    assert result[0]["id"] == "t1"
    assert result[0]["subject_id"] == "s1"


async def test_get_tasks_by_subject_404_returns_empty(task_client):
    with respx.mock:
        respx.get(
            "http://tasks/api/tasks", params={"view": "calendar", "subjectId": "s1"}
        ).mock(return_value=httpx.Response(404))
        result = await task_client.get_tasks_by_subject("u1", "s1", "tok")
    assert result == []


async def test_get_tasks_by_subject_server_error_raises(task_client):
    with respx.mock, patch("asyncio.sleep", new_callable=AsyncMock):
        respx.get(
            "http://tasks/api/tasks", params={"view": "calendar", "subjectId": "s1"}
        ).mock(return_value=httpx.Response(500))
        with pytest.raises(ServiceUnavailableError):
            await task_client.get_tasks_by_subject("u1", "s1", "tok")


async def test_get_tasks_by_subject_connection_error_raises(task_client):
    with respx.mock, patch("asyncio.sleep", new_callable=AsyncMock):
        respx.get(
            "http://tasks/api/tasks", params={"view": "calendar", "subjectId": "s1"}
        ).mock(side_effect=httpx.ConnectError("refused"))
        with pytest.raises(ServiceUnavailableError):
            await task_client.get_tasks_by_subject("u1", "s1", "tok")
