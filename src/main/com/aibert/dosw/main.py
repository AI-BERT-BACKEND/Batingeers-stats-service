from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from com.aibert.dosw.config import settings
from com.aibert.dosw.entrypoints.advice.exception_handler import register_exception_handlers
from com.aibert.dosw.entrypoints.rest.controller.dashboard_controller import (
    router as dashboard_router,
)
from com.aibert.dosw.entrypoints.rest.controller.gamification_controller import (
    router as gamification_router,
)
from com.aibert.dosw.entrypoints.rest.controller.subject_stats_controller import (
    router as subject_stats_router,
)


@asynccontextmanager
async def lifespan(application: FastAPI):
    from com.aibert.dosw.infrastructure.db import init_db
    from com.aibert.dosw.infrastructure.messaging.kafka_producer import (
        start_producer,
        stop_producer,
    )

    await init_db()
    await start_producer()
    yield
    await stop_producer()


app = FastAPI(
    title="Batingeers Stats Service",
    description=(
        "Academic statistics microservice for the **AI.BERT / Batingeers** platform.\n\n"
        "---\n\n"
        "### What this service does\n"
        "Aggregates academic data from **academic-service** (subjects, grades, evaluation "
        "periods) and **task-service** (tasks, completion status) to compute rich analytics "
        "for each student. Results are cached in PostgreSQL so that a snapshot is always "
        "available even when upstream services are temporarily unreachable.\n\n"
        "### Covered requirements\n"
        "| Requirement | Endpoint | Description |\n"
        "|---|---|---|\n"
        "| R20 | `GET /api/stats/dashboard` | Overall academic dashboard — GPA, "
        "task summary, and subject list |\n"
        "| R21 | `GET /api/stats/subjects/{id}` | Per-subject analytics — grade history, "
        "projections, task metrics, and weekly chart |\n"
        "| R24 | `GET /api/stats/gamification` | Gamification profile — points, "
        "levels, badges, and progress toward next level |\n\n"
        "### Event publishing (Kafka)\n"
        "The service publishes domain events to the notification microservice via Kafka "
        "when academically relevant conditions are detected:\n\n"
        "| Topic | Trigger |\n"
        "|---|---|\n"
        "| `stats.academic-performance-alert` | One or more subjects are at risk or failing |\n"
        "| `stats.academic-overload-alert` | Declining GPA trend combined with overdue tasks |\n"
        "| `stats.study-suggestion` | A subject's grade trend is declining |\n\n"
        "Kafka is optional — if `KAFKA_BOOTSTRAP_SERVERS` is not configured, events are "
        "silently skipped and all endpoints remain fully operational.\n\n"
        "### Authentication\n"
        "Every endpoint requires a valid `Bearer` JWT token in the `Authorization` header. "
        "The `userId` is extracted from the token's `sub` claim — no path or body parameter needed.\n\n"
        "### Error reference\n"
        "| HTTP | Code | Meaning |\n"
        "|---|---|---|\n"
        "| 401 | — | Invalid or expired JWT |\n"
        "| 403 | FORBIDDEN | Missing Authorization header |\n"
        "| 404 | SUBJECT_NOT_FOUND | Subject does not exist |\n"
        "| 503 | SERVICE_UNAVAILABLE | Upstream service unreachable and no cached snapshot |\n"
        "| 500 | INTERNAL_SERVER_ERROR | Unexpected server error |"
    ),
    version="1.0.0",
    contact={"name": "Batingeers Team", "email": "juandavidvaleroa@gmail.com"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
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
