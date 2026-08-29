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
