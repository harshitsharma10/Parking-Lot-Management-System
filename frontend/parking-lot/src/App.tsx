import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute, AdminRoute } from "./components/Routes";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import DynamicEntry from "./pages/user/DynamicEntry";
import QueueEntry from "./pages/user/QueueEntry";
import MySessions from "./pages/user/MySessions";
import Ticket from "./pages/user/Ticket";
import SlotManager from "./pages/admin/SlotManager";
import ActiveSessions from "./pages/admin/ActiveSessions";
import WalkIn from "./pages/admin/WalkIn";

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#0f0f0f]">
      <Navbar />
      <main className="p-6">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/" element={<Navigate to="/login" replace />} />

          <Route element={<ProtectedRoute />}>
            <Route
              path="/dashboard"
              element={
                <Layout>
                  <Dashboard />
                </Layout>
              }
            />
            <Route
              path="/dynamic-entry"
              element={
                <Layout>
                  <DynamicEntry />
                </Layout>
              }
            />
            <Route
              path="/queue-entry"
              element={
                <Layout>
                  <QueueEntry />
                </Layout>
              }
            />
            <Route
              path="/my-sessions"
              element={
                <Layout>
                  <MySessions />
                </Layout>
              }
            />
            <Route
              path="/ticket/:sessionId"
              element={
                <Layout>
                  <Ticket />
                </Layout>
              }
            />
          </Route>

          <Route element={<AdminRoute />}>
            <Route
              path="/admin/slots"
              element={
                <Layout>
                  <SlotManager />
                </Layout>
              }
            />
            <Route
              path="/admin/sessions"
              element={
                <Layout>
                  <ActiveSessions />
                </Layout>
              }
            />
            <Route
              path="/admin/walk-in"
              element={
                <Layout>
                  <WalkIn />
                </Layout>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
