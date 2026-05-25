"""
Feedback CRUD Layer

This module is the *only* place that talks to the database for the
`Feedback` model. The service layer calls into here so swapping the
ORM or the database has a single, well-defined seam.

The class is exposed as a singleton (`feedback_crud`) which keeps the
call sites short while still being trivial to mock in unit tests.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.feedback_model import Feedback
from app.schemas.feedback_schema import FeedbackCreate, FeedbackUpdate


class FeedbackCRUD:
    """Encapsulates database operations for the Feedback entity."""

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def create(self, db: Session, payload: FeedbackCreate) -> Feedback:
        """Persist a new feedback record and return it."""
        feedback = Feedback(
            participant_name=payload.participant_name,
            program_name=payload.program_name,
            rating=payload.rating,
            comments=payload.comments,
            submitted_at=datetime.utcnow(),
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def get_by_id(self, db: Session, feedback_id: int) -> Optional[Feedback]:
        """Return a single feedback record by id, or None."""
        return db.get(Feedback, feedback_id)

    def list(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "submitted_at",
        descending: bool = True,
    ) -> Tuple[List[Feedback], int]:
        """Return a paginated list and the total row count."""
        offset = (page - 1) * page_size
        order_col = getattr(Feedback, order_by, Feedback.submitted_at)
        direction = desc if descending else asc

        stmt = (
            select(Feedback)
            .order_by(direction(order_col))
            .offset(offset)
            .limit(page_size)
        )
        items = list(db.execute(stmt).scalars().all())

        total = db.execute(select(func.count(Feedback.feedback_id))).scalar_one()
        return items, int(total)

    def search(
        self,
        db: Session,
        *,
        keyword: Optional[str] = None,
        rating: Optional[int] = None,
        program_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Feedback], int]:
        """
        Run a flexible search query.

        - `keyword` does case-insensitive partial matching on
          participant_name, program_name and comments.
        - `rating` filters on exact rating value.
        - `program_name` filters by partial program name match.
        """
        stmt = select(Feedback)
        count_stmt = select(func.count(Feedback.feedback_id))

        filters = []
        if keyword:
            pattern = f"%{keyword.lower()}%"
            filters.append(
                or_(
                    func.lower(Feedback.participant_name).like(pattern),
                    func.lower(Feedback.program_name).like(pattern),
                    func.lower(Feedback.comments).like(pattern),
                )
            )
        if rating is not None:
            filters.append(Feedback.rating == rating)
        if program_name:
            filters.append(
                func.lower(Feedback.program_name).like(
                    f"%{program_name.lower()}%"
                )
            )

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        offset = (page - 1) * page_size
        stmt = (
            stmt.order_by(desc(Feedback.submitted_at))
            .offset(offset)
            .limit(page_size)
        )

        items = list(db.execute(stmt).scalars().all())
        total = db.execute(count_stmt).scalar_one()
        return items, int(total)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(
        self, db: Session, feedback: Feedback, payload: FeedbackUpdate
    ) -> Feedback:
        """Apply non-None fields from `payload` to `feedback`."""
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in data.items():
            setattr(feedback, field, value)
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete(self, db: Session, feedback: Feedback) -> None:
        """Remove a feedback record from the database."""
        db.delete(feedback)
        db.commit()

    # ------------------------------------------------------------------
    # Aggregates / Stats
    # ------------------------------------------------------------------
    def count(self, db: Session) -> int:
        return int(
            db.execute(select(func.count(Feedback.feedback_id))).scalar_one()
        )

    def average_rating(self, db: Session) -> float:
        avg = db.execute(select(func.avg(Feedback.rating))).scalar()
        return round(float(avg), 2) if avg is not None else 0.0

    def rating_distribution(self, db: Session) -> dict[int, int]:
        rows = db.execute(
            select(Feedback.rating, func.count(Feedback.feedback_id))
            .group_by(Feedback.rating)
        ).all()
        distribution = {r: 0 for r in range(1, 6)}
        for rating_value, count in rows:
            distribution[int(rating_value)] = int(count)
        return distribution

    def recent(self, db: Session, limit: int = 5) -> List[Feedback]:
        stmt = (
            select(Feedback)
            .order_by(desc(Feedback.submitted_at))
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())


# Singleton-style instance used by the service layer
feedback_crud = FeedbackCRUD()
