/**
 * EtlHistory Page (Phase 2)
 *
 * Lists every previous ETL run with counters and status so operators
 * can audit what happened.
 */
import { Link } from "react-router-dom";
import Alert from "../components/Alert";
import Loader from "../components/Loader";
import { useEtlRuns } from "../hooks/useAnalytics";
import { ROUTES } from "../utils/constants";

function formatDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function EtlHistory() {
  const { data, loading, error, refetch } = useEtlRuns(100);

  return (
    <section>
      <header className="page-header">
        <div>
          <h1 className="page-header__title">ETL history</h1>
          <p className="page-header__subtitle">
            Every ETL run, in reverse chronological order.
          </p>
        </div>
        <div className="row">
          <button type="button" className="btn" onClick={refetch}>
            ⟳ Refresh
          </button>
          <Link to={ROUTES.ETL_UPLOAD} className="btn btn--primary">
            Run new ETL
          </Link>
        </div>
      </header>

      {error && <Alert kind="danger">{error.message}</Alert>}
      {loading && <Loader label="Loading history..." />}

      {!loading && (data?.items?.length ?? 0) === 0 && (
        <div className="empty-state">
          <h3>No ETL runs yet</h3>
          <p>Run the ETL pipeline to populate this list.</p>
          <Link to={ROUTES.ETL_UPLOAD} className="btn btn--primary">
            Run ETL
          </Link>
        </div>
      )}

      {!loading && (data?.items?.length ?? 0) > 0 && (
        <div className="card" style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: "0.92rem",
            }}
          >
            <thead>
              <tr style={{ textAlign: "left" }}>
                <th style={{ padding: "0.5rem 0.4rem" }}>#</th>
                <th style={{ padding: "0.5rem 0.4rem" }}>When</th>
                <th style={{ padding: "0.5rem 0.4rem" }}>Source</th>
                <th style={{ padding: "0.5rem 0.4rem" }}>Status</th>
                <th style={{ padding: "0.5rem 0.4rem" }}>Extracted</th>
                <th style={{ padding: "0.5rem 0.4rem" }}>Loaded</th>
                <th style={{ padding: "0.5rem 0.4rem" }}>Dups</th>
                <th style={{ padding: "0.5rem 0.4rem" }}>Bad ratings</th>
                <th style={{ padding: "0.5rem 0.4rem" }}>Missing</th>
                <th style={{ padding: "0.5rem 0.4rem" }}>Duration</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((r) => (
                <tr
                  key={r.run_id}
                  style={{ borderTop: "1px solid var(--color-border)" }}
                >
                  <td style={{ padding: "0.5rem 0.4rem" }}>{r.run_id}</td>
                  <td style={{ padding: "0.5rem 0.4rem" }}>{formatDate(r.run_at)}</td>
                  <td style={{ padding: "0.5rem 0.4rem" }}>
                    <code>{r.source_filename}</code>{" "}
                    <span className="muted">({r.source_kind})</span>
                  </td>
                  <td style={{ padding: "0.5rem 0.4rem" }}>
                    <span
                      className={`rating rating--${r.status === "success" ? 5 : 1}`}
                    >
                      {r.status}
                    </span>
                  </td>
                  <td style={{ padding: "0.5rem 0.4rem" }}>{r.rows_extracted}</td>
                  <td style={{ padding: "0.5rem 0.4rem" }}>{r.rows_loaded}</td>
                  <td style={{ padding: "0.5rem 0.4rem" }}>
                    {r.duplicates_removed}
                  </td>
                  <td style={{ padding: "0.5rem 0.4rem" }}>
                    {r.invalid_ratings_dropped}
                  </td>
                  <td style={{ padding: "0.5rem 0.4rem" }}>
                    {r.missing_fields_dropped}
                  </td>
                  <td style={{ padding: "0.5rem 0.4rem" }}>
                    {r.duration_ms} ms
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
