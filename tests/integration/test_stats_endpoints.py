from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from com.aibert.dosw.config import settings
from com.aibert.dosw.main import app

_SUBJECTS = [
    {
        "id": "sub-1",
        "name": "Álgebra Lineal",
        "code": "MAT201",
        "credits": 3,
        "evaluations": [
            {
                "id": "e1",
                "name": "Examen 1",
                "weight": 0.5,
                "grade": 4.0,
                "date": "2026-03-01",
            },
            {
                "id": "e2",
                "name": "Examen 2",
                "weight": 0.5,
                "grade": None,
                "date": None,
            },
        ],
    }
]

_TASKS = [
    {"id": "t1", "subject_id": "sub-1", "status": "COMPLETED"},
    {"id": "t2", "subject_id": "sub-1", "status": "TODO"},
]


def _make_token(user_id: str = "user-test-1") -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {_make_token()}"}


# ── Health ─────────────────────────────────────────────────────────────────────


def test_health_check_returns_up(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"


# ── Dashboard (R20) ────────────────────────────────────────────────────────────


@patch(
    "com.aibert.dosw.entrypoints.rest.controller.dashboard_controller.AcademicClient"
)
@patch("com.aibert.dosw.entrypoints.rest.controller.dashboard_controller.TaskClient")
def test_dashboard_returns_200(MockTask, MockAcademic, client, auth_headers):
    MockAcademic.return_value.get_subjects = AsyncMock(return_value=_SUBJECTS)
    MockTask.return_value.get_tasks = AsyncMock(return_value=_TASKS)

    response = client.get("/api/stats/dashboard", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-test-1"
    assert "overall_gpa" in data
    assert "gpa_trend" in data
    assert "subjects" in data
    assert "tasks" in data
    assert data["tasks"]["total"] == 2
    assert data["tasks"]["completed"] == 1


@patch(
    "com.aibert.dosw.entrypoints.rest.controller.dashboard_controller.AcademicClient"
)
@patch("com.aibert.dosw.entrypoints.rest.controller.dashboard_controller.TaskClient")
def test_dashboard_without_token_returns_401(MockTask, MockAcademic, client):
    response = client.get("/api/stats/dashboard")
    assert response.status_code == 401


@patch(
    "com.aibert.dosw.entrypoints.rest.controller.dashboard_controller.AcademicClient"
)
@patch("com.aibert.dosw.entrypoints.rest.controller.dashboard_controller.TaskClient")
def test_dashboard_with_invalid_token_returns_401(MockTask, MockAcademic, client):
    headers = {"Authorization": "Bearer token.invalido.aqui"}
    response = client.get("/api/stats/dashboard", headers=headers)
    assert response.status_code == 401


# ── Subjects stats (R21) ───────────────────────────────────────────────────────


@patch(
    "com.aibert.dosw.entrypoints.rest.controller.subject_stats_controller.AcademicClient"
)
@patch(
    "com.aibert.dosw.entrypoints.rest.controller.subject_stats_controller.TaskClient"
)
def test_get_all_subjects_returns_200(MockTask, MockAcademic, client, auth_headers):
    MockAcademic.return_value.get_subjects = AsyncMock(return_value=_SUBJECTS)
    MockTask.return_value.get_tasks = AsyncMock(return_value=_TASKS)

    response = client.get("/api/stats/subjects", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["subject_id"] == "sub-1"
    assert data[0]["current_average"] == 4.0


@patch(
    "com.aibert.dosw.entrypoints.rest.controller.subject_stats_controller.AcademicClient"
)
@patch(
    "com.aibert.dosw.entrypoints.rest.controller.subject_stats_controller.TaskClient"
)
def test_get_specific_subject_returns_200(MockTask, MockAcademic, client, auth_headers):
    MockAcademic.return_value.get_subject = AsyncMock(return_value=_SUBJECTS[0])
    MockTask.return_value.get_tasks_by_subject = AsyncMock(return_value=_TASKS)

    response = client.get("/api/stats/subjects/sub-1", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["subject_id"] == "sub-1"
    assert "grades_by_period" in data
    assert "minimum_needed" in data
    assert "max_possible_grade" in data
    assert data["status"] in ("passing", "at_risk", "failing")


@patch(
    "com.aibert.dosw.entrypoints.rest.controller.subject_stats_controller.AcademicClient"
)
@patch(
    "com.aibert.dosw.entrypoints.rest.controller.subject_stats_controller.TaskClient"
)
def test_get_nonexistent_subject_returns_404(
    MockTask, MockAcademic, client, auth_headers
):
    MockAcademic.return_value.get_subject = AsyncMock(return_value=None)
    MockTask.return_value.get_tasks_by_subject = AsyncMock(return_value=[])

    response = client.get("/api/stats/subjects/nonexistent", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["error"] == "SUBJECT_NOT_FOUND"
