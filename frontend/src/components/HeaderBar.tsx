import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { getNavLabel } from "../lib/nav";

/** Port of HeaderBar from src/gui/main_window.py — 64px tall, white, with the
 *  active nav item's label as the page title. */
export function HeaderBar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  if (!user) return null;

  // The path is the source of truth for which nav item is active, so the title
  // stays correct on a page refresh or a pasted URL, not just on click.
  const key = location.pathname.replace(/^\//, "") || "dashboard";
  const title = getNavLabel(user.role, key);

  const initial = user.name.trim().charAt(0).toUpperCase();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="flex h-header shrink-0 items-center justify-between border-b border-border-light bg-bg-white px-6">
      <h1 className="text-lg font-semibold text-text-dark">{title}</h1>

      <div className="flex items-center gap-4">
        <button
          type="button"
          aria-label="Notifications"
          className="flex h-9 w-9 items-center justify-center rounded-[10px] text-text-body transition-colors hover:bg-bg-surface focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            aria-hidden="true"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
        </button>

        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-accent/15 text-sm font-semibold text-accent">
            {initial}
          </div>
          <div className="leading-tight">
            <p className="text-sm font-medium text-text-dark">{user.name}</p>
            <p className="text-xs text-text-body">
              {user.location_name
                ? `${user.role} — ${user.location_name}`
                : user.role}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleLogout}
          className="h-9 rounded-[10px] border border-danger px-4 text-sm font-medium text-danger transition-colors hover:bg-danger hover:text-bg-white focus-visible:ring-2 focus-visible:ring-danger focus-visible:ring-offset-2 focus-visible:outline-none"
        >
          Log out
        </button>
      </div>
    </header>
  );
}
