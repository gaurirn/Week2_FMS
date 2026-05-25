"""
Feedback Router

HTTP layer for feedback management. Endpoints stay deliberately thin:
they parse and validate input, delegate to the service layer, and
return the result wrapped in the uniform `APIResponse` envelope.

Endpoints
---------
    GET    /feedback/stats
    GET    /feedback/search
    GET    /feedback
    GET    /feedback/{feedback_id}
    POST   /feedback
    PUT    /feedback/{feedback_id}
    DELETE /feedback/{feedback_id}
"""

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.constants import MAX_RATING, MIN_RATING, Messages
from app.core.database import get_db
from app.schemas.feedback_schema import (
    APIResponse,
    FeedbackCreate,
    FeedbackListResponse,
    FeedbackResponse,
    FeedbackStats,
    FeedbackUpdate,
)
from app.services.feedback_service import FeedbackService, feedback_service

router = APIRouter(prefix="/feedback", tags=["Feedback"])


# ----------------------------------------------------------------------
# Dependency injection helpers
# ----------------------------------------------------------------------
def get_feedback_service() -> FeedbackService:
    """Resolve the service singleton (overridable in tests)."""
    return feedback_service


# ----------------------------------------------------------------------
# Statistics (dashboard)
# ----------------------------------------------------------------------
@router.get(
    "/stats",
    response_model=APIResponse[FeedbackStats],
    summary="Aggregate statistics for the dashboard",
)
def get_stats(
    recent_limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    service: FeedbackService = Depends(get_feedback_service),
):
    stats = service.get_stats(db, recent_limit=recent_limit)
    return APIResponse[FeedbackStats](message="OK", data=stats)


# ----------------------------------------------------------------------
# Search
# ----------------------------------------------------------------------
@router.get(
    "/search",
    response_model=APIResponse[FeedbackListResponse],
    summary="Search and filter feedback",
)
def search_feedback(
    keyword: Optional[str] = Query(
        default=None,
        description="Case-insensitive partial match across name/program/comments.",
    ),
    rating: Optional[int] = Query(
        default=None, ge=MIN_RATING, le=MAX_RATING
    ),
    program_name: Optional[str] = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    service: FeedbackService = Depends(get_feedback_service),
):
    result = service.search_feedback(
        db,
        keyword=keyword,
        rating=rating,
        program_name=program_name,
        page=page,
        page_size=page_size,
    )
    return APIResponse[FeedbackListResponse](message="OK", data=result)


# ----------------------------------------------------------------------
# List
# ----------------------------------------------------------------------
@router.get(
    "",
    response_model=APIResponse[FeedbackListResponse],
    summary="List all feedback (paginated)",
)
def list_feedback(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    service: FeedbackService = Depends(get_feedback_service),
):
    result = service.list_feedback(db, page=page, page_size=page_size)
    return APIResponse[FeedbackListResponse](message="OK", data=result)


# ----------------------------------------------------------------------
# Retrieve single
# ----------------------------------------------------------------------
@router.get(
    "/{feedback_id}",
    response_model=APIResponse[FeedbackResponse],
    summary="Retrieve a single feedback record",
)
def get_feedback(
    feedback_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    service: FeedbackService = Depends(get_feedback_service),
):
    record = service.get_feedback(db, feedback_id)
    return APIResponse[FeedbackResponse](message="OK", data=record)


# ----------------------------------------------------------------------
# Create
# ----------------------------------------------------------------------
@router.post(
    "",
    response_model=APIResponse[FeedbackResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new feedback",
)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    service: FeedbackService = Depends(get_feedback_service),
):
    created = service.create_feedback(db, payload)
    return APIResponse[FeedbackResponse](
        message=Messages.FEEDBACK_CREATED, data=created
    )


# ----------------------------------------------------------------------
# Update
# ----------------------------------------------------------------------
@router.put(
    "/{feedback_id}",
    response_model=APIResponse[FeedbackResponse],
    summary="Update an existing feedback",
)
def update_feedback(
    payload: FeedbackUpdate,
    feedback_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    service: FeedbackService = Depends(get_feedback_service),
):
    updated = service.update_feedback(db, feedback_id, payload)
    return APIResponse[FeedbackResponse](
        message=Messages.FEEDBACK_UPDATED, data=updated
    )


# ----------------------------------------------------------------------
# Delete
# ----------------------------------------------------------------------
@router.delete(
    "/{feedback_id}",
    response_model=APIResponse[None],
    summary="Delete a feedback record",
)
def delete_feedback(
    feedback_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    service: FeedbackService = Depends(get_feedback_service),
):
    service.delete_feedback(db, feedback_id)
    return APIResponse[None](message=Messages.FEEDBACK_DELETED, data=None)
