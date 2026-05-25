/**
 * Navbar
 *
 * Top navigation bar; uses `NavLink` so the active route is highlighted
 * automatically. Marked sticky in the global stylesheet.
 */
import { NavLink } from "react-router-dom";
import { ROUTES } from "../utils/constants";

const LINKS = [
  { to: ROUTES.DASHBOARD, label: "Dashboard", end: true },
  { to: ROUTES.LIST, label: "Feedback" },
  { to: ROUTES.SUBMIT, label: "Submit" },
  { to: ROUTES.ANALYTICS, label: "Analytics" },
  { to: ROUTES.ETL_UPLOAD, label: "ETL" },
  { to: ROUTES.ETL_HISTORY, label: "ETL History" },
];

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar__inner">
        <NavLink to={ROUTES.DASHBOARD} className="navbar__brand">
          <span className="navbar__brand-mark">F</span>
          <span>Feedback Manager</span>
        </NavLink>
        <nav className="navbar__links" aria-label="Primary">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `navbar__link${isActive ? " is-active" : ""}`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
