"""
Analytics Service

Wraps the analytics CRUD and the ETL pipeline behind a single
high-level interface. The router stays thin.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.constants import RATING_LABELS
from app.crud.analytics_crud import AnalyticsCRUD, analytics_crud
from app.etl.pipeline import EtlPipeline, EtlResult, pipeline
from app.models.analytics_model import FeedbackAnalytics
from app.schemas.analytics_schema import (
    AnalyticsSummary,
    ProgramAnalyticsItem,
    RatingDistributionItem,
    SentimentBreakdown,
    TimelinePoint,
)


class AnalyticsService:
    def __init__(
        self,
        crud: AnalyticsCRUD = analytics_crud,
        etl: EtlPipeline = pipeline,
    ) -> None:
        self._crud = crud
        self._etl = etl

    # ---- ETL --------------------------------------------------------
    def run_etl_from_bytes(
        self, db: Session, *, contents: bytes, filename: str, mode: str = "replace"
    ) -> EtlResult:
        return self._etl.run_from_bytes(
            db, contents=contents, filename=filename, mode=mode
        )

    def run_etl_from_path(
        self, db: Session, *, path: str, mode: str = "replace"
    ) -> EtlResult:
        return self._etl.run_from_path(db, path=path, mode=mode)

    # ---- Summary ----------------------------------------------------
    def get_summary(self, db: Session) -> AnalyticsSummary:
        total = self._crud.total_responses(db)
        avg = self._crud.average_rating(db)
        programs_total = self._crud.distinct_program_count(db)
        latest = self._crud.latest_run_at(db)
        sentiment = self._crud.sentiment_breakdown(db)
        rating_dist = self._crud.rating_distribution(db)
        top = self._crud.top_programs(db, limit=5)
        bottom = self._crud.bottom_programs(db, limit=5)
        timeline_raw = self._crud.monthly_timeline(db)

        return AnalyticsSummary(
            total_responses=total,
            average_rating=avg,
            distinct_programs=programs_total,
            last_etl_at=latest,
            sentiment=SentimentBreakdown(**sentiment),
            rating_distribution=[
                RatingDistributionItem(
                    rating=r,
                    count=rating_dist.get(r, 0),
                    label=RATING_LABELS.get(r, str(r)),
                )
                for r in range(1, 6)
            ],
            top_programs=[ProgramAnalyticsItem.model_validate(p) for p in top],
            bottom_programs=[
                ProgramAnalyticsItem.model_validate(p) for p in bottom
            ],
            timeline=[
                TimelinePoint(
                    period=period, total=total, average_rating=avg_rating
                )
                for period, total, avg_rating in timeline_raw
            ],
        )

    def list_programs(self, db: Session):
        return self._crud.list_programs(db)

    def list_etl_runs(self, db: Session, *, limit: int = 50):
        return self._crud.list_runs(db, limit=limit)

    def all_clean_rows(self, db: Session) -> list[FeedbackAnalytics]:
        return self._crud.all_clean_rows(db)


analytics_service = AnalyticsService()
