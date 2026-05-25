/**
 * Feedback API Service Layer
 *
 * Centralises every HTTP call against the backend so the rest of the
 * UI never touches Axios directly. Each method:
 *   - returns the data payload (already unwrapped from the API envelope)
 *   - rethrows a normalised error (message + status + fieldErrors)
 *
 * This abstraction makes mocking trivial in tests and keeps the call
 * sites readable.
 */

import axios from "axios";
import { API_BASE_URL } from "../utils/constants";

// ---- Axios instance ---------------------------------------------------
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

// ---- Response envelope helpers ---------------------------------------
function unwrap(response) {
  // Backend envelope: { success, message, data }
  const payload = response?.data ?? {};
  return payload.data ?? null;
}

function normalizeError(error) {
  const status = error?.response?.status ?? 0;
  const payload = error?.response?.data ?? {};
  const fieldErrors = payload?.data?.errors ?? [];
  return {
    message:
      payload?.message ||
      error?.message ||
      "Unexpected error. Please try again.",
    status,
    fieldErrors,
    raw: payload,
  };
}

api.interceptors.response.use(
  (resp) => resp,
  (err) => Promise.reject(normalizeError(err))
);

// ---- Endpoints --------------------------------------------------------
const feedbackService = {
  async list({ page = 1, pageSize = 20 } = {}) {
    const resp = await api.get(`/feedback`, {
      params: { page, page_size: pageSize },
    });
    return unwrap(resp);
  },

  async getById(id) {
    const resp = await api.get(`/feedback/${id}`);
    return unwrap(resp);
  },

  async create(payload) {
    const resp = await api.post(`/feedback`, payload);
    return unwrap(resp);
  },

  async update(id, payload) {
    const resp = await api.put(`/feedback/${id}`, payload);
    return unwrap(resp);
  },

  async remove(id) {
    const resp = await api.delete(`/feedback/${id}`);
    return unwrap(resp);
  },

  async search({
    keyword,
    rating,
    programName,
    page = 1,
    pageSize = 20,
  } = {}) {
    const params = { page, page_size: pageSize };
    if (keyword) params.keyword = keyword;
    if (rating != null && rating !== "") params.rating = rating;
    if (programName) params.program_name = programName;

    const resp = await api.get(`/feedback/search`, { params });
    return unwrap(resp);
  },

  async stats(recentLimit = 5) {
    const resp = await api.get(`/feedback/stats`, {
      params: { recent_limit: recentLimit },
    });
    return unwrap(resp);
  },
};

export default feedbackService;
