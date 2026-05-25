# Setup Guide

Step-by-step instructions for getting the Feedback Management System
running locally on Windows, macOS or Linux.

## 1. Prerequisites

- **Python 3.10+** — verify with `python --version`.
- **Node.js 18+** and **npm 9+** — verify with `node --version`.
- **Git** (for cloning).
- A REST client such as Postman, Insomnia, or `curl` (optional).

## 2. Project layout

```
feedback-management-system/
├── backend/      # FastAPI service
├── frontend/     # React (Vite) SPA
├── docs/         # Documentation
└── README.md
```

## 3. Backend setup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` if you want to override defaults.
The most useful variables are:

```env
DATABASE_URL=sqlite:///./feedback.db
DEBUG=True
```

### Run

```bash
uvicorn app.main:app --reload --port 8000
```

The server starts at <http://localhost:8000> and creates the SQLite
database file (`feedback.db`) on first launch. The interactive docs
live at <http://localhost:8000/docs>.

### Optional: seed sample data

Run this snippet from a Python shell with the virtualenv activated:

```python
import requests

samples = [
    {"participant_name": "Aarav Singh", "program_name": "AI Bootcamp 2026", "rating": 5, "comments": "Loved every session."},
    {"participant_name": "Priya Iyer", "program_name": "Cloud Workshop",     "rating": 4, "comments": "Very practical and well organised."},
    {"participant_name": "Diego Rivera","program_name": "DevOps Summit",     "rating": 3, "comments": "Good content, pacing could improve."},
    {"participant_name": "Mei Tanaka",  "program_name": "AI Bootcamp 2026",  "rating": 5, "comments": "Mentors were outstanding."},
    {"participant_name": "Lia Costa",   "program_name": "UX Conference",     "rating": 2, "comments": "Sessions were too short."},
]
for s in samples:
    r = requests.post("http://localhost:8000/api/v1/feedback", json=s)
    print(r.status_code, r.json())
```

## 4. Frontend setup

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The app opens automatically at <http://localhost:5173>.

### How the frontend talks to the backend

`vite.config.js` proxies any request to `/api/*` to
`http://localhost:8000`. This means:

- No CORS configuration is required during development.
- `frontend/src/utils/constants.js` defines `API_BASE_URL = "/api/v1"`.
- For a production build that hits a different host, set
  `VITE_API_BASE_URL` in a `.env` file.

## 5. Production build

Backend:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Frontend:

```bash
cd frontend
npm run build
npm run preview   # serves the dist/ folder for smoke testing
```

Serve `frontend/dist` from your reverse proxy (nginx, Caddy, etc.) and
point `/api` at the FastAPI service.

## 6. Troubleshooting

- **`ModuleNotFoundError: app`** — make sure you’re running `uvicorn`
  from the `backend/` folder so that `app.main:app` resolves.
- **CORS errors** — confirm your frontend origin is listed in
  `CORS_ALLOW_ORIGINS` in `app/core/config.py` (defaults cover the
  common dev ports already).
- **SQLite file locked** — close any SQLite browser that has the
  `feedback.db` file open.
- **Vite proxy not working** — restart `npm run dev` after changing
  `vite.config.js`.
