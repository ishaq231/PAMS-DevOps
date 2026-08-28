import type { Role } from "./types";

/**
 * Ported verbatim from _get_nav_items() in src/gui/main_window.py.
 * Order and labels match the desktop app exactly — don't "tidy" them.
 *
 * `available: false` means the desktop app has this screen but the API has no
 * endpoint behind it. Those render a "coming soon" state rather than being
 * hidden, so the web app's navigation still mirrors the desktop app.
 */

export type NavItem = {
  key: string;
  label: string;
  path: string;
  available: boolean;
};

const item = (
  key: string,
  label: string,
  available = true,
): NavItem => ({ key, label, path: `/${key}`, available });

const dashboard = item("dashboard", "Dashboard");

const roleNav: Record<Role, NavItem[]> = {
  Administrator: [
    item("users", "User Management"),
    item("apartments", "Apartments"),
    item("tenants", "Tenants"),
    item("staff", "Staff Members"),
    item("leases", "Lease Tracking"),
    item("reports", "Reports", false),
    item("settings", "Settings", false),
  ],
  Manager: [
    item("occupancy", "Occupancy", false),
    item("expand", "Expand Business", false),
    item("locations", "Locations"),
    item("users", "User Management"),
    item("apartments", "Apartments"),
    item("tenants", "Tenants"),
    item("leases", "Lease Tracking"),
    item("reports", "Reports", false),
    item("register", "Register Tenant"),
    item("maintenance", "Maintenance"),
    item("complaints", "Complaints"),
    item("invoices", "Invoices"),
    item("payments", "Payments"),
    item("late", "Late Payments", false),
    item("fin_reports", "Financial Reports", false),
    item("requests", "Maint. Requests"),
    item("log", "Log Resolution"),
    item("schedule", "Schedule"),
    item("settings", "Settings", false),
  ],
  "Front Desk Staff": [
    item("register", "Register Tenant"),
    item("tenants", "Tenant Info"),
    item("maintenance", "Maintenance"),
    item("complaints", "Complaints"),
  ],
  "Finance Manager": [
    item("invoices", "Invoices"),
    item("payments", "Payments"),
    item("late", "Late Payments", false),
    item("fin_reports", "Financial Reports", false),
  ],
  "Maintenance Staff": [
    item("requests", "My Requests"),
    item("log", "Log Resolution"),
    item("schedule", "Schedule"),
  ],
  Tenant: [
    item("my_lease", "My Lease"),
    item("my_payments", "Payments"),
    item("my_maint", "Maintenance"),
    item("my_profile", "Profile"),
    item("notifications", "Notifications", false),
  ],
};

export function getNavItems(role: Role): NavItem[] {
  return [dashboard, ...(roleNav[role] ?? [])];
}

/** Used by the header bar as the page title / breadcrumb. */
export function getNavLabel(role: Role, key: string): string {
  return getNavItems(role).find((i) => i.key === key)?.label ?? "Dashboard";
}
