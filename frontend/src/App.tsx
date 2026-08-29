import { Routes, Route, Navigate } from "react-router-dom";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { Tenants } from "./pages/Tenants";
import { Invoices } from "./pages/Invoices";
import {
  Apartments,
  Complaints,
  Locations,
  Payments,
} from "./pages/Operations";
import { Users } from "./pages/Users";
import { Staff, Leases } from "./pages/StaffLeases";
import { Maintenance } from "./pages/Maintenance";
import {
  MyLease,
  MyMaintenance,
  MyPayments,
  MyProfile,
  Register,
} from "./pages/TenantScreens";
import { ProtectedLayout } from "./components/ProtectedLayout";
import { ComingSoon } from "./components/ui";

/** Nav items the desktop app has but the API has no endpoint for. */
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

        {/* Staff-side screens */}
        <Route path="/users" element={<Users />} />
        <Route path="/staff" element={<Staff />} />
        <Route path="/apartments" element={<Apartments />} />
        <Route path="/tenants" element={<Tenants />} />
        <Route path="/leases" element={<Leases />} />
        <Route path="/locations" element={<Locations />} />
        <Route path="/register" element={<Register />} />
        <Route path="/maintenance" element={<Maintenance scope="all" />} />
        <Route path="/complaints" element={<Complaints />} />
        <Route path="/invoices" element={<Invoices />} />
        <Route path="/payments" element={<Payments />} />

        {/* Maintenance Staff — same table, scoped to the signed-in user */}
        <Route path="/requests" element={<Maintenance scope="mine" />} />
        <Route path="/log" element={<Maintenance scope="mine" />} />
        <Route path="/schedule" element={<Maintenance scope="mine" />} />

        {/* Tenant role */}
        <Route path="/my_lease" element={<MyLease />} />
        <Route path="/my_payments" element={<MyPayments />} />
        <Route path="/my_maint" element={<MyMaintenance />} />
        <Route path="/my_profile" element={<MyProfile />} />

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
