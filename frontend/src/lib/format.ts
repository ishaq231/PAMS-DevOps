/**
 * Pulled out of PageHeader.tsx deliberately: React Fast Refresh (the thing
 * that lets Vite hot-swap a component without a full page reload) only works
 * reliably on files that export components and nothing else. A file mixing
 * a component export with plain function exports defeats that, so ESLint's
 * react-refresh rule flags it. Splitting non-component helpers into their own
 * file is the fix, not a workaround.
 */

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

export function formatMoney(
  value: number | string | null | undefined,
): string {
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
