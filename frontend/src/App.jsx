import { Routes, Route, Navigate } from "react-router-dom";
import AuthLayout from "./components/layout/AuthLayout";
import AppLayout from "./components/layout/AppLayout";
import ProtectedRoute from "./components/layout/ProtectedRoute";

import Landing from "./pages/Landing";
import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import VerifyEmail from "./pages/auth/VerifyEmail";

import Dashboard from "./pages/Dashboard";
import DigitalTwin from "./pages/DigitalTwin";
import Goals from "./pages/Goals";
import Habits from "./pages/Habits";
import Journal from "./pages/Journal";
import Simulations from "./pages/Simulations";
import Chatbot from "./pages/Chatbot";
import Analytics from "./pages/Analytics";
import Notifications from "./pages/Notifications";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />

      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/app" element={<Navigate to="/app/dashboard" replace />} />
          <Route path="/app/dashboard" element={<Dashboard />} />
          <Route path="/app/twin" element={<DigitalTwin />} />
          <Route path="/app/goals" element={<Goals />} />
          <Route path="/app/habits" element={<Habits />} />
          <Route path="/app/journal" element={<Journal />} />
          <Route path="/app/simulations" element={<Simulations />} />
          <Route path="/app/chatbot" element={<Chatbot />} />
          <Route path="/app/analytics" element={<Analytics />} />
          <Route path="/app/notifications" element={<Notifications />} />
          <Route path="/app/settings" element={<Settings />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
