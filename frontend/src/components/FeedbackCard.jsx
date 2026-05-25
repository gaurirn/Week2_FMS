/**
 * FeedbackCard
 *
 * Compact representation of a single feedback entry used in lists and
 * dashboards. Receives all data via props and delegates actions to
 * callbacks — no business logic lives here.
 */
import { Link } from "react-router-dom";
import { RATING_LABELS, ROUTES } from "../utils/constants";

function formatDate(iso) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

function ratingStars(rating) {
  const filled = "★".repeat(rating);
  const empty = "☆".repeat(5 - rating);
  return `${filled}${empty}`;
}

export default function FeedbackCard({ item, onDelete, showActions = true }) {
  if (!item) return null;
  const ratingLabel = item.rating_label || RATING_LABELS[item.rating];

  return (
    <article className="card card--hoverable">
      <header className="card__header">
        <div>
          <h3 className="card__title">{item.participant_name}</h3>
          <p className="card__subtitle">{item.program_name}</p>
        </div>
        <span className={`rating rating--${item.rating}`}>
          <span className="rating__stars" aria-hidden="true">
            {ratingStars(item.rating)}
          </span>
          {ratingLabel}
        </span>
      </header>

      <div className="card__body">
        <p className="muted" style={{ marginBottom: "0.75rem" }}>
          Submitted {formatDate(item.submitted_at)}
        </p>
        <p style={{ margin: 0 }}>
          {item.comments?.length > 220
            ? `${item.comments.slice(0, 217)}…`
            : item.comments}
        </p>
      </div>

      {showActions && (
        <footer className="card__footer">
          <Link
            to={ROUTES.DETAILS(item.feedback_id)}
            className="btn btn--small"
          >
            View
          </Link>
          <Link
            to={ROUTES.EDIT(item.feedback_id)}
            className="btn btn--small btn--primary"
          >
            Edit
          </Link>
          {onDelete && (
            <button
              type="button"
              className="btn btn--small btn--danger"
              onClick={() => onDelete(item)}
            >
              Delete
            </button>
          )}
        </footer>
      )}
    </article>
  );
}
