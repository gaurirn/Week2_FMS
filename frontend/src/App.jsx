/**
 * App
 *
 * Top-level layout: navbar, routed page content and the footer.
 */
import Navbar from "./components/Navbar";
import AppRoutes from "./routes";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="container" role="main">
        <AppRoutes />
      </main>
      <footer className="footer">
        © {new Date().getFullYear()} Feedback Management System — Capstone Project
      </footer>
    </div>
  );
}
