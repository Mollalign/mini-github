from __future__ import annotations

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def init_engine() -> AsyncEngine:
    """Initialize the global async SQLAlchemy engine and sessionmaker."""
    global _engine, _sessionmaker

    if _engine is not None:
        return _engine

    settings = get_settings()

    _engine = create_async_engine(
        settings.database_url,
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_pre_ping=True,
    )

    _sessionmaker = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    logger.info("db.engine_initialized")

    return _engine


async def verify_db_connection() -> None:
    """Verify that the database engine can successfully establish a network connection."""
    engine = get_engine()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("db.connection_verified")
    except Exception as exc:
        logger.critical("db.connection_verification_failed", error=str(exc))
        raise RuntimeError("Database connection verification failed during startup.") from exc


async def dispose_engine() -> None:
    """Dispose the database engine and release all connections."""
    global _engine, _sessionmaker

    if _engine is not None:
        await _engine.dispose()
        logger.info("db.engine_disposed")

    _engine = None
    _sessionmaker = None


def get_engine() -> AsyncEngine:
    """Return the initialized database engine."""
    if _engine is None:
        raise RuntimeError(
            "Database engine is not initialized. "
            "Call init_engine() during application startup."
        )

    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Return the initialized session factory."""
    if _sessionmaker is None:
        raise RuntimeError(
            "Database sessionmaker is not initialized. "
            "Call init_engine() during application startup."
        )

    return _sessionmaker


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session for workers, scripts, and background tasks.

    Commits when the operation succeeds.
    Rolls back when an exception occurs.
    """
    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncIterator[AsyncSession]:
    """
    FastAPI database dependency.

    This dependency does not automatically commit.
    Services are responsible for committing successful transactions.
    """
    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
