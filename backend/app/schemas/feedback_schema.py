"""
Pydantic Schemas for Feedback

These DTOs define the public contract of the API:
  * `FeedbackCreate` -> validated request body for POST
  * `FeedbackUpdate` -> validated request body for PUT (partial updates)
  * `FeedbackResponse` -> outbound representation of a feedback record
  * `FeedbackListResponse` -> paginated list wrapper
  * `FeedbackStats` -> aggregated statistics used by the dashboard
  * `APIResponse` -> generic envelope used by all endpoints
"""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import (
    COMMENTS_MAX_LEN,
    COMMENTS_MIN_LEN,
    MAX_RATING,
    MIN_RATING,
    PARTICIPANT_NAME_MAX_LEN,
    PARTICIPANT_NAME_MIN_LEN,
    PROGRAM_NAME_MAX_LEN,
    PROGRAM_NAME_MIN_LEN,
    RATING_LABELS,
)


# ----------------------------------------------------------------------
# Base / shared schemas
# ----------------------------------------------------------------------
class FeedbackBase(BaseModel):
    """Fields shared between create and update payloads."""

    participant_name: str = Field(
        ...,
        min_length=PARTICIPANT_NAME_MIN_LEN,
        max_length=PARTICIPANT_NAME_MAX_LEN,
        description="Full name of the person submitting feedback.",
        examples=["Jane Doe"],
    )
    program_name: str = Field(
        ...,
        min_length=PROGRAM_NAME_MIN_LEN,
        max_length=PROGRAM_NAME_MAX_LEN,
        description="Program, event or product being rated.",
        examples=["AI Bootcamp 2026"],
    )
    rating: int = Field(
        ...,
        ge=MIN_RATING,
        le=MAX_RATING,
        description=f"Integer rating between {MIN_RATING} and {MAX_RATING}.",
        examples=[5],
    )
    comments: str = Field(
        ...,
        min_length=COMMENTS_MIN_LEN,
        max_length=COMMENTS_MAX_LEN,
        description="Free-form feedback text.",
        examples=["The sessions were extremely insightful and well structured."],
    )

    # -- strip surrounding whitespace from string fields ---------------
    @field_validator("participant_name", "program_name", "comments")
    @classmethod
    def _strip_strings(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


# ----------------------------------------------------------------------
# Create
# ----------------------------------------------------------------------
class FeedbackCreate(FeedbackBase):
    """Request body for POST /feedback."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "participant_name": "Jane Doe",
                "program_name": "AI Bootcamp 2026",
                "rating": 5,
                "comments": "Excellent program with great mentors.",
            }
        }
    )


# ----------------------------------------------------------------------
# Update (partial)
# ----------------------------------------------------------------------
class FeedbackUpdate(BaseModel):
    """Request body for PUT /feedback/{id}. All fields optional."""

    participant_name: Optional[str] = Field(
        default=None,
        min_length=PARTICIPANT_NAME_MIN_LEN,
        max_length=PARTICIPANT_NAME_MAX_LEN,
    )
    program_name: Optional[str] = Field(
        default=None,
        min_length=PROGRAM_NAME_MIN_LEN,
        max_length=PROGRAM_NAME_MAX_LEN,
    )
    rating: Optional[int] = Field(
        default=None, ge=MIN_RATING, le=MAX_RATING
    )
    comments: Optional[str] = Field(
        default=None,
        min_length=COMMENTS_MIN_LEN,
        max_length=COMMENTS_MAX_LEN,
    )

    @field_validator("participant_name", "program_name", "comments")
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if isinstance(value, str) else value

    def has_updates(self) -> bool:
        """Return True if at least one field was provided."""
        return any(v is not None for v in self.model_dump().values())


# ----------------------------------------------------------------------
# Response
# ----------------------------------------------------------------------
class FeedbackResponse(FeedbackBase):
    """Outbound representation of a feedback record."""

    feedback_id: int
    submitted_at: datetime
    rating_label: str = Field(
        ...,
        description="Human-friendly label for the rating value.",
        examples=["Excellent"],
    )

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_model(cls, obj) -> "FeedbackResponse":
        """Build a response DTO from an ORM Feedback instance."""
        return cls(
            feedback_id=obj.feedback_id,
            participant_name=obj.participant_name,
            program_name=obj.program_name,
            rating=obj.rating,
            comments=obj.comments,
            submitted_at=obj.submitted_at,
            rating_label=RATING_LABELS.get(obj.rating, "Unknown"),
        )


# ----------------------------------------------------------------------
# Pagination / list wrapper
# ----------------------------------------------------------------------
class FeedbackListResponse(BaseModel):
    """A paginated list of feedback items."""

    total: int = Field(..., description="Total number of items matching the query.")
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    items: List[FeedbackResponse]


# ----------------------------------------------------------------------
# Statistics (dashboard)
# ----------------------------------------------------------------------
class FeedbackStats(BaseModel):
    """Aggregated feedback statistics used by the dashboard."""

    total_feedback: int
    average_rating: float
    rating_distribution: dict[int, int] = Field(
        default_factory=dict,
        description="Mapping of rating value -> number of submissions.",
    )
    recent_feedback: List[FeedbackResponse] = Field(default_factory=list)


# ----------------------------------------------------------------------
# Generic API envelope
# ----------------------------------------------------------------------
T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Uniform envelope used by every endpoint."""

    success: bool = True
    message: str = "OK"
    data: Optional[T] = None
