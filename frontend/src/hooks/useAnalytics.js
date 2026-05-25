/**
 * Custom hooks for the analytics dashboard and ETL screens.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import analyticsService from "../services/analyticsService";

function useAsync(loader, deps = []) {
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

export function useAnalyticsSummary() {
  return useAsync(() => analyticsService.summary(), []);
}

export function useEtlRuns(limit = 50) {
  return useAsync(() => analyticsService.etlRuns(limit), [limit]);
}

export function usePrograms() {
  return useAsync(() => analyticsService.programs(), []);
}
