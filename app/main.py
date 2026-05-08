from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.entrypoints.advice.exception_handler import register_exception_handlers
from app.entrypoints.rest.controller.dashboard_controller import router as dashboard_router
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
        "Microservicio de estadísticas académicas del proyecto **AI.BERT / Batingeers**.\n\n"
        "### Requerimientos cubiertos\n"
        "- **R20**: Dashboard de estadísticas académicas\n"
        "- **R21**: Estadísticas y evolución por materia\n\n"
        "### Integración\n"
        "Consume **academic-service** (materias y notas) y **task-service** (tareas) "
        "mediante llamadas HTTP REST. El token JWT del usuario se reenvía a cada servicio.\n\n"
        "### Persistencia\n"
        "Los resultados se cachean en PostgreSQL. Si los servicios externos no están disponibles, "
        "se retorna el último snapshot almacenado.\n\n"
        "### Autenticación\n"
        "Todos los endpoints requieren un token `Bearer` en el header `Authorization`."
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


@app.get("/health", tags=["Health"], summary="Health check del servicio")
async def health_check() -> dict:
    return {"status": "UP", "service": settings.app_name, "version": "1.0.0"}
