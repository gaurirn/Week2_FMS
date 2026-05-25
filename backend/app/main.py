"""
FastAPI Application Entry Point (P2)

Wires together configuration, CORS, exception handlers, routers and
the database initialisation hook. Compared to P1, the analytics +
ETL router is mounted under the same `/api/v1` prefix.

Run locally:
    uvicorn app.main:app --reload
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.middleware.error_handler import register_exception_handlers
from app.routers import feedback_router
from app.routers.analytics_router import router as analytics_router
from app.schemas.feedback_schema import APIResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Application factory (preferred for testability)."""

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ---- CORS --------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # ---- Exception handlers -----------------------------------------
    register_exception_handlers(app)

    # ---- Routers (P1 + P2) ------------------------------------------
    app.include_router(feedback_router, prefix=settings.API_V1_PREFIX)
    app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)

    # ---- Lifecycle hooks --------------------------------------------
    @app.on_event("startup")
    def _on_startup() -> None:
        logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
        init_db()
        logger.info("Database initialised.")

    @app.on_event("shutdown")
    def _on_shutdown() -> None:
        logger.info("Shutting down %s", settings.APP_NAME)

    # ---- Root + health ----------------------------------------------
    @app.get("/", response_model=APIResponse[dict], tags=["Meta"])
    def root() -> APIResponse[dict]:
        return APIResponse[dict](
            message=f"{settings.APP_NAME} API (P2) is running.",
            data={
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "docs": "/docs",
                "api_prefix": settings.API_V1_PREFIX,
            },
        )

    @app.get("/health", response_model=APIResponse[dict], tags=["Meta"])
    def health() -> APIResponse[dict]:
        return APIResponse[dict](message="healthy", data={"status": "ok"})

    return app


app = create_app()
