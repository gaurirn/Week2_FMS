"""
Application Constants

Holds all magic numbers, magic strings and lookup tables used across
the codebase. Keeping them centralised here means changes propagate
everywhere automatically and the rest of the code stays declarative.
"""

from enum import IntEnum


# ---- Rating ----------------------------------------------------------
class Rating(IntEnum):
    """Allowed rating values."""

    POOR = 1
    FAIR = 2
    GOOD = 3
    VERY_GOOD = 4
    EXCELLENT = 5


RATING_LABELS = {
    Rating.POOR: "Poor",
    Rating.FAIR: "Fair",
    Rating.GOOD: "Good",
    Rating.VERY_GOOD: "Very Good",
    Rating.EXCELLENT: "Excellent",
}

MIN_RATING = Rating.POOR.value
MAX_RATING = Rating.EXCELLENT.value


# ---- Field length limits --------------------------------------------
PARTICIPANT_NAME_MIN_LEN = 2
PARTICIPANT_NAME_MAX_LEN = 120
PROGRAM_NAME_MIN_LEN = 2
PROGRAM_NAME_MAX_LEN = 150
COMMENTS_MIN_LEN = 3
COMMENTS_MAX_LEN = 2000


# ---- API response messages -----------------------------------------
class Messages:
    FEEDBACK_CREATED = "Feedback submitted successfully."
    FEEDBACK_UPDATED = "Feedback updated successfully."
    FEEDBACK_DELETED = "Feedback deleted successfully."
    FEEDBACK_NOT_FOUND = "Feedback with id={feedback_id} was not found."
    VALIDATION_ERROR = "One or more fields failed validation."
    DATABASE_ERROR = "An unexpected database error occurred."
    INTERNAL_ERROR = "An unexpected error occurred. Please try again later."
