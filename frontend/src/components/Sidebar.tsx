import { NavLink } from "react-router-dom";
import { useAuth } from "../lib/useAuth";
import { getNavItems } from "../lib/nav";

/**
 * Port of Sidebar + NavButton from src/gui/main_window.py.
 *
 * NavButton's active state is a 3px left accent border + accent-glow
 * background + accent text; inactive is transparent with a hover to BG_HOVER.
 * Both states carry the border so the label doesn't shift horizontally when
 * you click between items — the original does the same thing with
 * `border-left: 3px solid transparent`.
 */
export function Sidebar() {
  const { user } = useAuth();
  if (!user) return null;

  const items = getNavItems(user.role);

  return (
    <aside className="flex w-sidebar shrink-0 flex-col bg-bg-sidebar">
      {/* Brand */}
      <div className="flex items-center gap-3 px-5 py-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-accent-dim text-xl font-semibold text-bg-darkest">
          P
        </div>
        <div>
          <p className="text-sm font-semibold tracking-wide text-text-primary">
            PARAGON
          </p>
          <p className="text-[10px] tracking-[0.15em] text-text-secondary uppercase">
            Apartment Management
          </p>
        </div>
      </div>

      <p className="px-5 pt-4 pb-2 text-[10px] font-semibold tracking-[0.15em] text-text-muted uppercase">
        Navigation
      </p>

      <nav className="flex-1 overflow-y-auto pb-4">
        {items.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            className={({ isActive }) =>
              [
                "flex items-center border-l-[3px] py-2.5 pl-[20px] text-[13px] transition-colors",
                isActive
                  ? "border-accent bg-[var(--accent-glow)] font-semibold text-accent"
                  : "border-transparent font-normal text-text-secondary hover:bg-bg-hover hover:text-text-primary",
              ].join(" ")
            }
          >
            <span className="flex-1">{item.label}</span>
            {!item.available && (
              <span className="mr-4 rounded-full bg-bg-hover px-2 py-0.5 text-[9px] tracking-wide text-text-muted uppercase">
                Soon
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Location indicator */}
      <div className="border-t border-[var(--border-subtle)] px-5 py-4">
        <p className="text-[10px] tracking-[0.15em] text-text-muted uppercase">
          Location
        </p>
        <p className="mt-1 text-sm text-text-secondary">
          {user.location_name ?? "All locations"}
        </p>
      </div>
    </aside>
  );
}
