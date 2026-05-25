# Feedback Management System - Frontend

React + Vite single-page application that consumes the FastAPI backend.

## Tech stack

- React 18 (functional components + hooks)
- React Router DOM 6
- Axios (centralised service layer)
- Vite (dev server + build)
- Hand-rolled CSS design system (no external UI framework required)

## Project layout

```
frontend/
├── public/
├── src/
│   ├── components/      # Reusable presentational components
│   │   ├── Navbar.jsx
│   │   ├── FeedbackCard.jsx
│   │   ├── FeedbackForm.jsx
│   │   ├── SearchBar.jsx
│   │   ├── ProgramFilter.jsx
│   │   ├── RatingFilter.jsx
│   │   ├── Alert.jsx
│   │   └── Loader.jsx
│   ├── pages/           # Route-level components
│   │   ├── Dashboard.jsx
│   │   ├── SubmitFeedback.jsx
│   │   ├── FeedbackList.jsx
│   │   ├── FeedbackDetails.jsx
│   │   ├── EditFeedback.jsx
│   │   └── NotFound.jsx
│   ├── services/        # Axios service layer
│   ├── hooks/           # Custom React hooks
│   ├── styles/          # Global stylesheet
│   ├── utils/           # Constants / helpers
│   ├── App.jsx
│   ├── main.jsx
│   └── routes.jsx
├── index.html
├── vite.config.js
├── package.json
└── README.md
```

## Setup

```bash
cd frontend
npm install
```

## Run (dev)

```bash
npm run dev
```

The app starts at <http://localhost:5173>. The Vite dev server proxies
all `/api/*` requests to `http://localhost:8000`, so you can run the
backend without any CORS configuration.

## Build

```bash
npm run build
npm run preview
```

## Configuration

The API base URL is read from `VITE_API_BASE_URL` (defaults to `/api/v1`).
Override it via a `.env` file (see `.env.example`).
