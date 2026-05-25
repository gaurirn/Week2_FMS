"""
ETL Pipeline Orchestrator

Glues the extract → transform → load stages together, records an
`EtlRun` row, and returns a structured result for the API layer.
"""

import time
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.etl import extract, load, transform
from app.models.etl_run_model import EtlRun


@dataclass
class EtlResult:
    run_id: int
    source_filename: str
    source_kind: str
    rows_extracted: int = 0
    rows_transformed: int = 0
    rows_loaded: int = 0
    rows_rejected: int = 0
    duplicates_removed: int = 0
    invalid_ratings_dropped: int = 0
    missing_fields_dropped: int = 0
    duration_ms: int = 0
    status: str = "success"
    error_message: Optional[str] = None
    counters: dict = field(default_factory=dict)


class EtlPipeline:
    def run_from_bytes(
        self,
        db: Session,
        *,
        contents: bytes,
        filename: str,
        mode: str = "replace",
    ) -> EtlResult:
        df, kind = extract.extract_from_bytes(contents, filename)
        return self._run(db, df=df, filename=filename, kind=kind, mode=mode)

    def run_from_path(
        self,
        db: Session,
        *,
        path: str,
        mode: str = "replace",
    ) -> EtlResult:
        df, kind = extract.extract_from_path(path)
        filename = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        return self._run(db, df=df, filename=filename, kind=kind, mode=mode)

    def _run(
        self,
        db: Session,
        *,
        df: pd.DataFrame,
        filename: str,
        kind: str,
        mode: str,
    ) -> EtlResult:
        run_row = EtlRun(
            source_filename=filename,
            source_kind=kind,
            status="running",
        )
        db.add(run_row)
        db.commit()
        db.refresh(run_row)

        started = time.perf_counter()
        try:
            df_clean, counters = transform.transform(df)
            load_counters = load.load(
                db, df_clean, etl_run_id=run_row.run_id, mode=mode
            )

            duration_ms = int((time.perf_counter() - started) * 1000)
            run_row.rows_extracted = counters["rows_extracted"]
            run_row.rows_transformed = counters["rows_transformed"]
            run_row.rows_loaded = int(load_counters["rows_loaded"])
            run_row.rows_rejected = counters["rows_rejected"]
            run_row.duplicates_removed = counters["duplicates_removed"]
            run_row.invalid_ratings_dropped = counters["invalid_ratings_dropped"]
            run_row.missing_fields_dropped = counters["missing_fields_dropped"]
            run_row.duration_ms = duration_ms
            run_row.status = "success"
            db.add(run_row)
            db.commit()
            db.refresh(run_row)

            return EtlResult(
                run_id=run_row.run_id,
                source_filename=filename,
                source_kind=kind,
                rows_extracted=run_row.rows_extracted,
                rows_transformed=run_row.rows_transformed,
                rows_loaded=run_row.rows_loaded,
                rows_rejected=run_row.rows_rejected,
                duplicates_removed=run_row.duplicates_removed,
                invalid_ratings_dropped=run_row.invalid_ratings_dropped,
                missing_fields_dropped=run_row.missing_fields_dropped,
                duration_ms=duration_ms,
                status="success",
                counters=counters,
            )
        except Exception as exc:
            db.rollback()
            duration_ms = int((time.perf_counter() - started) * 1000)
            run_row.status = "failed"
            run_row.error_message = str(exc)[:1000]
            run_row.duration_ms = duration_ms
            db.add(run_row)
            db.commit()
            db.refresh(run_row)
            return EtlResult(
                run_id=run_row.run_id,
                source_filename=filename,
                source_kind=kind,
                duration_ms=duration_ms,
                status="failed",
                error_message=str(exc),
            )


pipeline = EtlPipeline()
