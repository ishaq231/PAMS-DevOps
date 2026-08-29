import type { ReactNode } from "react";
import { EmptyState, ErrorState, LoadingState } from "./ui";

/**
 * Port of PAMSTableWidget from src/gui/dialogs.py — white card, 8px radius,
 * BG_SURFACE header row with a 2px bottom border, alternating row tint,
 * accent-glow on hover.
 *
 * Columns are described as data rather than as JSX so every page renders rows
 * the same way. `render` lets a column return anything (a badge, a button)
 * while `value` stays a plain field lookup for the common case.
 */
export type Column<T> = {
  header: string;
  /** Field to read, or a function for computed/formatted values. */
  value: (row: T) => ReactNode;
  /** Tailwind width class, e.g. "w-32". Optional. */
  className?: string;
};

type DataTableProps<T> = {
  columns: Column<T>[];
  rows: T[] | null;
  rowKey: (row: T) => string | number;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  emptyTitle?: string;
  emptyHint?: string;
  emptyAction?: ReactNode;
  onRowClick?: (row: T) => void;
};

export function DataTable<T>({
  columns,
  rows,
  rowKey,
  loading,
  error,
  onRetry,
  emptyTitle = "Nothing here yet",
  emptyHint,
  emptyAction,
  onRowClick,
}: DataTableProps<T>) {
  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={onRetry} />;
  if (!rows || rows.length === 0) {
    return (
      <EmptyState title={emptyTitle} hint={emptyHint} action={emptyAction} />
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border-light bg-bg-white">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-[13px] text-text-dark">
          <thead>
            <tr className="border-b-2 border-border-light bg-bg-surface">
              {columns.map((col) => (
                <th
                  key={col.header}
                  scope="col"
                  className={`px-3 py-2.5 text-[11px] font-semibold text-text-body ${col.className ?? ""}`}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={rowKey(row)}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                className={[
                  "border-b border-bg-surface transition-colors last:border-b-0",
                  i % 2 === 1 ? "bg-[#FAFCFE]" : "",
                  onRowClick
                    ? "cursor-pointer hover:bg-[var(--accent-glow)]"
                    : "",
                ].join(" ")}
              >
                {columns.map((col) => (
                  <td
                    key={col.header}
                    className={`px-3 py-2 ${col.className ?? ""}`}
                  >
                    {col.value(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/** Status pill, coloured by meaning rather than by a fixed list of strings, so
 *  a status the database has that we didn't anticipate still renders sensibly. */
export function Badge({ status }: { status: string | null | undefined }) {
  const text = status ?? "Unknown";
  const s = text.toLowerCase();

  let tone = "bg-bg-surface text-text-body";
  if (/paid|resolved|completed|active|available/.test(s)) {
    tone = "bg-success/12 text-success";
  } else if (/pending|in progress|scheduled|open/.test(s)) {
    tone = "bg-warning/12 text-warning";
  } else if (/overdue|terminated|rejected|cancelled|urgent|high/.test(s)) {
    tone = "bg-danger/12 text-danger";
  } else if (/occupied|assigned|low/.test(s)) {
    tone = "bg-info/12 text-info";
  }

  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-[11px] font-medium ${tone}`}
    >
      {text}
    </span>
  );
}
