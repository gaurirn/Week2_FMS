/**
 * Analytics Page (Phase 2)
 *
 * Reads the aggregates produced by the ETL pipeline and renders:
 *   - summary tiles (total responses, average rating, distinct programs,
 *     last ETL run)
 *   - sentiment breakdown
 *   - rating distribution bar chart
 *   - monthly timeline line chart
 *   - top / bottom programs
 *   - per-program table
 *   - download buttons for CSV + XLSX reports
 */
import { Link } from "react-router-dom";
import Alert from "../components/Alert";
import BarChart from "../components/BarChart";
import LineChart from "../components/LineChart";
import Loader from "../components/Loader";
import analyticsService from "../services/analyticsService";
import { useAnalyticsSummary, usePrograms } from "../hooks/useAnalytics";
import { ROUTES } from "../utils/constants";

function formatDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function Analytics() {
  const summary = useAnalyticsSummary();
  const programs = usePrograms();

  if (summary.loading || programs.loading) {
    return <Loader label="Loading analytics..." />;
  }
  if (summary.error) {
    return <Alert kind="danger">{summary.error.message}</Alert>;
  }
  const s = summary.data;

  // Empty-state: ETL hasn't been run yet.
  if (!s || s.total_responses === 0) {
    return (
      <section>
        <header className="page-header">
          <div>
            <h1 className="page-header__title">Analytics</h1>
            <p className="page-header__subtitle">
              Cleaned analytics powered by the ETL pipeline (Phase 2).
            </p>
          </div>
        </header>
        <div className="alert alert--info">
          No analytics yet — run the ETL pipeline first.
          <div className="row" style={{ marginTop: "0.75rem" }}>
            <Link to={ROUTES.ETL_UPLOAD} className="btn btn--primary">
              Open ETL screen →
            </Link>
          </div>
        </div>
      </section>
    );
  }

  const ratingChartData = s.rating_distribution.map((r) => ({
    label: `${r.rating}★`,
    value: r.count,
  }));
  const sentimentChartData = [
    { label: "Positive", value: s.sentiment.positive, accent: "#10b981" },
    { label: "Neutral", value: s.sentiment.neutral, accent: "#f59e0b" },
    { label: "Negative", value: s.sentiment.negative, accent: "#ef4444" },
  ];
  const timelineData = s.timeline.map((p) => ({
    period: p.period,
    value: p.total,
  }));

  return (
    <section>
      <header className="page-header">
        <div>
          <h1 className="page-header__title">Analytics</h1>
          <p className="page-header__subtitle">
            Cleaned data from the ETL pipeline · last refreshed{" "}
            {formatDate(s.last_etl_at)}.
          </p>
        </div>
        <div className="row">
          <a
            className="btn"
            href={analyticsService.reportCsvUrl()}
            download="feedback_analytics.csv"
          >
            ⬇ Download CSV
          </a>
          <a
            className="btn"
            href={analyticsService.reportXlsxUrl()}
            download="feedback_analytics.xlsx"
          >
            ⬇ Download Excel
          </a>
          <Link to={ROUTES.ETL_UPLOAD} className="btn btn--primary">
            Run ETL
          </Link>
        </div>
      </header>

      {/* Summary tiles */}
      <div className="grid grid--cols-3" style={{ marginBottom: "1.5rem" }}>
        <div className="stat">
          <div className="stat__label">Total responses</div>
          <div className="stat__value">{s.total_responses}</div>
        </div>
        <div className="stat">
          <div className="stat__label">Average rating</div>
          <div className="stat__value">{s.average_rating.toFixed(2)}</div>
        </div>
        <div className="stat">
          <div className="stat__label">Programs covered</div>
          <div className="stat__value">{s.distinct_programs}</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid--cols-2" style={{ marginBottom: "1.5rem" }}>
        <div className="card">
          <h3 style={{ marginTop: 0, marginBottom: "1rem", fontSize: "1rem", color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600 }}>Rating distribution</h3>
          <BarChart data={ratingChartData} height={200} />
        </div>
        <div className="card">
          <h3 style={{ marginTop: 0, marginBottom: "1rem", fontSize: "1rem", color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600 }}>Sentiment breakdown</h3>
          <BarChart data={sentimentChartData} height={200} />
        </div>
      </div>

      <div className="card mb-2">
        <h3 style={{ marginTop: 0, marginBottom: "1rem", fontSize: "1rem", color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600 }}>Monthly trend</h3>
        <LineChart data={timelineData} height={260} />
      </div>

      {/* Top / bottom */}
      <div className="grid grid--cols-2" style={{ marginBottom: "1.5rem" }}>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Top programs</h3>
          {s.top_programs.length === 0 ? (
            <p className="muted">No programs yet.</p>
          ) : (
            <ul style={{ paddingLeft: "1.2rem", margin: 0 }}>
              {s.top_programs.map((p) => (
                <li key={p.program_name} style={{ marginBottom: "0.35rem" }}>
                  <strong>{p.program_name}</strong>{" "}
                  <span className="muted">
                    — {p.average_rating.toFixed(2)}★ across {p.total_responses}{" "}
                    responses
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Programs needing attention</h3>
          {s.bottom_programs.length === 0 ? (
            <p className="muted">No programs yet.</p>
          ) : (
            <ul style={{ paddingLeft: "1.2rem", margin: 0 }}>
              {s.bottom_programs.map((p) => (
                <li key={p.program_name} style={{ marginBottom: "0.35rem" }}>
                  <strong>{p.program_name}</strong>{" "}
                  <span className="muted">
                    — {p.average_rating.toFixed(2)}★ ({p.negative_count}{" "}
                    negative reviews)
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Per-program table */}
      <div className="card">
        <h3 style={{ marginTop: 0 }}>All programs</h3>
        {programs.error ? (
          <Alert kind="danger">{programs.error.message}</Alert>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "0.92rem",
              }}
            >
              <thead>
                <tr style={{ textAlign: "left" }}>
                  <th style={{ padding: "0.5rem 0.4rem" }}>Program</th>
                  <th style={{ padding: "0.5rem 0.4rem" }}>Responses</th>
                  <th style={{ padding: "0.5rem 0.4rem" }}>Avg rating</th>
                  <th style={{ padding: "0.5rem 0.4rem" }}>Positive</th>
                  <th style={{ padding: "0.5rem 0.4rem" }}>Neutral</th>
                  <th style={{ padding: "0.5rem 0.4rem" }}>Negative</th>
                </tr>
              </thead>
              <tbody>
                {(programs.data || []).map((p) => (
                  <tr key={p.program_name} style={{ borderTop: "1px solid var(--color-border)" }}>
                    <td style={{ padding: "0.5rem 0.4rem" }}>
                      {p.program_name}
                    </td>
                    <td style={{ padding: "0.5rem 0.4rem" }}>
                      {p.total_responses}
                    </td>
                    <td style={{ padding: "0.5rem 0.4rem" }}>
                      {p.average_rating.toFixed(2)}
                    </td>
                    <td style={{ padding: "0.5rem 0.4rem", color: "#065f46" }}>
                      {p.positive_count}
                    </td>
                    <td style={{ padding: "0.5rem 0.4rem", color: "#92400e" }}>
                      {p.neutral_count}
                    </td>
                    <td style={{ padding: "0.5rem 0.4rem", color: "#991b1b" }}>
                      {p.negative_count}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
