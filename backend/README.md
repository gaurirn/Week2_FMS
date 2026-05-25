# Feedback Management System - Backend

FastAPI service that powers the Feedback Management System.

## Tech stack

- FastAPI (Python web framework)
- SQLAlchemy 2.x (ORM)
- Pydantic v2 (validation / serialization)
- SQLite (default; swappable to PostgreSQL via `DATABASE_URL`)
- Uvicorn (ASGI server)

## Project layout

```
backend/
├── app/
│   ├── main.py                 # FastAPI app factory + lifecycle hooks
│   ├── core/                   # Settings, DB engine/session, constants
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic DTOs
│   ├── crud/                   # Data-access layer (DB-only)
│   ├── services/               # Business logic / orchestration
│   ├── routers/                # HTTP endpoints (thin controllers)
│   ├── utils/                  # Helpers, reusable validators
│   └── middleware/             # Centralised exception handlers
├── requirements.txt
└── README.md
```

## Setup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

The app starts at `http://localhost:8000`.

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- OpenAPI JSON: <http://localhost:8000/openapi.json>

All feedback endpoints are mounted under `/api/v1/feedback`.

## Configuration

Configuration is loaded from environment variables (or `.env`) via
`app/core/config.py`. The most relevant variables are:

| Variable             | Default                      | Purpose                       |
| -------------------- | ---------------------------- | ----------------------------- |
| `DATABASE_URL`       | `sqlite:///./feedback.db`    | SQLAlchemy connection string  |
| `CORS_ALLOW_ORIGINS` | localhost dev origins        | Comma-separated CORS origins  |
| `DEBUG`              | `True`                       | Enable verbose error reports  |

## API summary

| Method | Path                            | Description                       |
| ------ | ------------------------------- | --------------------------------- |
| GET    | `/api/v1/feedback`              | List feedback (paginated)         |
| GET    | `/api/v1/feedback/{id}`         | Retrieve one feedback             |
| POST   | `/api/v1/feedback`              | Submit a new feedback             |
| PUT    | `/api/v1/feedback/{id}`         | Update a feedback                 |
| DELETE | `/api/v1/feedback/{id}`         | Delete a feedback                 |
| GET    | `/api/v1/feedback/search`       | Keyword / rating / program search |
| GET    | `/api/v1/feedback/stats`        | Dashboard aggregates              |

See `docs/api-documentation.md` for full request/response examples.
