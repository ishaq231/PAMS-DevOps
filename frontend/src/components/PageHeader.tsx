import type { ReactNode } from "react";

export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-5 flex items-start justify-between gap-4">
      <div>
        <h2 className="text-xl font-semibold text-text-dark">{title}</h2>
        {subtitle && <p className="mt-1 text-sm text-text-body">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

/** MySQL DATE columns come back as ISO strings; show them the way the desktop
 *  app does rather than dumping the raw value with a T and a timezone on it. */
export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function formatMoney(value: number | string | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return String(value);
  return `£${n.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function fullName(row: { fname?: string; lname?: string }): string {
  return [row.fname, row.lname].filter(Boolean).join(" ") || "—";
}
