/**
 * EditFeedback Page
 *
 * Loads an existing feedback, pre-fills the reusable `FeedbackForm`,
 * and PUTs the changes back to the API.
 */
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import FeedbackForm from "../components/FeedbackForm";
import Loader from "../components/Loader";
import Alert from "../components/Alert";
import feedbackService from "../services/feedbackService";
import { useAsyncAction, useFeedbackItem } from "../hooks/useFeedback";
import { ROUTES } from "../utils/constants";

export default function EditFeedback() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data, loading, error } = useFeedbackItem(id);
  const [serverErrors, setServerErrors] = useState([]);
  const {
    execute,
    loading: saving,
    error: saveError,
  } = useAsyncAction((payload) => feedbackService.update(id, payload));

  if (loading) return <Loader label="Loading feedback..." />;
  if (error) return <Alert kind="danger">{error.message}</Alert>;
  if (!data) {
    return (
      <div className="empty-state">
        <h3>Feedback not found</h3>
      </div>
    );
  }

  async function handleSubmit(payload) {
    setServerErrors([]);
    const result = await execute(payload);
    if (result.ok) {
      navigate(ROUTES.DETAILS(id));
    } else {
      setServerErrors(result.error?.fieldErrors || []);
    }
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1 className="page-header__title">Edit feedback</h1>
          <p className="page-header__subtitle">
            Update the rating, comments or other details.
          </p>
        </div>
      </header>

      {saveError && (!serverErrors || serverErrors.length === 0) && (
        <Alert kind="danger">{saveError.message}</Alert>
      )}

      <div className="card" style={{ maxWidth: 720 }}>
        <FeedbackForm
          initialValues={{
            participant_name: data.participant_name,
            program_name: data.program_name,
            rating: data.rating,
            comments: data.comments,
          }}
          submitLabel="Save changes"
          onSubmit={handleSubmit}
          busy={saving}
          serverErrors={serverErrors}
        />
      </div>
    </section>
  );
}
