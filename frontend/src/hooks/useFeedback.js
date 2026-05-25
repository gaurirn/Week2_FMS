/**
 * Custom React hooks for feedback data.
 *
 *   useFeedbackList   - paginated list with optional search params
 *   useFeedbackItem   - single feedback record by id
 *   useFeedbackStats  - dashboard aggregates
 *   useAsyncAction    - generic helper for create / update / delete flows
 *
 * Each hook returns { data, loading, error, refetch } so the UI can
 * stay declarative.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import feedbackService from "../services/feedbackService";

// ---------- generic data hook -----------------------------------------
function useAsyncData(loader, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const mounted = useRef(true);

  const run = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await loader();
      if (mounted.current) setData(result);
    } catch (err) {
      if (mounted.current) setError(err);
    } finally {
      if (mounted.current) setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    mounted.current = true;
    run();
    return () => {
      mounted.current = false;
    };
  }, [run]);

  return { data, loading, error, refetch: run };
}

// ---------- list -------------------------------------------------------
export function useFeedbackList({
  page = 1,
  pageSize = 20,
  keyword = "",
  rating = "",
  programName = "",
} = {}) {
  return useAsyncData(
    () => {
      const hasFilters =
        Boolean(keyword) ||
        rating !== "" ||
        Boolean(programName);
      return hasFilters
        ? feedbackService.search({
            keyword,
            rating: rating === "" ? undefined : Number(rating),
            programName,
            page,
            pageSize,
          })
        : feedbackService.list({ page, pageSize });
    },
    [page, pageSize, keyword, rating, programName]
  );
}

// ---------- single item -----------------------------------------------
export function useFeedbackItem(id) {
  return useAsyncData(
    () => (id ? feedbackService.getById(id) : Promise.resolve(null)),
    [id]
  );
}

// ---------- stats ------------------------------------------------------
export function useFeedbackStats(recentLimit = 5) {
  return useAsyncData(
    () => feedbackService.stats(recentLimit),
    [recentLimit]
  );
}

// ---------- mutation helper -------------------------------------------
export function useAsyncAction(action) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      try {
        const result = await action(...args);
        return { ok: true, data: result };
      } catch (err) {
        setError(err);
        return { ok: false, error: err };
      } finally {
        setLoading(false);
      }
    },
    [action]
  );

  return { execute, loading, error, reset: () => setError(null) };
}
