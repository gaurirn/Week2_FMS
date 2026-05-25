# Feedback Management System — P2

Phase 2 of the capstone Feedback Management System. P2 keeps every
operational endpoint from Phase 1 and adds a **Pandas-based ETL
pipeline**, dedicated **analytics tables**, an analytics dashboard,
ETL upload + history screens, and downloadable cleaned-data reports.

> **Stack:** FastAPI · SQLAlchemy · SQLite · Pydantic v2 · pandas ·
> openpyxl · React 18 · React Router · Axios · Vite.

---

## What’s new in P2

- **ETL pipeline** (`backend/app/etl/`) — extract / transform / load
  built around `pandas`.
- **Analytics tables** — `feedback_analytics`, `program_analytics`,
  `etl_runs`.
- **Analytics API** — `/api/v1/analytics/summary`, `/programs`,
  `/etl/upload`, `/etl/run-sample`, `/etl/runs`, `/report.csv`,
  `/report.xlsx`.
- **Frontend** — new pages: Analytics dashboard, ETL upload, ETL
  history; new sidebar/navbar links.
- **Sample dataset** — `datasets/sample_feedback.csv` with 118 rows
  including duplicates, invalid ratings, missing fields, and text-form
  ratings to exercise every cleanup branch. A small Excel variant is
  included too.
- **Docs** — `docs/etl-workflow.md` explains the pipeline in detail.

The Phase 1 endpoints (`/feedback`, `/feedback/{id}`, `/feedback/search`,
`/feedback/stats`) are unchanged and continue to work side-by-side
with the new analytics endpoints.

---

## ETL workflow at a glance

```
CSV / XLSX  ──▶  EXTRACT  ──▶  TRANSFORM  ──▶  LOAD  ──▶  ANALYTICS API + UI
                                                  │
                                                  └─▶ etl_runs (audit trail)
```

- **EXTRACT** — `pandas.read_csv` / `pandas.read_excel` (engine
  `openpyxl`). Supports `.csv`, `.xlsx`, `.xls`. Accepts header aliases
  (`name`, `score`, `feedback`, `timestamp`, …).
- **TRANSFORM** — header normalisation, whitespace trim, Title-Case
  program names, rating coercion (`"five"`, `"5/5"`, `"2 out of 5"`
  all work; out-of-range or unparseable rows are dropped), de-dupe on
  `(participant_name, program_name, comments)`, permissive date
  parsing, sentiment derived from rating.
- **LOAD** — `replace` (default) truncates analytics first; `append`
  keeps existing rows and recomputes the per-program aggregates.

Full details — including the table-by-table schema and the expected
counters from the bundled dataset — live in
[`docs/etl-workflow.md`](docs/etl-workflow.md).

---

## Project structure

```
feedback-management-system-p2/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/                   # config, database, constants
│   │   ├── models/                 # ORM: Feedback + analytics + etl_runs
│   │   ├── schemas/                # Pydantic DTOs (P1 + analytics)
│   │   ├── crud/                   # Data-access layer
│   │   ├── services/               # Business logic
│   │   ├── routers/                # feedback_router + analytics_router
│   │   ├── etl/                    # 🆕  extract / transform / load / pipeline
│   │   ├── utils/                  # Helpers + reusable validators
│   │   └── middleware/             # Centralised exception handlers
│   ├── requirements.txt            # +pandas, +openpyxl
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BarChart.jsx        # 🆕  inline SVG bar chart
│   │   │   ├── LineChart.jsx       # 🆕  inline SVG line chart
│   │   │   └── ...                 # P1 components
│   │   ├── pages/
│   │   │   ├── Analytics.jsx       # 🆕  dashboard with charts + downloads
│   │   │   ├── EtlUpload.jsx       # 🆕  upload CSV/Excel + run pipeline
│   │   │   ├── EtlHistory.jsx      # 🆕  audit log of ETL runs
│   │   │   └── ...                 # P1 pages
│   │   ├── services/
│   │   │   ├── analyticsService.js # 🆕  /analytics/* client
│   │   │   └── feedbackService.js
│   │   ├── hooks/
│   │   │   ├── useAnalytics.js     # 🆕
│   │   │   └── useFeedback.js
│   │   └── ...
│   └── package.json
│
├── datasets/                       # 🆕
│   ├── sample_feedback.csv         # 118 dirty rows
│   └── sample_feedback_small.xlsx  # 30 rows (XLSX path)
│
├── docs/
│   ├── api-documentation.md
│   ├── setup-guide.md
│   ├── etl-workflow.md             # 🆕
│   └── screenshots/
│
└── README.md (this file)
```

---

## Running the app

### Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Swagger UI: <http://localhost:8000/docs>

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api/*` to
<http://localhost:8000>, so no CORS configuration is needed.

---

## Trying the ETL

Three ways to drive the pipeline:

1. **UI** — go to `ETL` in the navbar → click *Run on bundled sample*
   → then open `Analytics`.
2. **curl** — `curl -X POST "http://localhost:8000/api/v1/analytics/etl/run-sample"`
3. **Python** — see `docs/etl-workflow.md`.

Expected counters for `datasets/sample_feedback.csv`:

| Counter                   | Value |
| ------------------------- | ----- |
| `rows_extracted`          | 118   |
| `invalid_ratings_dropped` | 5     |
| `missing_fields_dropped`  | 3     |
| `duplicates_removed`      | 9     |
| `rows_transformed`        | 101   |
| `rows_loaded`             | 101   |

---

## Endpoints

### Phase 1 (unchanged)

| Method | Path                          |
| ------ | ----------------------------- |
| GET    | `/api/v1/feedback`            |
| GET    | `/api/v1/feedback/{id}`       |
| POST   | `/api/v1/feedback`            |
| PUT    | `/api/v1/feedback/{id}`       |
| DELETE | `/api/v1/feedback/{id}`       |
| GET    | `/api/v1/feedback/search`     |
| GET    | `/api/v1/feedback/stats`      |

### Phase 2 — analytics + ETL

| Method | Path                                    | Purpose                                  |
| ------ | --------------------------------------- | ---------------------------------------- |
| POST   | `/api/v1/analytics/etl/upload`          | Upload CSV/Excel & run ETL                |
| POST   | `/api/v1/analytics/etl/run-sample`      | Run ETL against the bundled sample        |
| GET    | `/api/v1/analytics/etl/runs`            | List previous ETL runs                    |
| GET    | `/api/v1/analytics/summary`             | Dashboard aggregates                      |
| GET    | `/api/v1/analytics/programs`            | Per-program metrics                       |
| GET    | `/api/v1/analytics/report.csv`          | Download cleaned analytics as CSV         |
| GET    | `/api/v1/analytics/report.xlsx`         | Download cleaned analytics as Excel       |

---

## Screenshots

Drop screenshots under `docs/screenshots/`:

- `etl-upload.png` — ETL screen, file picker + counters card.
- `etl-history.png` — audit table with counters per run.
- `analytics-dashboard.png` — totals, rating chart, sentiment chart, monthly trend.
- `analytics-programs.png` — per-program breakdown table.
- `download-report.png` — browser save dialog for CSV/XLSX.

---

## Future enhancements

- Real NLP-based sentiment analysis on the comments column.
- Semantic search using sentence-transformer embeddings.
- Scheduled ETL runs (APScheduler / cron).
- Polars or Dask for very large files.
- Authentication + role-based access on analytics endpoints.
- Migrate analytics tables to a separate PostgreSQL schema.
