"""
Centralized Exception Handling

Wires up global handlers so every error response follows the
`APIResponse` envelope shape: { success, message, data }.
"""

import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.constants import Messages
from app.utils.helpers import envelope

logger = logging.getLogger(__name__)


def _json(
    status_code: int,
    message: str,
    data: Any = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=envelope(success=False, message=message, data=data),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the standard set of exception handlers to `app`."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        # Re-wrap FastAPI's default response into the API envelope.
        return _json(
            status_code=exc.status_code,
            message=str(exc.detail) if exc.detail else "HTTP error",
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Compact the verbose Pydantic errors into something a UI can render.
        errors: list[Dict[str, Any]] = []
        for err in exc.errors():
            loc = ".".join(str(p) for p in err.get("loc", []) if p != "body")
            errors.append(
                {
                    "field": loc or "body",
                    "message": err.get("msg", "Invalid value"),
                    "type": err.get("type", "value_error"),
                }
            )
        return _json(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=Messages.VALIDATION_ERROR,
            data={"errors": errors},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.exception("Database error while handling %s", request.url.path)
        return _json(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=Messages.DATABASE_ERROR,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled error while handling %s", request.url.path)
        return _json(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=Messages.INTERNAL_ERROR,
        )
