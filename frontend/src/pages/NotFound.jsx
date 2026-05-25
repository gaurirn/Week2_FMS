/**
 * NotFound Page
 *
 * Catch-all route shown when no other route matches.
 */
import { Link } from "react-router-dom";
import { ROUTES } from "../utils/constants";

export default function NotFound() {
  return (
    <div className="empty-state">
      <h3>404 — Page not found</h3>
      <p>The page you’re looking for doesn’t exist.</p>
      <Link to={ROUTES.DASHBOARD} className="btn btn--primary">
        Back to dashboard
      </Link>
    </div>
  );
}
