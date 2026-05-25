"""
ETL — Load stage

Persists the cleaned DataFrame into the analytics tables:

  * `feedback_analytics`  — one row per validated feedback record.
  * `program_analytics`   — pre-aggregated per-program metrics
                            (upserted from the cleaned data).

The load runs in a single transaction; on failure the caller rolls
back via the surrounding ETL pipeline.

Modes
-----
`replace`  (default) — truncate analytics tables before loading.
`append`             — keep existing rows; aggregates are recomputed
                       from the full table afterwards.
"""

from datetime import datetime
from typing import Dict, Literal

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.analytics_model import FeedbackAnalytics, ProgramAnalytics

LoadMode = Literal["replace", "append"]


def load(
    db: Session,
    df_clean: pd.DataFrame,
    *,
    etl_run_id: int,
    mode: LoadMode = "replace",
) -> Dict[str, int]:
    if mode == "replace":
        db.execute(delete(FeedbackAnalytics))
        db.execute(delete(ProgramAnalytics))
        db.flush()

    records = []
    for idx, row in df_clean.iterrows():
        records.append(
            FeedbackAnalytics(
                etl_run_id=etl_run_id,
                source_row_index=int(idx),
                participant_name=str(row["participant_name"]),
                program_name=str(row["program_name"]),
                rating=int(row["rating"]),
                sentiment=str(row["sentiment"]),
                comments=str(row["comments"]),
                submitted_at=row["submitted_at"],
            )
        )
    if records:
        db.add_all(records)
        db.flush()

    program_rows = (
        df_clean.groupby("program_name")
        .agg(
            total_responses=("rating", "count"),
            average_rating=("rating", "mean"),
            positive_count=("sentiment", lambda s: int((s == "positive").sum())),
            neutral_count=("sentiment", lambda s: int((s == "neutral").sum())),
            negative_count=("sentiment", lambda s: int((s == "negative").sum())),
        )
        .reset_index()
    )

    if mode == "append":
        full = pd.read_sql(
            select(
                FeedbackAnalytics.program_name,
                FeedbackAnalytics.rating,
                FeedbackAnalytics.sentiment,
            ),
            db.connection(),
        )
        program_rows = (
            full.groupby("program_name")
            .agg(
                total_responses=("rating", "count"),
                average_rating=("rating", "mean"),
                positive_count=("sentiment", lambda s: int((s == "positive").sum())),
                neutral_count=("sentiment", lambda s: int((s == "neutral").sum())),
                negative_count=("sentiment", lambda s: int((s == "negative").sum())),
            )
            .reset_index()
        )

    now = datetime.utcnow()
    program_records = [
        ProgramAnalytics(
            program_name=str(r["program_name"]),
            total_responses=int(r["total_responses"]),
            average_rating=float(round(r["average_rating"], 2)),
            positive_count=int(r["positive_count"]),
            neutral_count=int(r["neutral_count"]),
            negative_count=int(r["negative_count"]),
            last_updated=now,
        )
        for _, r in program_rows.iterrows()
    ]
    if mode == "append":
        db.execute(delete(ProgramAnalytics))
        db.flush()
    if program_records:
        db.add_all(program_records)

    db.commit()
    return {"rows_loaded": len(records)}
