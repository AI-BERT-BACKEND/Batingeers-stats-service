"""
Integration tests using httpx.AsyncClient + asyncio.run().
Running inside asyncio.run() keeps all code in the main thread so coverage tracks it.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import httpx
from jose import jwt

from com.aibert.dosw.config import settings

# ── helpers ───────────────────────────────────────────────────────────────────


def _make_token(user_id: str = "user-test") -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _auth(user_id="user-test") -> dict:
    return {"Authorization": f"Bearer {_make_token(user_id)}"}


_SUBJECTS = [
    {
        "id": "sub-1",
        "name": "Álgebra",
        "code": "MAT201",
        "credits": 3,
        "evaluations": [
            {
                "id": "e1",
                "name": "Examen",
                "weight": 1.0,
                "grade": 4.0,
                "date": "2026-03-01",
            },
        ],
    }
]

_TASKS = [
    {"id": "t1", "subject_id": "sub-1", "status": "COMPLETED"},
    {"id": "t2", "subject_id": "sub-1", "status": "PENDING"},
]

_GAMIFICATION_TASKS = [
    {
        "id": "t1",
        "status": "COMPLETED",
        "completedAt": "2026-03-15",
        "dueDate": "2026-03-15",
    },
]


def _run(coro):
    """Run an async coroutine from a sync test so coverage tracks all code."""
    return asyncio.run(coro)


# ── Health ─────────────────────────────────────────────────────────────────────


def test_health_sync():
    from com.aibert.dosw.main import app

    async def _call():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get("/health")

    response = _run(_call())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"


# ── Dashboard (R20) ────────────────────────────────────────────────────────────


def test_dashboard_sync_returns_200():
    from com.aibert.dosw.main import app

    async def _call():
        with (
            patch(
                "app.entrypoints.rest.controller.dashboard_controller.AcademicClient"
            ) as MockAcademic,
            patch(
                "app.entrypoints.rest.controller.dashboard_controller.TaskClient"
            ) as MockTask,
        ):
            MockAcademic.return_value.get_subjects = AsyncMock(return_value=_SUBJECTS)
            MockTask.return_value.get_tasks = AsyncMock(return_value=_TASKS)
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                return await client.get("/api/stats/dashboard", headers=_auth())

    response = _run(_call())
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-test"
    assert "overall_gpa" in data
    assert "subjects" in data
    assert "tasks" in data


def test_dashboard_sync_no_token_returns_403():
    from com.aibert.dosw.main import app

    async def _call():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get("/api/stats/dashboard")

    response = _run(_call())
    assert response.status_code == 403


def test_dashboard_sync_invalid_token_returns_401():
    from com.aibert.dosw.main import app

    async def _call():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get(
                "/api/stats/dashboard",
                headers={"Authorization": "Bearer invalid.token.here"},
            )

    response = _run(_call())
    assert response.status_code == 401


# ── Subjects (R21) ─────────────────────────────────────────────────────────────


def test_subjects_sync_returns_200():
    from com.aibert.dosw.main import app

    async def _call():
        with (
            patch(
                "app.entrypoints.rest.controller.subject_stats_controller.AcademicClient"
            ) as MockAcademic,
            patch(
                "app.entrypoints.rest.controller.subject_stats_controller.TaskClient"
            ) as MockTask,
        ):
            MockAcademic.return_value.get_subjects = AsyncMock(return_value=_SUBJECTS)
            MockTask.return_value.get_tasks = AsyncMock(return_value=_TASKS)
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                return await client.get("/api/stats/subjects", headers=_auth())

    response = _run(_call())
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["subject_id"] == "sub-1"


def test_subject_specific_sync_returns_200():
    from com.aibert.dosw.main import app

    async def _call():
        with (
            patch(
                "app.entrypoints.rest.controller.subject_stats_controller.AcademicClient"
            ) as MockAcademic,
            patch(
                "app.entrypoints.rest.controller.subject_stats_controller.TaskClient"
            ) as MockTask,
        ):
            MockAcademic.return_value.get_subject = AsyncMock(return_value=_SUBJECTS[0])
            MockTask.return_value.get_tasks_by_subject = AsyncMock(return_value=_TASKS)
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                return await client.get("/api/stats/subjects/sub-1", headers=_auth())

    response = _run(_call())
    assert response.status_code == 200
    data = response.json()
    assert data["subject_id"] == "sub-1"
    assert "grades_by_period" in data
    assert "grade_evolution" in data


def test_subject_not_found_sync_returns_404():
    from com.aibert.dosw.main import app

    async def _call():
        with (
            patch(
                "app.entrypoints.rest.controller.subject_stats_controller.AcademicClient"
            ) as MockAcademic,
            patch(
                "app.entrypoints.rest.controller.subject_stats_controller.TaskClient"
            ) as MockTask,
        ):
            MockAcademic.return_value.get_subject = AsyncMock(return_value=None)
            MockTask.return_value.get_tasks_by_subject = AsyncMock(return_value=[])
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                return await client.get(
                    "/api/stats/subjects/nonexistent", headers=_auth()
                )

    response = _run(_call())
    assert response.status_code == 404
    assert response.json()["error"] == "SUBJECT_NOT_FOUND"


# ── Gamification (R24) ─────────────────────────────────────────────────────────


def test_gamification_sync_returns_200():
    from com.aibert.dosw.main import app

    async def _call():
        with patch(
            "app.entrypoints.rest.controller.gamification_controller.TaskClient"
        ) as MockTask:
            MockTask.return_value.get_tasks = AsyncMock(
                return_value=_GAMIFICATION_TASKS
            )
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                return await client.get("/api/stats/gamification", headers=_auth())

    response = _run(_call())
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-test"
    assert "total_points" in data
    assert "current_level" in data
    assert "badges" in data
    assert "progress_to_next" in data
    assert data["total_points"] == 10
    assert len(data["badges"]) == 4
    assert all("badge_name" in b for b in data["badges"])
    assert all("unlocked" in b for b in data["badges"])


def test_gamification_no_token_returns_403():
    from com.aibert.dosw.main import app

    async def _call():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get("/api/stats/gamification")

    response = _run(_call())
    assert response.status_code == 403


def test_gamification_empty_tasks_returns_level_1():
    from com.aibert.dosw.main import app

    async def _call():
        with patch(
            "app.entrypoints.rest.controller.gamification_controller.TaskClient"
        ) as MockTask:
            MockTask.return_value.get_tasks = AsyncMock(return_value=[])
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                return await client.get("/api/stats/gamification", headers=_auth())

    response = _run(_call())
    assert response.status_code == 200
    data = response.json()
    assert data["total_points"] == 0
    assert data["current_level"] == 1
    assert len(data["badges"]) == 4
    assert all(not b["unlocked"] for b in data["badges"])


# ── Exception handlers ─────────────────────────────────────────────────────────


def test_service_unavailable_returns_503():
    from com.aibert.dosw.main import app
    from com.aibert.dosw.domain.exceptions.stats_exceptions import ServiceUnavailableError

    async def _call():
        with (
            patch(
                "app.entrypoints.rest.controller.dashboard_controller.AcademicClient"
            ) as MockAcademic,
            patch(
                "app.entrypoints.rest.controller.dashboard_controller.TaskClient"
            ) as MockTask,
        ):
            MockAcademic.return_value.get_subjects = AsyncMock(
                side_effect=ServiceUnavailableError("academic")
            )
            MockTask.return_value.get_tasks = AsyncMock(return_value=[])
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                return await client.get("/api/stats/dashboard", headers=_auth())

    response = _run(_call())
    assert response.status_code == 503
    assert response.json()["error"] == "SERVICE_UNAVAILABLE"


def test_generic_exception_returns_500():
    from com.aibert.dosw.main import app

    async def _call():
        with (
            patch(
                "app.entrypoints.rest.controller.dashboard_controller.AcademicClient"
            ) as MockAcademic,
            patch(
                "app.entrypoints.rest.controller.dashboard_controller.TaskClient"
            ) as MockTask,
        ):
            MockAcademic.return_value.get_subjects = AsyncMock(
                side_effect=RuntimeError("unexpected")
            )
            MockTask.return_value.get_tasks = AsyncMock(return_value=[])
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                return await client.get("/api/stats/dashboard", headers=_auth())

    response = _run(_call())
    assert response.status_code == 500
    assert response.json()["error"] == "INTERNAL_SERVER_ERROR"
