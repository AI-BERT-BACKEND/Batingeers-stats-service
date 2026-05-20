from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from com.aibert.dosw.domain.exceptions.stats_exceptions import (
    ServiceUnavailableError,
    SubjectNotFoundError,
    UnauthorizedError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ServiceUnavailableError)
    async def handle_service_unavailable(
        request: Request, exc: ServiceUnavailableError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"error": "SERVICE_UNAVAILABLE", "message": str(exc)},
        )

    @app.exception_handler(SubjectNotFoundError)
    async def handle_subject_not_found(
        request: Request, exc: SubjectNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": "SUBJECT_NOT_FOUND", "message": str(exc)},
        )

    @app.exception_handler(UnauthorizedError)
    async def handle_unauthorized(
        request: Request, exc: UnauthorizedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"error": "FORBIDDEN", "message": str(exc)},
        )

    @app.exception_handler(RuntimeError)
    async def handle_runtime_error(request: Request, exc: RuntimeError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred on the server",
            },
        )

    @app.exception_handler(Exception)
    async def handle_generic(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred on the server",
            },
        )
