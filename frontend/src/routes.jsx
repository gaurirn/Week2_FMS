/**
 * Application Routing Table
 *
 * Centralised so `App.jsx` stays presentation-only.
 */
import { Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import SubmitFeedback from "./pages/SubmitFeedback";
import FeedbackList from "./pages/FeedbackList";
import FeedbackDetails from "./pages/FeedbackDetails";
import EditFeedback from "./pages/EditFeedback";
import Analytics from "./pages/Analytics";
import EtlUpload from "./pages/EtlUpload";
import EtlHistory from "./pages/EtlHistory";
import NotFound from "./pages/NotFound";
import { ROUTES } from "./utils/constants";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path={ROUTES.DASHBOARD} element={<Dashboard />} />
      <Route path={ROUTES.SUBMIT} element={<SubmitFeedback />} />
      <Route path={ROUTES.LIST} element={<FeedbackList />} />
      <Route path="/feedback/:id" element={<FeedbackDetails />} />
      <Route path="/feedback/:id/edit" element={<EditFeedback />} />
      <Route path={ROUTES.ANALYTICS} element={<Analytics />} />
      <Route path={ROUTES.ETL_UPLOAD} element={<EtlUpload />} />
      <Route path={ROUTES.ETL_HISTORY} element={<EtlHistory />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
