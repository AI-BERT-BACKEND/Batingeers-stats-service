from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.entrypoints.advice.exception_handler import register_exception_handlers
from app.entrypoints.rest.controller.dashboard_controller import (
    router as dashboard_router,
)
from app.entrypoints.rest.controller.gamification_controller import (
    router as gamification_router,
)
from app.entrypoints.rest.controller.subject_stats_controller import (
    router as subject_stats_router,
)


@asynccontextmanager
async def lifespan(application: FastAPI):
    from app.infrastructure.db import init_db

    await init_db()
    yield


app = FastAPI(
    title="Stats Service — Batingeers",
    description=(
        "Academic statistics microservice for the **AI.BERT / Batingeers** project.\n\n"
        "### Covered Requirements\n"
        "- **R20**: Academic statistics dashboard\n"
        "- **R21**: Statistics and evolution per subject\n\n"
        "### Integration\n"
        "Consumes **academic-service** (subjects and grades) and **task-service** (tasks) "
        "via HTTP REST calls. The user's JWT token is forwarded to each service.\n\n"
        "### Persistence\n"
        "Results are cached in PostgreSQL. If external services are unavailable, "
        "the last stored snapshot is returned.\n\n"
        "### Authentication\n"
        "All endpoints require a `Bearer` token in the `Authorization` header."
    ),
    version="1.0.0",
    contact={"name": "Batingeers Team", "email": "juandavidvaleroa@gmail.com"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(dashboard_router)
app.include_router(subject_stats_router)
app.include_router(gamification_router)


@app.get("/health", tags=["Health"], summary="Service health check")
async def health_check() -> dict:
    return {"status": "UP", "service": settings.app_name, "version": "1.0.0"}
