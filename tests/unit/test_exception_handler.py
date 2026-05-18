"""Tests for FastAPI global exception handlers."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.entrypoints.advice.exception_handler import register_exception_handlers
from app.domain.exceptions.stats_exceptions import (
    ServiceUnavailableError,
    SubjectNotFoundError,
    UnauthorizedError,
)


def _make_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/service-unavailable")
    async def _svc():
        raise ServiceUnavailableError("test-service")

    @app.get("/not-found")
    async def _nf():
        raise SubjectNotFoundError("sub-1")

    @app.get("/unauthorized")
    async def _unauth():
        raise UnauthorizedError()

    @app.get("/runtime-error")
    async def _rt():
        raise RuntimeError("boom")

    @app.get("/generic-error")
    async def _generic():
        raise ValueError("unexpected")

    return app


_client = TestClient(_make_app(), raise_server_exceptions=False)


def test_service_unavailable_returns_503():
    response = _client.get("/service-unavailable")
    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "SERVICE_UNAVAILABLE"
    assert "test-service" in body["message"]


def test_subject_not_found_returns_404():
    response = _client.get("/not-found")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "SUBJECT_NOT_FOUND"
    assert "sub-1" in body["message"]


def test_unauthorized_returns_403():
    response = _client.get("/unauthorized")
    assert response.status_code == 403
    body = response.json()
    assert body["error"] == "FORBIDDEN"


def test_runtime_error_returns_500():
    response = _client.get("/runtime-error")
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "INTERNAL_SERVER_ERROR"
    assert "unexpected error" in body["message"].lower()


def test_generic_exception_returns_500():
    response = _client.get("/generic-error")
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "INTERNAL_SERVER_ERROR"
