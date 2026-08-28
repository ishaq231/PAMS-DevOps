import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useApi } from "../lib/useApi";
import { StatCard, ErrorState, LoadingState } from "../components/ui";
import type {
  ComplaintStats,
  Invoice,
  MaintenanceRequest,
  Tenant,
} from "../lib/types";

/**
 * Each role sees the stats it actually has permission to fetch. A Tenant
 * calling GET /invoices would get a 403 from require_roles(), so the dashboard
 * asks for different things depending on who's signed in rather than firing
 * every request and swallowing the failures.
 */
export function Dashboard() {
  const { user } = useAuth();
  const role = user?.role;

  const isAdminish = role === "Administrator" || role === "Manager";
  const isFinance = isAdminish || role === "Finance Manager";
  const isFrontDesk = isAdminish || role === "Front Desk Staff";

  return (
    <div>
      <h2 className="text-2xl font-semibold text-accent">
        Welcome back, {user?.name?.split(" ")[0]}
      </h2>
      <p className="mt-1 text-sm text-text-body">
        Here's what's happening across your properties.
      </p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {isAdminish && <ApartmentCount />}
        {isAdminish && <UserCount />}
        {isFrontDesk && <TenantCount />}
        {isFinance && <OutstandingInvoices />}
        {isAdminish && <OpenMaintenance />}
        {isFrontDesk && <OpenComplaints />}
      </div>
    </div>
  );
}

function ApartmentCount() {
  const { data, loading, error } = useApi(() =>
    api.get<{ count: number }>("/apartments/count"),
  );
  if (loading) return <CardSkeleton />;
  if (error) return <CardError message={error} />;
  return <StatCard title="Apartments" value={data?.count ?? 0} />;
}

function UserCount() {
  const { data, loading, error } = useApi(() =>
    api.get<{ count: number }>("/users/count"),
  );
  if (loading) return <CardSkeleton />;
  if (error) return <CardError message={error} />;
  return <StatCard title="Users" value={data?.count ?? 0} />;
}

function TenantCount() {
  const { data, loading, error } = useApi(() => api.get<Tenant[]>("/tenants"));
  if (loading) return <CardSkeleton />;
  if (error) return <CardError message={error} />;
  return <StatCard title="Tenants" value={data?.length ?? 0} />;
}

function OutstandingInvoices() {
  const { data, loading, error } = useApi(() =>
    api.get<Invoice[]>("/invoices"),
  );
  if (loading) return <CardSkeleton />;
  if (error) return <CardError message={error} />;

  const unpaid = (data ?? []).filter(
    (i) => (i.status ?? "").toLowerCase() !== "paid",
  );
  const total = unpaid.reduce((sum, i) => sum + Number(i.amount ?? 0), 0);

  return (
    <StatCard
      title="Outstanding"
      value={`£${total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
      subtitle={`${unpaid.length} unpaid invoice${unpaid.length === 1 ? "" : "s"}`}
      accent="var(--color-warning)"
    />
  );
}

function OpenMaintenance() {
  const { data, loading, error } = useApi(() =>
    api.get<MaintenanceRequest[]>("/maintenance"),
  );
  if (loading) return <CardSkeleton />;
  if (error) return <CardError message={error} />;

  const open = (data ?? []).filter(
    (m) => (m.status ?? "").toLowerCase() !== "completed",
  );
  return (
    <StatCard
      title="Open maintenance"
      value={open.length}
      accent="var(--color-info)"
    />
  );
}

function OpenComplaints() {
  const { data, loading, error } = useApi(() =>
    api.get<ComplaintStats>("/complaints/stats"),
  );
  if (loading) return <CardSkeleton />;
  if (error) return <CardError message={error} />;

  // get_complaint_stats() returns counts keyed by status; the exact keys come
  // from whatever statuses exist in the data, so we sum everything that isn't
  // resolved rather than assuming a specific key name.
  const open = Object.entries(data ?? {})
    .filter(([status]) => !/resolved|closed/i.test(status))
    .reduce((sum, [, count]) => sum + Number(count ?? 0), 0);

  return (
    <StatCard
      title="Open complaints"
      value={open}
      accent="var(--color-danger)"
    />
  );
}

function CardSkeleton() {
  return (
    <div className="min-h-[130px] animate-pulse rounded border border-border-light bg-bg-white" />
  );
}

function CardError({ message }: { message: string }) {
  return (
    <div className="flex min-h-[130px] items-center rounded border border-border-light bg-bg-white px-4">
      <p className="text-xs text-text-body">{message}</p>
    </div>
  );
}

export { LoadingState, ErrorState };
