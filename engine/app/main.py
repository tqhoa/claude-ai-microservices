import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from sqlalchemy import text

from app.config import get_settings
from app.database import async_session, dispose_engine, init_database
from app.exceptions import register_exception_handlers
from app.logging import setup_logging
from app.models import *  # noqa: F401,F403 — ensure all models registered before create_all

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(log_level=settings.log_level, json_output=not settings.debug)
    await init_database()
    logger.info("application_started", app=settings.app_name, version=settings.app_version)
    yield
    await dispose_engine()
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    from app.api.v1 import api_router

    app.include_router(api_router)

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next: object) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        response: Response = await call_next(request)  # type: ignore[misc]
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "request_completed",
            method=request.method,
            path=str(request.url.path),
            status=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        return response

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {
            "status": "healthy",
            "service": "engine",
            "version": settings.app_version,
        }

    @app.get("/ready")
    async def ready() -> Response:
        from fastapi.responses import JSONResponse

        try:
            async with async_session() as session:
                await session.execute(text("SELECT 1"))
            return JSONResponse(
                status_code=200,
                content={"status": "ready", "database": "connected"},
            )
        except Exception:
            logger.error("readiness_check_failed")
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "database": "disconnected"},
            )

    return app


app = create_app()
