/**
 * SubmitFeedback Page
 *
 * Hosts the `FeedbackForm` and wires it up to the create endpoint.
 * Shows success / error banners and resets the form after a successful
 * submission.
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import FeedbackForm from "../components/FeedbackForm";
import Alert from "../components/Alert";
import feedbackService from "../services/feedbackService";
import { useAsyncAction } from "../hooks/useFeedback";
import { ROUTES } from "../utils/constants";

export default function SubmitFeedback() {
  const navigate = useNavigate();
  const [created, setCreated] = useState(null);
  const [serverErrors, setServerErrors] = useState([]);
  const { execute, loading, error } = useAsyncAction(feedbackService.create);

  async function handleSubmit(payload) {
    setServerErrors([]);
    setCreated(null);
    const result = await execute(payload);
    if (result.ok) {
      setCreated(result.data);
    } else {
      setServerErrors(result.error?.fieldErrors || []);
    }
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1 className="page-header__title">Submit feedback</h1>
          <p className="page-header__subtitle">
            Share your thoughts on a program, event or product.
          </p>
        </div>
      </header>

      {created && (
        <Alert kind="success" onClose={() => setCreated(null)}>
          Thanks! Your feedback was submitted successfully.{" "}
          <button
            type="button"
            className="btn btn--small"
            onClick={() => navigate(ROUTES.DETAILS(created.feedback_id))}
          >
            View it
          </button>
        </Alert>
      )}

      {error && (!serverErrors || serverErrors.length === 0) && (
        <Alert kind="danger">{error.message}</Alert>
      )}

      <div className="card" style={{ maxWidth: 720 }}>
        <FeedbackForm
          submitLabel="Submit feedback"
          onSubmit={handleSubmit}
          busy={loading}
          serverErrors={serverErrors}
        />
      </div>
    </section>
  );
}
