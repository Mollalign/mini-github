from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import configure_logging, get_logger
from app.db.session import init_engine, dispose_engine, verify_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Bootstrapping logging MUST run first before initializing any logger instances
    configure_logging()
    logger = get_logger("lifespan")

    logger.info("app.starting")

    try:
        # 2. Instantiate engine state configuration parameters
        init_engine()
        
        # 3. Verify database cluster connectivity asynchronously so the loop isn't blocked
        await verify_db_connection()
        logger.info("database.connection_verified")
        
    except Exception as exc:
        logger.critical("app.startup_failed", error=str(exc))
        raise

    logger.info("app.started")

    try:
        yield
    finally:
        logger.info("app.stopping")

        # 4. Gracefully close down database connection pools cleanly
        try:
            await dispose_engine()
            logger.info("database.connection_pool_disposed")
        except Exception as exc:
            logger.error("database.dispose_failed", error=str(exc))

        logger.info("app.stopped")
