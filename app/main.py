from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

from app.admin.views import setup_admin
from app.core.config import get_settings
from app.core.logger import setup_logging
from app.database.session import close_db, init_models

setup_logging()
settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting Challenge Omid admin application")
    if settings.auto_create_db:
        await init_models()
    try:
        yield
    finally:
        await close_db()
        logger.info("Stopped Challenge Omid admin application")


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
    )
    application.mount(
        "/admin/static",
        StaticFiles(directory="static"),
        name="static",
    )
    setup_admin(application)

    @application.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/admin/dashboard")

    @application.get("/health", tags=["System"])
    async def health() -> dict[str, bool | str]:
        return {"ok": True, "service": settings.app_name}

    @application.get("/api/health", tags=["System"])
    async def api_health() -> dict[str, bool | str]:
        return {"ok": True, "service": settings.app_name}

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled admin application error", extra={"path": request.url.path})
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return application


app = create_app()
