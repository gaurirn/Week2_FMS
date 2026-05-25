/**
 * EtlUpload Page (Phase 2)
 *
 * Lets the user pick a CSV/Excel file (or run the bundled sample
 * dataset) and triggers the ETL pipeline. Shows a detailed result
 * card with extracted/transformed/loaded/rejected counters.
 */
import { useState } from "react";
import { Link } from "react-router-dom";
import Alert from "../components/Alert";
import analyticsService from "../services/analyticsService";
import { ROUTES } from "../utils/constants";

const ACCEPT = ".csv,.xlsx,.xls,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";

export default function EtlUpload() {
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState("replace");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  function pick(e) {
    setError(null);
    setResult(null);
    setFile(e.target.files?.[0] ?? null);
  }

  async function runUpload() {
    if (!file) {
      setError({ message: "Please choose a CSV or Excel file." });
      return;
    }
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyticsService.uploadAndRun(file, mode);
      setResult(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  async function runSample() {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyticsService.runSample(mode);
      setResult(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1 className="page-header__title">ETL — upload feedback dataset</h1>
          <p className="page-header__subtitle">
            Upload a CSV or Excel file with feedback rows. The pipeline will
            clean, validate, deduplicate, and load it into the analytics
            tables.
          </p>
        </div>
        <div className="row">
          <Link to={ROUTES.ETL_HISTORY} className="btn">
            View ETL history
          </Link>
          <Link to={ROUTES.ANALYTICS} className="btn btn--primary">
            Open Analytics
          </Link>
        </div>
      </header>

      {error && <Alert kind="danger">{error.message}</Alert>}

      <div className="grid grid--cols-2">
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Upload a file</h3>
          <div className="form__group">
            <label className="form__label" htmlFor="file">
              CSV or Excel file
            </label>
            <input
              id="file"
              className="form__control"
              type="file"
              accept={ACCEPT}
              onChange={pick}
              disabled={busy}
            />
            <span className="form__hint">
              Expected columns:{" "}
              <code>participant_name, program_name, rating, comments, submitted_at</code>
              . Header variants like “name”, “score”, “feedback”, “timestamp”
              are also accepted.
            </span>
          </div>

          <div className="form__group">
            <label className="form__label" htmlFor="mode">
              Load mode
            </label>
            <select
              id="mode"
              className="form__select"
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              disabled={busy}
            >
              <option value="replace">Replace — clear existing analytics</option>
              <option value="append">Append — keep existing rows</option>
            </select>
          </div>

          <div className="form__actions">
            <button
              type="button"
              className="btn btn--primary"
              onClick={runUpload}
              disabled={busy || !file}
            >
              {busy ? "Running ETL..." : "Run ETL"}
            </button>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0 }}>No file handy?</h3>
          <p className="muted">
            Use the bundled sample dataset (118 rows including duplicates,
            invalid ratings and missing fields) so you can see the ETL clean
            real-world-style messy data.
          </p>
          <div className="form__actions">
            <button
              type="button"
              className="btn"
              onClick={runSample}
              disabled={busy}
            >
              {busy ? "Running..." : "Run on bundled sample"}
            </button>
          </div>
        </div>
      </div>

      {result && (
        <div className="card mt-2">
          <h3 style={{ marginTop: 0 }}>
            ETL run #{result.run_id} ·{" "}
            <span
              className={`rating rating--${result.status === "success" ? 5 : 1}`}
            >
              {result.status}
            </span>
          </h3>
          <p className="muted">
            Source: <code>{result.source_filename}</code> ·{" "}
            {result.duration_ms} ms
          </p>
          <div className="grid grid--cols-3">
            <div className="stat">
              <div className="stat__label">Extracted</div>
              <div className="stat__value">{result.rows_extracted}</div>
            </div>
            <div className="stat">
              <div className="stat__label">Transformed</div>
              <div className="stat__value">{result.rows_transformed}</div>
            </div>
            <div className="stat">
              <div className="stat__label">Loaded</div>
              <div className="stat__value">{result.rows_loaded}</div>
            </div>
          </div>
          <div className="grid grid--cols-3 mt-2">
            <div className="stat">
              <div className="stat__label">Duplicates removed</div>
              <div className="stat__value" style={{ color: "#f59e0b" }}>
                {result.duplicates_removed}
              </div>
            </div>
            <div className="stat">
              <div className="stat__label">Invalid ratings dropped</div>
              <div className="stat__value" style={{ color: "#ef4444" }}>
                {result.invalid_ratings_dropped}
              </div>
            </div>
            <div className="stat">
              <div className="stat__label">Missing fields dropped</div>
              <div className="stat__value" style={{ color: "#ef4444" }}>
                {result.missing_fields_dropped}
              </div>
            </div>
          </div>
          <div className="form__actions" style={{ marginTop: "1rem" }}>
            <Link to={ROUTES.ANALYTICS} className="btn btn--primary">
              See updated analytics →
            </Link>
          </div>
        </div>
      )}
    </section>
  );
}
