/**
 * FeedbackForm
 *
 * Reusable controlled form for both creating and editing a feedback.
 * Validation mirrors the backend constraints so users get immediate
 * feedback before a network round-trip.
 */
import { useEffect, useState } from "react";
import {
  FIELD_LIMITS,
  RATING_LABELS,
  RATING_VALUES,
} from "../utils/constants";

const EMPTY = {
  participant_name: "",
  program_name: "",
  rating: 5,
  comments: "",
};

function validate(values) {
  const errors = {};

  if (
    !values.participant_name ||
    values.participant_name.trim().length < FIELD_LIMITS.participantNameMin
  ) {
    errors.participant_name = `Name must be at least ${FIELD_LIMITS.participantNameMin} characters.`;
  } else if (
    values.participant_name.length > FIELD_LIMITS.participantNameMax
  ) {
    errors.participant_name = `Name must be at most ${FIELD_LIMITS.participantNameMax} characters.`;
  }

  if (
    !values.program_name ||
    values.program_name.trim().length < FIELD_LIMITS.programNameMin
  ) {
    errors.program_name = `Program name must be at least ${FIELD_LIMITS.programNameMin} characters.`;
  } else if (values.program_name.length > FIELD_LIMITS.programNameMax) {
    errors.program_name = `Program name must be at most ${FIELD_LIMITS.programNameMax} characters.`;
  }

  const numericRating = Number(values.rating);
  if (
    !Number.isInteger(numericRating) ||
    numericRating < 1 ||
    numericRating > 5
  ) {
    errors.rating = "Rating must be an integer between 1 and 5.";
  }

  if (
    !values.comments ||
    values.comments.trim().length < FIELD_LIMITS.commentsMin
  ) {
    errors.comments = `Comments must be at least ${FIELD_LIMITS.commentsMin} characters.`;
  } else if (values.comments.length > FIELD_LIMITS.commentsMax) {
    errors.comments = `Comments must be at most ${FIELD_LIMITS.commentsMax} characters.`;
  }

  return errors;
}

export default function FeedbackForm({
  initialValues,
  onSubmit,
  submitLabel = "Submit",
  busy = false,
  serverErrors = [],
}) {
  const [values, setValues] = useState({ ...EMPTY, ...(initialValues || {}) });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  // Re-sync when editing an existing record loads asynchronously.
  useEffect(() => {
    if (initialValues) {
      setValues((curr) => ({ ...curr, ...initialValues }));
    }
  }, [initialValues]);

  // Merge server-side validation errors keyed by field name.
  useEffect(() => {
    if (!serverErrors || serverErrors.length === 0) return;
    const next = {};
    for (const err of serverErrors) {
      if (err.field) next[err.field] = err.message;
    }
    setErrors((curr) => ({ ...curr, ...next }));
  }, [serverErrors]);

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((curr) => ({
      ...curr,
      [name]: name === "rating" ? Number(value) : value,
    }));
  }

  function handleBlur(event) {
    setTouched((t) => ({ ...t, [event.target.name]: true }));
    setErrors(validate({ ...values, [event.target.name]: event.target.value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    const validation = validate(values);
    setErrors(validation);
    setTouched({
      participant_name: true,
      program_name: true,
      rating: true,
      comments: true,
    });
    if (Object.keys(validation).length === 0) {
      onSubmit({
        participant_name: values.participant_name.trim(),
        program_name: values.program_name.trim(),
        rating: Number(values.rating),
        comments: values.comments.trim(),
      });
    }
  }

  const showError = (field) =>
    touched[field] && errors[field] ? (
      <span className="form__error">{errors[field]}</span>
    ) : null;

  return (
    <form className="form" onSubmit={handleSubmit} noValidate>
      <div className="form__group">
        <label className="form__label" htmlFor="participant_name">
          Participant Name
        </label>
        <input
          id="participant_name"
          name="participant_name"
          className="form__control"
          type="text"
          value={values.participant_name}
          onChange={handleChange}
          onBlur={handleBlur}
          maxLength={FIELD_LIMITS.participantNameMax}
          placeholder="Jane Doe"
          required
        />
        {showError("participant_name")}
      </div>

      <div className="form__group">
        <label className="form__label" htmlFor="program_name">
          Program / Event / Product
        </label>
        <input
          id="program_name"
          name="program_name"
          className="form__control"
          type="text"
          value={values.program_name}
          onChange={handleChange}
          onBlur={handleBlur}
          maxLength={FIELD_LIMITS.programNameMax}
          placeholder="AI Bootcamp 2026"
          required
        />
        {showError("program_name")}
      </div>

      <div className="form__group">
        <label className="form__label" htmlFor="rating">
          Rating
        </label>
        <select
          id="rating"
          name="rating"
          className="form__select"
          value={values.rating}
          onChange={handleChange}
          onBlur={handleBlur}
        >
          {RATING_VALUES.map((value) => (
            <option key={value} value={value}>
              {value} — {RATING_LABELS[value]}
            </option>
          ))}
        </select>
        <span className="form__hint">
          1 = Poor, 2 = Fair, 3 = Good, 4 = Very Good, 5 = Excellent
        </span>
        {showError("rating")}
      </div>

      <div className="form__group">
        <label className="form__label" htmlFor="comments">
          Comments
        </label>
        <textarea
          id="comments"
          name="comments"
          className="form__textarea"
          value={values.comments}
          onChange={handleChange}
          onBlur={handleBlur}
          maxLength={FIELD_LIMITS.commentsMax}
          placeholder="Tell us what you thought..."
          required
        />
        <span className="form__hint">
          {values.comments.length} / {FIELD_LIMITS.commentsMax}
        </span>
        {showError("comments")}
      </div>

      <div className="form__actions">
        <button
          type="submit"
          className="btn btn--primary"
          disabled={busy}
        >
          {busy ? "Saving..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
