"""
Analytics / ETL Schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---- ETL run -----------------------------------------------------------
class EtlRunResponse(BaseModel):
    run_id: int
    source_filename: str
    source_kind: str
    rows_extracted: int
    rows_transformed: int
    rows_loaded: int
    rows_rejected: int
    duplicates_removed: int
    invalid_ratings_dropped: int
    missing_fields_dropped: int
    duration_ms: int
    status: str
    error_message: Optional[str] = None
    run_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EtlRunListResponse(BaseModel):
    total: int
    items: List[EtlRunResponse]


# ---- Analytics aggregates ----------------------------------------------
class RatingDistributionItem(BaseModel):
    rating: int
    count: int
    label: str


class SentimentBreakdown(BaseModel):
    positive: int = 0
    neutral: int = 0
    negative: int = 0


class ProgramAnalyticsItem(BaseModel):
    program_name: str
    total_responses: int
    average_rating: float
    positive_count: int
    neutral_count: int
    negative_count: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class TimelinePoint(BaseModel):
    period: str = Field(..., description="ISO date for the period (month or day).")
    total: int
    average_rating: float


class AnalyticsSummary(BaseModel):
    total_responses: int
    average_rating: float
    distinct_programs: int
    last_etl_at: Optional[datetime] = None
    sentiment: SentimentBreakdown
    rating_distribution: List[RatingDistributionItem]
    top_programs: List[ProgramAnalyticsItem]
    bottom_programs: List[ProgramAnalyticsItem]
    timeline: List[TimelinePoint]
