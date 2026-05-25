/**
 * RatingFilter
 *
 * Dropdown that lets the user filter the feedback list by an exact
 * rating value, or clear the filter entirely.
 */
import { RATING_LABELS, RATING_VALUES } from "../utils/constants";

export default function RatingFilter({ value = "", onChange }) {
  return (
    <select
      className="form__select"
      style={{ maxWidth: 200 }}
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      aria-label="Filter by rating"
    >
      <option value="">All ratings</option>
      {RATING_VALUES.map((rating) => (
        <option key={rating} value={rating}>
          {rating} — {RATING_LABELS[rating]}
        </option>
      ))}
    </select>
  );
}
