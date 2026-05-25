"""
Feedback Service Layer

Holds business logic and orchestration. Routers are kept thin: they
parse input and call into here. This layer enforces invariants such
as "a feedback must exist before it can be updated", and it converts
ORM objects into Pydantic response DTOs.

Keeping this seam clean makes it straightforward to plug in features
later (sentiment scoring, semantic search, async tasks, etc.) without
touching the HTTP layer.
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import Messages
from app.crud.feedback_crud import FeedbackCRUD, feedback_crud
from app.schemas.feedback_schema import (
    FeedbackCreate,
    FeedbackListResponse,
    FeedbackResponse,
    FeedbackStats,
    FeedbackUpdate,
)
from app.utils.helpers import clamp_page_size


class FeedbackService:
    """Encapsulates business workflows for feedback management."""

    def __init__(self, crud: FeedbackCRUD = feedback_crud) -> None:
        self._crud = crud

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def create_feedback(
        self, db: Session, payload: FeedbackCreate
    ) -> FeedbackResponse:
        record = self._crud.create(db, payload)
        return FeedbackResponse.from_orm_model(record)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def get_feedback(self, db: Session, feedback_id: int) -> FeedbackResponse:
        record = self._crud.get_by_id(db, feedback_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Messages.FEEDBACK_NOT_FOUND.format(
                    feedback_id=feedback_id
                ),
            )
        return FeedbackResponse.from_orm_model(record)

    def list_feedback(
        self, db: Session, page: int = 1, page_size: int = 20
    ) -> FeedbackListResponse:
        page_size = clamp_page_size(page_size)
        page = max(page, 1)
        records, total = self._crud.list(db, page=page, page_size=page_size)
        return FeedbackListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[FeedbackResponse.from_orm_model(r) for r in records],
        )

    def search_feedback(
        self,
        db: Session,
        *,
        keyword: Optional[str] = None,
        rating: Optional[int] = None,
        program_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> FeedbackListResponse:
        page_size = clamp_page_size(page_size)
        page = max(page, 1)
        records, total = self._crud.search(
            db,
            keyword=keyword,
            rating=rating,
            program_name=program_name,
            page=page,
            page_size=page_size,
        )
        return FeedbackListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[FeedbackResponse.from_orm_model(r) for r in records],
        )

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update_feedback(
        self, db: Session, feedback_id: int, payload: FeedbackUpdate
    ) -> FeedbackResponse:
        if not payload.has_updates():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided for an update.",
            )
        record = self._crud.get_by_id(db, feedback_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Messages.FEEDBACK_NOT_FOUND.format(
                    feedback_id=feedback_id
                ),
            )
        updated = self._crud.update(db, record, payload)
        return FeedbackResponse.from_orm_model(updated)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete_feedback(self, db: Session, feedback_id: int) -> None:
        record = self._crud.get_by_id(db, feedback_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Messages.FEEDBACK_NOT_FOUND.format(
                    feedback_id=feedback_id
                ),
            )
        self._crud.delete(db, record)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------
    def get_stats(self, db: Session, recent_limit: int = 5) -> FeedbackStats:
        recent_records = self._crud.recent(db, limit=recent_limit)
        return FeedbackStats(
            total_feedback=self._crud.count(db),
            average_rating=self._crud.average_rating(db),
            rating_distribution=self._crud.rating_distribution(db),
            recent_feedback=[
                FeedbackResponse.from_orm_model(r) for r in recent_records
            ],
        )


# Singleton service instance used by routers
feedback_service = FeedbackService()
