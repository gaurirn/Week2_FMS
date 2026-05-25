/**
 * Analytics + ETL API service.
 *
 * Talks to the Phase 2 endpoints under /api/v1/analytics.
 * Reuses the same error envelope shape as feedbackService.
 */

import axios from "axios";
import { API_BASE_URL } from "../utils/constants";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // ETL uploads can take a moment for big files
});

function unwrap(response) {
  const payload = response?.data ?? {};
  return payload.data ?? null;
}

function normalizeError(error) {
  const status = error?.response?.status ?? 0;
  const payload = error?.response?.data ?? {};
  return {
    message:
      payload?.message ||
      error?.message ||
      "Unexpected error. Please try again.",
    status,
    raw: payload,
  };
}

api.interceptors.response.use(
  (r) => r,
  (err) => Promise.reject(normalizeError(err))
);

const analyticsService = {
  async summary() {
    const resp = await api.get("/analytics/summary");
    return unwrap(resp);
  },

  async programs() {
    const resp = await api.get("/analytics/programs");
    return unwrap(resp);
  },

  async etlRuns(limit = 50) {
    const resp = await api.get("/analytics/etl/runs", { params: { limit } });
    return unwrap(resp);
  },

  async uploadAndRun(file, mode = "replace") {
    const form = new FormData();
    form.append("file", file);
    const resp = await api.post("/analytics/etl/upload", form, {
      params: { mode },
      headers: { "Content-Type": "multipart/form-data" },
    });
    return unwrap(resp);
  },

  async runSample(mode = "replace") {
    const resp = await api.post(
      "/analytics/etl/run-sample",
      null,
      { params: { mode } }
    );
    return unwrap(resp);
  },

  reportCsvUrl() {
    return `${API_BASE_URL}/analytics/report.csv`;
  },

  reportXlsxUrl() {
    return `${API_BASE_URL}/analytics/report.xlsx`;
  },
};

export default analyticsService;
