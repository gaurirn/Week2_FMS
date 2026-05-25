"""
ETL Run ORM Model

Every invocation of the ETL pipeline persists a single row here so
operators can audit what was processed, when, and how clean the input
data was.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EtlRun(Base):
    __tablename__ = "etl_runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_kind: Mapped[str] = mapped_column(String(20), nullable=False)  # csv/xlsx
    rows_extracted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_transformed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_loaded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicates_removed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    invalid_ratings_dropped: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    missing_fields_dropped: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    run_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
