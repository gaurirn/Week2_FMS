"""
Analytics ORM Models

`FeedbackAnalytics` stores cleaned feedback rows produced by the ETL
pipeline. `ProgramAnalytics` stores the pre-aggregated per-program
metrics so dashboard endpoints stay fast even on large datasets.

Both tables are written by the ETL load step and read by the
analytics endpoints — they are *not* used by the operational feedback
endpoints from Phase 1.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FeedbackAnalytics(Base):
    """One row per cleaned, validated feedback record."""

    __tablename__ = "feedback_analytics"
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_feedback_analytics_rating_range",
        ),
    )

    analytics_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    etl_run_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("etl_runs.run_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_row_index: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    participant_name: Mapped[str] = mapped_column(
        String(160), nullable=False, index=True
    )
    program_name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    sentiment: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )
    comments: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


class ProgramAnalytics(Base):
    """One row per program — pre-aggregated for fast dashboard queries."""

    __tablename__ = "program_analytics"

    program_name: Mapped[str] = mapped_column(String(200), primary_key=True)
    total_responses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    positive_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    neutral_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    negative_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
