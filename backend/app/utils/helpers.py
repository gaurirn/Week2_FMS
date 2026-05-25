"""
General Helpers

Small pure functions reused across the codebase. Keep this file free
of any framework imports so it remains trivially unit-testable.
"""

from datetime import datetime
from typing import Any, Dict

from app.core.config import settings


def clamp_page_size(value: int) -> int:
    """Constrain page size to the configured range."""
    if value < 1:
        return settings.DEFAULT_PAGE_SIZE
    return min(value, settings.MAX_PAGE_SIZE)


def to_iso(dt: datetime) -> str:
    """Render a datetime in ISO-8601 with a trailing 'Z' for UTC."""
    return dt.replace(microsecond=0).isoformat() + "Z"


def envelope(
    *,
    success: bool = True,
    message: str = "OK",
    data: Any = None,
) -> Dict[str, Any]:
    """Build the standard API response envelope as a plain dict.

    Useful from exception handlers where a Pydantic generic envelope
    would be cumbersome.
    """
    return {"success": success, "message": message, "data": data}
