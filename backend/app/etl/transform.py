"""
ETL — Transform stage

Cleans the raw DataFrame produced by `extract.py`:

  1. Standardise column names (whitespace-trim, lowercase, snake_case
     aliases). Accept several common header variants so the same ETL
     works on Kaggle, Google Forms and manually-curated CSVs.
  2. Coerce rating to a valid integer in [1, 5]. Strings like "five" or
     "5/5" are accepted; everything else is dropped.
  3. Trim whitespace from string fields, drop empty ones.
  4. Standardise `program_name` to Title Case.
  5. Parse `submitted_at` with a permissive set of date formats; missing
     values default to "now".
  6. Drop exact duplicates on (participant_name, program_name, comments)
     after standardisation.
  7. Derive a simple `sentiment` ("positive" / "neutral" / "negative")
     from the rating: 4-5 positive, 3 neutral, 1-2 negative.

The return value contains both the cleaned DataFrame and a dictionary
of counters that the load stage uses to populate `etl_runs`.
"""

from datetime import datetime
from typing import Dict, Tuple

import pandas as pd


# Header aliases (lower-cased + whitespace stripped) -> canonical name.
_HEADER_ALIASES = {
    "participant_name": "participant_name",
    "participant": "participant_name",
    "name": "participant_name",
    "full_name": "participant_name",
    "respondent": "participant_name",
    "program_name": "program_name",
    "program": "program_name",
    "event": "program_name",
    "event_name": "program_name",
    "course": "program_name",
    "product": "program_name",
    "rating": "rating",
    "score": "rating",
    "stars": "rating",
    "comments": "comments",
    "comment": "comments",
    "feedback": "comments",
    "remark": "comments",
    "remarks": "comments",
    "submitted_at": "submitted_at",
    "submitted_date": "submitted_at",
    "submitted": "submitted_at",
    "date": "submitted_at",
    "timestamp": "submitted_at",
}

REQUIRED_COLUMNS = ["participant_name", "program_name", "rating", "comments"]


def _normalise_headers(df: pd.DataFrame) -> pd.DataFrame:
    new_cols = {}
    for col in df.columns:
        clean = str(col).strip().lower().replace(" ", "_")
        canonical = _HEADER_ALIASES.get(clean)
        if canonical is not None:
            new_cols[col] = canonical
    df = df.rename(columns=new_cols)
    keep = [c for c in REQUIRED_COLUMNS + ["submitted_at"] if c in df.columns]
    return df[keep].copy()


def _coerce_rating(value):
    """Return an int in [1, 5] or None when not parseable."""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and (value != value):
            return None
        try:
            ivalue = int(round(float(value)))
        except (ValueError, OverflowError):
            return None
        return ivalue if 1 <= ivalue <= 5 else None

    s = str(value).strip().lower()
    if not s:
        return None
    if "/" in s:
        s = s.split("/")[0].strip()
    if " " in s:
        s = s.split(" ")[0].strip()
    word_map = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "poor": 1, "fair": 2, "good": 3, "very_good": 4,
        "excellent": 5,
    }
    if s in word_map:
        return word_map[s]
    try:
        n = int(round(float(s)))
    except ValueError:
        return None
    return n if 1 <= n <= 5 else None


def _parse_date(value) -> datetime:
    if pd.isna(value) or value in ("", None):
        return datetime.utcnow()
    if isinstance(value, datetime):
        return value
    try:
        parsed = pd.to_datetime(value, errors="coerce", utc=False)
    except Exception:
        return datetime.utcnow()
    if pd.isna(parsed):
        return datetime.utcnow()
    return parsed.to_pydatetime()


def _sentiment_from_rating(rating: int) -> str:
    if rating >= 4:
        return "positive"
    if rating == 3:
        return "neutral"
    return "negative"


def transform(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    counters = {
        "rows_extracted": int(len(df_raw)),
        "rows_transformed": 0,
        "rows_rejected": 0,
        "duplicates_removed": 0,
        "invalid_ratings_dropped": 0,
        "missing_fields_dropped": 0,
    }

    df = _normalise_headers(df_raw)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Input is missing required columns after header normalisation: {missing}"
        )

    if "submitted_at" not in df.columns:
        df["submitted_at"] = pd.NaT

    for col in ("participant_name", "program_name", "comments"):
        df[col] = df[col].astype("string").str.strip()

    df["program_name"] = df["program_name"].str.title()

    df["rating"] = df["rating"].apply(_coerce_rating)
    invalid_rating_mask = df["rating"].isna()
    counters["invalid_ratings_dropped"] = int(invalid_rating_mask.sum())
    df = df[~invalid_rating_mask].copy()
    df["rating"] = df["rating"].astype(int)

    before = len(df)
    df = df.dropna(subset=["participant_name", "program_name", "comments"]).copy()
    df = df[
        (df["participant_name"].astype(str).str.len() > 0)
        & (df["program_name"].astype(str).str.len() > 0)
        & (df["comments"].astype(str).str.len() > 0)
    ].copy()
    counters["missing_fields_dropped"] += before - len(df)

    before_dedup = len(df)
    df = df.drop_duplicates(
        subset=["participant_name", "program_name", "comments"]
    ).copy()
    counters["duplicates_removed"] = before_dedup - len(df)

    df["submitted_at"] = df["submitted_at"].apply(_parse_date)
    df["sentiment"] = df["rating"].apply(_sentiment_from_rating)

    counters["rows_transformed"] = int(len(df))
    counters["rows_rejected"] = counters["rows_extracted"] - counters["rows_transformed"]
    return df.reset_index(drop=True), counters
