"""
Feedback ORM Model

Defines the database table that stores user-submitted feedback.
The model purposely contains only persistence concerns; all
validation lives in the Pydantic schemas, and business logic lives
in the service layer.
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import MAX_RATING, MIN_RATING
from app.core.database import Base


class Feedback(Base):
    """Represents a single feedback record."""

    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint(
            f"rating >= {MIN_RATING} AND rating <= {MAX_RATING}",
            name="ck_feedback_rating_range",
        ),
    )

    feedback_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    participant_name: Mapped[str] = mapped_column(
        String(120), nullable=False, index=True
    )
    program_name: Mapped[str] = mapped_column(
        String(150), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    comments: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    def __repr__(self) -> str:  # pragma: no cover - dev convenience only
        return (
            f"<Feedback id={self.feedback_id} "
            f"participant={self.participant_name!r} "
            f"program={self.program_name!r} "
            f"rating={self.rating}>"
        )
