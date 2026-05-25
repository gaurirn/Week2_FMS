/**
 * Dashboard Page
 *
 * Aggregated overview: total submissions, average rating, distribution
 * across ratings, and the most recent feedback entries.
 */
import { Link } from "react-router-dom";
import FeedbackCard from "../components/FeedbackCard";
import Loader from "../components/Loader";
import Alert from "../components/Alert";
import { useFeedbackStats } from "../hooks/useFeedback";
import { RATING_LABELS, ROUTES } from "../utils/constants";

export default function Dashboard() {
  const { data: stats, loading, error, refetch } = useFeedbackStats(5);

  if (loading) return <Loader label="Loading dashboard..." />;
  if (error) {
    return (
      <Alert kind="danger">
        {error.message || "Failed to load dashboard."}
        <button
          type="button"
          className="btn btn--small"
          style={{ marginLeft: "0.75rem" }}
          onClick={refetch}
        >
          Retry
        </button>
      </Alert>
    );
  }

  const distribution = stats?.rating_distribution || {};

  return (
    <section>
      <header className="page-header">
        <div>
          <h1 className="page-header__title">Dashboard</h1>
          <p className="page-header__subtitle">
            A quick snapshot of feedback submissions across all programs.
          </p>
        </div>
        <Link to={ROUTES.SUBMIT} className="btn btn--primary">
          + New feedback
        </Link>
      </header>

      <div className="grid grid--cols-3">
        <div className="stat">
          <div className="stat__label">Total feedback</div>
          <div className="stat__value">{stats?.total_feedback ?? 0}</div>
        </div>
        <div className="stat">
          <div className="stat__label">Average rating</div>
          <div className="stat__value">
            {stats?.average_rating?.toFixed
              ? stats.average_rating.toFixed(2)
              : stats?.average_rating ?? "0.00"}
          </div>
        </div>
        <div className="stat">
          <div className="stat__label">Highest bucket</div>
          <div className="stat__value">
            {(() => {
              const entries = Object.entries(distribution);
              if (entries.length === 0) return "—";
              const [rating] = entries.reduce(
                (best, curr) =>
                  Number(curr[1]) > Number(best[1]) ? curr : best,
                ["0", 0]
              );
              return Number(rating) > 0
                ? `${RATING_LABELS[Number(rating)]}`
                : "—";
            })()}
          </div>
        </div>
      </div>

      <h2 style={{ marginTop: "2rem" }}>Rating distribution</h2>
      <div className="grid grid--cols-3" style={{ marginBottom: "2rem" }}>
        {[1, 2, 3, 4, 5].map((rating) => (
          <div key={rating} className="card">
            <div className="row row--between">
              <span className={`rating rating--${rating}`}>
                {RATING_LABELS[rating]}
              </span>
              <strong style={{ fontSize: "1.4rem" }}>
                {distribution[rating] ?? 0}
              </strong>
            </div>
          </div>
        ))}
      </div>

      <h2>Recent feedback</h2>
      {stats?.recent_feedback?.length ? (
        <div className="grid grid--cards">
          {stats.recent_feedback.map((item) => (
            <FeedbackCard
              key={item.feedback_id}
              item={item}
              showActions={false}
            />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <h3>No feedback yet</h3>
          <p>Submit your first feedback to populate the dashboard.</p>
          <Link to={ROUTES.SUBMIT} className="btn btn--primary">
            Submit feedback
          </Link>
        </div>
      )}
    </section>
  );
}
