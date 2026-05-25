# ETL Workflow (Phase 2)

Phase 2 adds a Pandas-based ETL pipeline that imports messy feedback
datasets, cleans them, and stores the result into dedicated analytics
tables. The Phase 1 operational tables (`feedback`) are untouched —
analytics live alongside, so existing endpoints keep working.

## High-level flow

```
                ┌───────────────┐
   CSV / XLSX ──▶│   EXTRACT     │  pandas.read_csv / pandas.read_excel
                └──────┬────────┘
                       ▼
                ┌───────────────┐
                │  TRANSFORM    │  normalise headers, coerce ratings,
                │  (pandas)     │  trim whitespace, dedupe, derive
                └──────┬────────┘  sentiment, parse dates
                       ▼
                ┌───────────────┐
                │     LOAD      │  bulk insert into
                │  (SQLAlchemy) │  feedback_analytics + program_analytics
                └──────┬────────┘
                       ▼
                ┌───────────────┐
                │ ANALYTICS API │  /api/v1/analytics/summary, /programs,
                │ + FRONTEND    │  /report.csv, /report.xlsx
                └───────────────┘
```

Every run is audited in the `etl_runs` table with counters for
extracted / transformed / loaded / rejected / duplicates removed /
invalid ratings dropped / missing fields dropped / duration.

## Extract

`backend/app/etl/extract.py`

- Accepts `.csv`, `.xlsx`, `.xls`. The kind is inferred from the
  filename extension.
- Two entry points: `extract_from_path(path)` for local files (used by
  the bundled-sample endpoint) and `extract_from_bytes(contents,
  filename)` for HTTP uploads.
- Returns a raw, untouched `pandas.DataFrame`. Cleaning is deliberately
  pushed to the next stage so this module stays trivially testable.

## Transform

`backend/app/etl/transform.py`

| Step | What it does                                                                |
| ---- | --------------------------------------------------------------------------- |
| 1.   | **Header normalisation** — accepts aliases (`name`, `score`, `feedback`, `timestamp`, etc.) and maps them to the canonical 5-column schema. |
| 2.   | **String cleanup** — trims whitespace, drops empty values.                  |
| 3.   | **Program standardisation** — Title Case so `"ai bootcamp"` and `"AI Bootcamp"` collapse together. |
| 4.   | **Rating coercion** — accepts `5`, `"5"`, `"5/5"`, `"five"`, `"2 out of 5"`. Anything outside `[1,5]` is dropped (and counted). |
| 5.   | **Duplicate removal** — on `(participant_name, program_name, comments)` after standardisation. |
| 6.   | **Date parsing** — tries multiple formats; missing values default to `now()`. |
| 7.   | **Sentiment derivation** — `positive` for 4–5, `neutral` for 3, `negative` for 1–2. |

The function returns `(clean_df, counters)` where the counters dict
records how many rows were dropped at each step.

## Load

`backend/app/etl/load.py`

- Two modes:
  - `replace` (default) — truncate `feedback_analytics` and
    `program_analytics`, then load the new batch.
  - `append` — keep existing rows; aggregates are recomputed from the
    full table afterwards.
- Bulk inserts into `feedback_analytics` (one row per cleaned feedback)
  and rebuilds `program_analytics` (one row per program with aggregate
  metrics).
- Runs in a single SQLAlchemy transaction so partial failures roll back
  cleanly.

## Orchestration

`backend/app/etl/pipeline.py`

- The `EtlPipeline` glues the three stages together.
- Inserts an `EtlRun` row at the start with `status="running"` so even
  failures are auditable, then updates it with final counts.
- Returns an `EtlResult` dataclass — the analytics router maps that
  into `EtlRunResponse` for the JSON envelope.

## Analytics tables

```
feedback_analytics
------------------
analytics_id PK
etl_run_id   FK -> etl_runs.run_id
participant_name, program_name, rating, sentiment,
comments, submitted_at, created_at

program_analytics              (pre-aggregated for fast dashboards)
-----------------
program_name  PK
total_responses, average_rating,
positive_count, neutral_count, negative_count, last_updated

etl_runs                       (audit trail)
--------
run_id PK
source_filename, source_kind,
rows_extracted, rows_transformed, rows_loaded, rows_rejected,
duplicates_removed, invalid_ratings_dropped, missing_fields_dropped,
duration_ms, status, error_message, run_at
```

## API endpoints (P2)

| Method | Path                              | Purpose                             |
| ------ | --------------------------------- | ----------------------------------- |
| POST   | `/api/v1/analytics/etl/upload`    | Upload CSV/XLSX + run pipeline       |
| POST   | `/api/v1/analytics/etl/run-sample`| Run on the bundled dataset           |
| GET    | `/api/v1/analytics/etl/runs`      | List previous runs                   |
| GET    | `/api/v1/analytics/summary`       | Dashboard aggregates                 |
| GET    | `/api/v1/analytics/programs`      | Per-program metrics                  |
| GET    | `/api/v1/analytics/report.csv`    | Download cleaned data as CSV         |
| GET    | `/api/v1/analytics/report.xlsx`   | Download cleaned data as Excel       |

## Sample dataset

`datasets/sample_feedback.csv` — 118 rows containing:

- 100 base rows with realistic distribution across 12 programs.
- 6 exact duplicates.
- 5 rows with invalid ratings (`6`, `0`, `"abc"`, `-1`, empty).
- 3 rows with missing required fields.
- 4 rows with text-form ratings (`"five"`, `"four"`, `"3 / 5"`, `"2 out of 5"`).

Running the ETL against this file produces predictable counters:

| Counter                  | Expected |
| ------------------------ | -------- |
| `rows_extracted`         | 118      |
| `invalid_ratings_dropped`| 5        |
| `missing_fields_dropped` | 3        |
| `duplicates_removed`     | 9        |
| `rows_transformed`       | 101      |
| `rows_loaded`            | 101      |

A small Excel variant (`sample_feedback_small.xlsx`) is also provided
for testing the XLSX code path.

## Running the ETL

### From the UI

1. Start the backend and frontend (see top-level README).
2. Open the **ETL** screen.
3. Either upload a CSV/XLSX or click **Run on bundled sample**.
4. Review the counters card; click **See updated analytics** to view
   the dashboard.

### From the CLI (curl)

```bash
# Bundled sample
curl -X POST "http://localhost:8000/api/v1/analytics/etl/run-sample?mode=replace"

# Upload your own file
curl -X POST -F "file=@my_dataset.csv" \
  "http://localhost:8000/api/v1/analytics/etl/upload?mode=replace"

# Download cleaned data
curl -o feedback_analytics.csv \
  "http://localhost:8000/api/v1/analytics/report.csv"
```

### Programmatically (Python)

```python
from app.core.database import SessionLocal, init_db
from app.etl.pipeline import pipeline

init_db()
with SessionLocal() as db:
    result = pipeline.run_from_path(db, path="datasets/sample_feedback.csv")
    print(result)
```

## Future enhancements

- Real sentiment analysis (replace the rating-derived heuristic).
- Semantic search over comments using sentence-transformer embeddings.
- Scheduled ETL runs (e.g., cron / APScheduler) for recurring imports.
- Streaming ETL for very large files (Polars / Dask).
- Move analytics to a separate PostgreSQL schema for clearer isolation.
