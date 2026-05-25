/**
 * Shared frontend constants.
 *
 * Keeping these in one place mirrors the backend's `constants.py`
 * and ensures the UI is never littered with magic numbers/strings.
 */

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const RATING_VALUES = [1, 2, 3, 4, 5];

export const RATING_LABELS = {
  1: "Poor",
  2: "Fair",
  3: "Good",
  4: "Very Good",
  5: "Excellent",
};

export const ROUTES = {
  DASHBOARD: "/",
  SUBMIT: "/submit",
  LIST: "/feedback",
  DETAILS: (id) => `/feedback/${id}`,
  EDIT: (id) => `/feedback/${id}/edit`,
  ANALYTICS: "/analytics",
  ETL_UPLOAD: "/analytics/etl",
  ETL_HISTORY: "/analytics/etl/history",
};

export const SENTIMENT_LABELS = {
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
};

export const FIELD_LIMITS = {
  participantNameMin: 2,
  participantNameMax: 120,
  programNameMin: 2,
  programNameMax: 150,
  commentsMin: 3,
  commentsMax: 2000,
};

export const DEFAULT_PAGE_SIZE = 20;
