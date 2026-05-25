/**
 * Alert
 *
 * Small banner used to surface success / error / info messages.
 */
export default function Alert({ kind = "info", children, onClose }) {
  if (!children) return null;
  return (
    <div className={`alert alert--${kind}`} role="alert">
      <div className="row row--between" style={{ gap: "1rem" }}>
        <div>{children}</div>
        {onClose && (
          <button
            type="button"
            className="btn btn--ghost btn--small"
            onClick={onClose}
            aria-label="Dismiss"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}
