"""
Reusable Validators

These helpers complement Pydantic and are used at the service layer
when validation must consider business rules rather than field shape.
Anything declarative belongs in the Pydantic schemas; this module is
for cross-field or contextual rules.
"""

from typing import Optional

from app.core.constants import MAX_RATING, MIN_RATING


def is_valid_rating(value: Optional[int]) -> bool:
    """Return True if `value` is an int in the allowed rating range."""
    if value is None:
        return False
    return isinstance(value, int) and MIN_RATING <= value <= MAX_RATING


def normalize_keyword(keyword: Optional[str]) -> Optional[str]:
    """Trim whitespace and downcase; return None for blank input."""
    if keyword is None:
        return None
    cleaned = keyword.strip()
    return cleaned.lower() or None


def ensure_positive_int(value: int, *, field_name: str) -> int:
    """Raise ValueError if `value` is not a positive integer."""
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer.")
    return value
