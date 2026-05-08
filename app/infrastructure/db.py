from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

_engine = (
    create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
    if settings.database_url
    else None
)

_session_factory: async_sessionmaker | None = (
    async_sessionmaker(_engine, expire_on_commit=False)
    if _engine is not None
    else None
)


async def get_db():
    if _session_factory is None:
        yield None
        return
    async with _session_factory() as session:
        yield session


async def init_db() -> None:
    if _engine is None:
        return
    from app.infrastructure.adapters.persistence.entity.stats_snapshot_entity import Base
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
