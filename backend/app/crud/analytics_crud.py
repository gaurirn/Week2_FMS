"""
Analytics CRUD

Read-only queries against the analytics tables populated by the ETL
pipeline, plus convenience queries against `etl_runs`.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.models.analytics_model import FeedbackAnalytics, ProgramAnalytics
from app.models.etl_run_model import EtlRun


class AnalyticsCRUD:
    # ---- Aggregates ----------------------------------------------------
    def total_responses(self, db: Session) -> int:
        return int(
            db.execute(select(func.count(FeedbackAnalytics.analytics_id))).scalar_one()
        )

    def average_rating(self, db: Session) -> float:
        avg = db.execute(select(func.avg(FeedbackAnalytics.rating))).scalar()
        return round(float(avg), 2) if avg is not None else 0.0

    def distinct_program_count(self, db: Session) -> int:
        return int(
            db.execute(
                select(func.count(func.distinct(FeedbackAnalytics.program_name)))
            ).scalar_one()
        )

    def rating_distribution(self, db: Session) -> dict[int, int]:
        rows = db.execute(
            select(FeedbackAnalytics.rating, func.count(FeedbackAnalytics.analytics_id))
            .group_by(FeedbackAnalytics.rating)
        ).all()
        distribution = {r: 0 for r in range(1, 6)}
        for rating_value, count in rows:
            distribution[int(rating_value)] = int(count)
        return distribution

    def sentiment_breakdown(self, db: Session) -> dict[str, int]:
        rows = db.execute(
            select(
                FeedbackAnalytics.sentiment,
                func.count(FeedbackAnalytics.analytics_id),
            ).group_by(FeedbackAnalytics.sentiment)
        ).all()
        breakdown = {"positive": 0, "neutral": 0, "negative": 0}
        for sentiment, count in rows:
            if sentiment in breakdown:
                breakdown[sentiment] = int(count)
        return breakdown

    # ---- Per-program ----------------------------------------------------
    def list_programs(self, db: Session) -> List[ProgramAnalytics]:
        stmt = select(ProgramAnalytics).order_by(
            desc(ProgramAnalytics.total_responses)
        )
        return list(db.execute(stmt).scalars().all())

    def top_programs(
        self, db: Session, *, limit: int = 5
    ) -> List[ProgramAnalytics]:
        stmt = (
            select(ProgramAnalytics)
            .where(ProgramAnalytics.total_responses > 0)
            .order_by(desc(ProgramAnalytics.average_rating), desc(ProgramAnalytics.total_responses))
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def bottom_programs(
        self, db: Session, *, limit: int = 5
    ) -> List[ProgramAnalytics]:
        stmt = (
            select(ProgramAnalytics)
            .where(ProgramAnalytics.total_responses > 0)
            .order_by(asc(ProgramAnalytics.average_rating), desc(ProgramAnalytics.total_responses))
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    # ---- Timeline (monthly buckets) -----------------------------------
    def monthly_timeline(self, db: Session) -> List[Tuple[str, int, float]]:
        # SQLite supports strftime; for other dialects this could use func.date_trunc.
        period = func.strftime("%Y-%m", FeedbackAnalytics.submitted_at)
        stmt = (
            select(
                period.label("period"),
                func.count(FeedbackAnalytics.analytics_id),
                func.avg(FeedbackAnalytics.rating),
            )
            .group_by("period")
            .order_by(asc("period"))
        )
        rows = db.execute(stmt).all()
        return [
            (str(period_val), int(total), round(float(avg or 0), 2))
            for period_val, total, avg in rows
        ]

    # ---- ETL runs ------------------------------------------------------
    def list_runs(
        self, db: Session, *, limit: int = 50
    ) -> List[EtlRun]:
        stmt = (
            select(EtlRun)
            .order_by(desc(EtlRun.run_at))
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def latest_run_at(self, db: Session) -> Optional[datetime]:
        stmt = (
            select(EtlRun.run_at)
            .where(EtlRun.status == "success")
            .order_by(desc(EtlRun.run_at))
            .limit(1)
        )
        return db.execute(stmt).scalar()

    # ---- Raw rows (for CSV/XLSX exports) -------------------------------
    def all_clean_rows(self, db: Session) -> List[FeedbackAnalytics]:
        stmt = select(FeedbackAnalytics).order_by(desc(FeedbackAnalytics.submitted_at))
        return list(db.execute(stmt).scalars().all())


analytics_crud = AnalyticsCRUD()
