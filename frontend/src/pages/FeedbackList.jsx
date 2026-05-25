/**
 * FeedbackList Page
 *
 * Paginated, searchable, filterable list of feedback. Drives the
 * `useFeedbackList` hook with state for search keyword, rating
 * filter and program filter.
 */
import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import FeedbackCard from "../components/FeedbackCard";
import SearchBar from "../components/SearchBar";
import RatingFilter from "../components/RatingFilter";
import ProgramFilter from "../components/ProgramFilter";
import Loader from "../components/Loader";
import Alert from "../components/Alert";
import feedbackService from "../services/feedbackService";
import { useFeedbackList } from "../hooks/useFeedback";
import { DEFAULT_PAGE_SIZE, ROUTES } from "../utils/constants";

export default function FeedbackList() {
  const [keyword, setKeyword] = useState("");
  const [rating, setRating] = useState("");
  const [programName, setProgramName] = useState("");
  const [page, setPage] = useState(1);
  const [deleteError, setDeleteError] = useState(null);
  const [flashMessage, setFlashMessage] = useState(null);

  const { data, loading, error, refetch } = useFeedbackList({
    page,
    pageSize: DEFAULT_PAGE_SIZE,
    keyword,
    rating,
    programName,
  });

  const handleDelete = useCallback(
    async (item) => {
      if (
        !window.confirm(
          `Delete feedback from "${item.participant_name}"? This cannot be undone.`
        )
      ) {
        return;
      }
      try {
        await feedbackService.remove(item.feedback_id);
        setFlashMessage(`Deleted feedback #${item.feedback_id}.`);
        refetch();
      } catch (err) {
        setDeleteError(err.message || "Failed to delete feedback.");
      }
    },
    [refetch]
  );

  const items = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.max(1, Math.ceil(total / DEFAULT_PAGE_SIZE));

  return (
    <section>
      <header className="page-header">
        <div>
          <h1 className="page-header__title">All feedback</h1>
          <p className="page-header__subtitle">
            {total} {total === 1 ? "entry" : "entries"} matching your filters.
          </p>
        </div>
        <Link to={ROUTES.SUBMIT} className="btn btn--primary">
          + New feedback
        </Link>
      </header>

      <div className="toolbar">
        <SearchBar
          value={keyword}
          onChange={(value) => {
            setPage(1);
            setKeyword(value);
          }}
        />
        <RatingFilter
          value={rating}
          onChange={(value) => {
            setPage(1);
            setRating(value);
          }}
        />
        <ProgramFilter
          value={programName}
          onChange={(value) => {
            setPage(1);
            setProgramName(value);
          }}
        />
        {(keyword || rating !== "" || programName) && (
          <button
            type="button"
            className="btn btn--ghost btn--small"
            onClick={() => {
              setKeyword("");
              setRating("");
              setProgramName("");
              setPage(1);
            }}
          >
            Clear filters
          </button>
        )}
      </div>

      {flashMessage && (
        <Alert kind="success" onClose={() => setFlashMessage(null)}>
          {flashMessage}
        </Alert>
      )}
      {deleteError && (
        <Alert kind="danger" onClose={() => setDeleteError(null)}>
          {deleteError}
        </Alert>
      )}
      {error && <Alert kind="danger">{error.message}</Alert>}

      {loading ? (
        <Loader label="Loading feedback..." />
      ) : items.length === 0 ? (
        <div className="empty-state">
          <h3>No feedback found</h3>
          <p>Try adjusting your filters or submit a new feedback.</p>
          <Link to={ROUTES.SUBMIT} className="btn btn--primary">
            Submit feedback
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid--cards">
            {items.map((item) => (
              <FeedbackCard
                key={item.feedback_id}
                item={item}
                onDelete={handleDelete}
              />
            ))}
          </div>

          <nav
            className="row row--between mt-2"
            aria-label="Pagination"
            style={{ marginTop: "1.5rem" }}
          >
            <span className="muted">
              Page {page} of {totalPages}
            </span>
            <div className="row">
              <button
                type="button"
                className="btn btn--small"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                ← Previous
              </button>
              <button
                type="button"
                className="btn btn--small"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                Next →
              </button>
            </div>
          </nav>
        </>
      )}
    </section>
  );
}
