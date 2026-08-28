import type { ReactNode } from "react";

/** Port of StatCard from main_window.py — white card, 5px left accent strip,
 *  uppercase label above a large KPI number. */
export function StatCard({
  title,
  value,
  subtitle,
  accent = "var(--color-accent)",
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  accent?: string;
}) {
  return (
    <div className="flex min-h-[130px] overflow-hidden rounded border border-border-light bg-bg-white shadow-[0_4px_20px_rgba(0,0,0,0.07)]">
      <div className="w-[5px] shrink-0" style={{ backgroundColor: accent }} />
      <div className="flex flex-col justify-center py-4 pr-[18px] pl-[18px]">
        <p className="text-xs font-medium tracking-[0.6px] text-text-body uppercase">
          {title}
        </p>
        <p className="mt-1 text-3xl font-semibold text-text-dark">{value}</p>
        {subtitle && (
          <p className="mt-1 text-xs text-text-body">{subtitle}</p>
        )}
      </div>
    </div>
  );
}

/** Shown for nav items the desktop app has but the API has no endpoint for. */
export function ComingSoon({ label }: { label: string }) {
  return (
    <div className="flex min-h-[300px] flex-col items-center justify-center rounded-card border border-border-light bg-bg-white p-10 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10 text-accent">
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v5l3 2" />
        </svg>
      </div>
      <h2 className="mt-4 text-lg font-semibold text-text-dark">
        {label} isn't available yet
      </h2>
      <p className="mt-1 max-w-sm text-sm text-text-body">
        This screen exists in the desktop app. The API doesn't expose the data
        for it yet, so there's nothing to show here.
      </p>
    </div>
  );
}

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex min-h-[200px] items-center justify-center">
      <p className="text-sm text-text-body">{label}</p>
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="rounded-card border border-danger/30 bg-danger/5 p-6"
    >
      <p className="font-medium text-danger">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 rounded-[10px] border border-danger px-4 py-1.5 text-sm font-medium text-danger transition-colors hover:bg-danger hover:text-bg-white"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({
  title,
  hint,
  action,
}: {
  title: string;
  hint?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex min-h-[200px] flex-col items-center justify-center rounded-card border border-border-light bg-bg-white p-10 text-center">
      <p className="font-medium text-text-dark">{title}</p>
      {hint && <p className="mt-1 text-sm text-text-body">{hint}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
