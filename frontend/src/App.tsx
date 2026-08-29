import { Routes, Route, Navigate } from "react-router-dom";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { ProtectedLayout } from "./components/ProtectedLayout";
import { ComingSoon } from "./components/ui";
import { Tenants } from "./pages/Tenants";
import { Invoices } from "./pages/Invoices";
import { Payments, Complaints, Locations, Apartments } from "./pages/Operations";

// inside <Route element={<ProtectedLayout />}>:

/**
 * Placeholder pages for screens not built yet. Phase 3 replaces these one at a
 * time with real components — keeping them as named routes now means the
 * sidebar links all work rather than dead-ending on a redirect.
 */
const PLACEHOLDER: Record<string, string> = {
  users: "User Management",
  staff: "Staff Members",
  leases: "Lease Tracking",
  register: "Register Tenant",
  maintenance: "Maintenance",
  requests: "Maintenance Requests",
  log: "Log Resolution",
  schedule: "Schedule",
  my_lease: "My Lease",
  my_maint: "Maintenance",
  my_profile: "Profile",
};

/** Nav items with no backing API endpoint — these keep the ComingSoon state
 *  permanently until routes exist for them. */
const UNAVAILABLE: Record<string, string> = {
  reports: "Reports",
  settings: "Settings",
  occupancy: "Occupancy",
  expand: "Expand Business",
  late: "Late Payments",
  fin_reports: "Financial Reports",
  notifications: "Notifications",
};

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<ProtectedLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/tenants" element={<Tenants />} />
        <Route path="/invoices" element={<Invoices />} />
        <Route path="/payments" element={<Payments />} />
        <Route path="/complaints" element={<Complaints />} />
        <Route path="/locations" element={<Locations />} />
        <Route path="/apartments" element={<Apartments />} />

        {Object.entries(PLACEHOLDER).map(([key, label]) => (
          <Route
            key={key}
            path={`/${key}`}
            element={<ComingSoon label={label} />}
          />
        ))}

        {Object.entries(UNAVAILABLE).map(([key, label]) => (
          <Route
            key={key}
            path={`/${key}`}
            element={<ComingSoon label={label} />}
          />
        ))}
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
