import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { getNavItems } from "../lib/nav";
import { Sidebar } from "./components/Sidebar";
import { HeaderBar } from "./components/HeaderBar";

/**
 * Wraps every signed-in screen. Three jobs:
 *  1. wait for the /me check before deciding anything
 *  2. bounce anonymous visitors to /login
 *  3. stop a user reaching a screen their role has no nav item for
 *
 * Point 3 is convenience, not security — the API enforces roles itself via
 * require_roles(). If this check were the only thing standing between a Tenant
 * and DELETE /users/5, it would be worthless, since anyone can edit
 * JavaScript in their own browser. It exists so a user doesn't land on a page
 * that would just fill with 403 errors.
 */
export function ProtectedLayout() {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg-surface">
        <p className="text-sm text-text-body">Loading…</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const key = location.pathname.replace(/^\//, "");
  const allowed = getNavItems(user.role).some((i) => i.key === key);
  if (key && !allowed) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="flex min-h-screen bg-bg-surface">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <HeaderBar />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
