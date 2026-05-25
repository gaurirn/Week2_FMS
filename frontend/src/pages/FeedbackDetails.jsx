/**
 * FeedbackDetails Page
 *
 * Read-only view of a single feedback. Offers edit/delete actions.
 */
import { Link, useNavigate, useParams } from "react-router-dom";
import Loader from "../components/Loader";
import Alert from "../components/Alert";
import feedbackService from "../services/feedbackService";
import { useFeedbackItem } from "../hooks/useFeedback";
import { RATING_LABELS, ROUTES } from "../utils/constants";

function formatDate(iso) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function FeedbackDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data, loading, error } = useFeedbackItem(id);

  if (loading) return <Loader label="Loading feedback..." />;
  if (error) return <Alert kind="danger">{error.message}</Alert>;
  if (!data) {
    return (
      <div className="empty-state">
        <h3>Feedback not found</h3>
        <Link to={ROUTES.LIST} className="btn btn--primary">
          Back to list
        </Link>
      </div>
    );
  }

  async function handleDelete() {
    if (!window.confirm("Delete this feedback? This cannot be undone.")) return;
    try {
      await feedbackService.remove(data.feedback_id);
      navigate(ROUTES.LIST);
    } catch (err) {
      window.alert(err.message || "Failed to delete feedback.");
    }
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1 className="page-header__title">{data.participant_name}</h1>
          <p className="page-header__subtitle">{data.program_name}</p>
        </div>
        <div className="row">
          <Link to={ROUTES.LIST} className="btn">
            ← Back
          </Link>
          <Link to={ROUTES.EDIT(data.feedback_id)} className="btn btn--primary">
            Edit
          </Link>
          <button type="button" className="btn btn--danger" onClick={handleDelete}>
            Delete
          </button>
        </div>
      </header>

      <div className="card" style={{ maxWidth: 760 }}>
        <div className="row row--between mb-2">
          <span className={`rating rating--${data.rating}`}>
            {data.rating_label || RATING_LABELS[data.rating]}
          </span>
          <span className="muted">Submitted {formatDate(data.submitted_at)}</span>
        </div>
        <h3 style={{ marginTop: "1rem" }}>Comments</h3>
        <p style={{ whiteSpace: "pre-wrap" }}>{data.comments}</p>

        <hr style={{ border: 0, borderTop: "1px solid var(--color-border)", margin: "1.25rem 0" }} />
        <dl style={{ display: "grid", gap: "0.4rem" }}>
          <div className="row row--between">
            <dt className="muted">Feedback ID</dt>
            <dd style={{ margin: 0 }}>{data.feedback_id}</dd>
          </div>
          <div className="row row--between">
            <dt className="muted">Rating</dt>
            <dd style={{ margin: 0 }}>
              {data.rating} ({data.rating_label || RATING_LABELS[data.rating]})
            </dd>
          </div>
        </dl>
      </div>
    </section>
  );
}
