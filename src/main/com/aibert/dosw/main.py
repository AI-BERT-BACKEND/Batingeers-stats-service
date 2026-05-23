from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from com.aibert.dosw.config import settings
from com.aibert.dosw.entrypoints.advice.exception_handler import (
    register_exception_handlers,
)
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


_OPENAPI_TAGS = [
    {
        "name": "Dashboard",
        "description": (
            "Manage the academic dashboard: retrieve overall GPA, subject summaries, "
            "task metrics, and GPA trend for the authenticated student. (R20)"
        ),
    },
    {
        "name": "Subject Statistics",
        "description": (
            "Manage subject-level analytics: retrieve grade history by evaluation period, "
            "grade projections, evolution charts, and related task metrics per subject. (R21)"
        ),
    },
    {
        "name": "Gamification",
        "description": (
            "Manage the gamification profile: retrieve total points, current level, "
            "badge unlock status, and progress toward the next level. (R24)"
        ),
    },
    {
        "name": "Health",
        "description": "Internal health check endpoint for load balancers and monitoring tools.",
    },
]

app = FastAPI(
    title="Stats Service API — AIBERT",
    description=(
        "Aggregates academic data from **academic-service** and **task-service** to compute "
        "rich analytics for each student, with PostgreSQL caching for resilience.\n\n"
        "**Key responsibilities:**\n"
        "- Compute overall GPA, GPA trend, subject status breakdown, and task metrics "
        "for the student dashboard (R20)\n"
        "- Calculate per-subject grade projections, maximum possible grade, minimum passing "
        "grade, weekly evolution chart, and related task metrics (R21)\n"
        "- Build the gamification profile: total points, current level (1–4), badge unlock "
        "status, and progress toward the next level from task history (R24)\n\n"
        "**Kafka topics published:**\n"
        "| Topic | Trigger |\n"
        "|---|---|\n"
        "| `stats.academic-performance-alert` | One or more subjects are at risk or failing |\n"
        "| `stats.academic-overload-alert` | Declining GPA trend combined with overdue tasks |\n"
        "| `stats.study-suggestion` | A subject's grade trend is declining |\n\n"
        "Kafka is optional — if `KAFKA_BOOTSTRAP_SERVERS` is not configured, events are "
        "silently skipped and all endpoints remain fully operational.\n\n"
        "Authentication: all endpoints require a Bearer JWT token issued by the auth service. "
        "Use the Authorize button to set your token.\n\n"
        "Local testing: see `swagger-tests/swagger-tests-guide.md` in the repository for "
        "ready-to-paste curl commands and a JWT token generation guide.\n\n"
        "Contact Batingeers Team"
    ),
    version="1.0.0",
    contact={"name": "Batingeers Team", "email": "juandavidvaleroa@gmail.com"},
    license_info={"name": "MIT"},
    openapi_tags=_OPENAPI_TAGS,
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


def _custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=_OPENAPI_TAGS,
    )
    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "JWT Bearer token issued by the auth service. "
                "The `userId` is extracted from the `sub` claim automatically."
            ),
        }
    }
    schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = _custom_openapi  # type: ignore[method-assign]


@app.get(
    "/health",
    tags=["Health"],
    summary="Service health check",
    responses={
        200: {"description": "Service is running normally"},
        503: {"description": "Service is unavailable or starting up"},
    },
)
async def health_check() -> dict:
    return {"status": "UP", "service": settings.app_name, "version": "1.0.0"}
