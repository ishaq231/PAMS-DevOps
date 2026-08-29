import { useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/useApi";
import type { Lease, Location, StaffMember } from "../lib/types";
import { Badge, DataTable, type Column } from "../components/DataTable";
import { PageHeader } from "../components/PageHeader";
import { formatDate, formatMoney, fullName } from "../lib/format";
import {
  Modal,
  NumberInput,
  PrimaryButton,
  RowAction,
  SecondaryButton,
  SelectInput,
  TextInput,
} from "../components/form";

/* ------------------------------------------------------------------ Staff */

export function Staff() {
  const { data, loading, error, reload } = useApi(() =>
    api.get<StaffMember[]>("/staff"),
  );
  const [editing, setEditing] = useState<StaffMember | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const columns: Column<StaffMember>[] = [
    { header: "Emp ID", value: (s) => s.employee_id, className: "w-20" },
    { header: "Name", value: (s) => fullName(s) },
    { header: "Email", value: (s) => s.email },
    // user_role is the account role; staff_role is the job title. Two
    // different columns in the schema, aliased apart in get_all_staff().
    { header: "Account role", value: (s) => <Badge status={s.user_role} /> },
    { header: "Job title", value: (s) => s.staff_role ?? "—" },
    { header: "Location", value: (s) => s.location ?? "—" },
    { header: "Salary", value: (s) => formatMoney(s.salary) },
    { header: "Started", value: (s) => formatDate(s.start_date) },
    {
      header: "",
      className: "w-24",
      value: (s) => <RowAction onClick={() => setEditing(s)}>Edit</RowAction>,
    },
  ];

  return (
    <div>
      <PageHeader
        title="Staff Members"
        subtitle="Employment details for everyone on payroll."
      />
      {actionError && (
        <p role="alert" className="mb-4 text-sm text-danger">
          {actionError}
        </p>
      )}
      <DataTable
        columns={columns}
        rows={data}
        rowKey={(s) => s.employee_id}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle="No staff members found"
      />
      <EditStaffModal
        staff={editing}
        onClose={() => setEditing(null)}
        onSaved={() => {
          setEditing(null);
          reload();
        }}
        onError={setActionError}
      />
    </div>
  );
}

function EditStaffModal({
  staff,
  onClose,
  onSaved,
  onError,
}: {
  staff: StaffMember | null;
  onClose: () => void;
  onSaved: () => void;
  onError: (m: string) => void;
}) {
  const [salary, setSalary] = useState("");
  const [staffRole, setStaffRole] = useState("");
  const [startDate, setStartDate] = useState("");
  const [locationId, setLocationId] = useState("");
  const [saving, setSaving] = useState(false);
  const [loadedId, setLoadedId] = useState<number | null>(null);

  const { data: locations } = useApi(() => api.get<Location[]>("/locations"));

  if (staff && staff.employee_id !== loadedId) {
    setLoadedId(staff.employee_id);
    setSalary(staff.salary != null ? String(staff.salary) : "");
    setStaffRole(staff.staff_role ?? "");
    setStartDate((staff.start_date ?? "").slice(0, 10));
    setLocationId(staff.location_id != null ? String(staff.location_id) : "");
  }
  if (!staff && loadedId !== null) setLoadedId(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!staff) return;
    setSaving(true);
    try {
      // PATCH /staff/{id} builds its SQL from whichever fields are non-null,
      // so blank inputs are sent as null and simply left untouched.
      await api.patch(`/staff/${staff.employee_id}`, {
        salary: salary === "" ? null : Number(salary),
        role: staffRole || null,
        start_date: startDate || null,
        location_id: locationId === "" ? null : Number(locationId),
      });
      onSaved();
    } catch (err) {
      onError(err instanceof Error ? err.message : "Couldn't save staff.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal
      open={staff !== null}
      onClose={onClose}
      title={staff ? `Edit ${fullName(staff)}` : "Edit staff"}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <NumberInput
            label="Salary (£)"
            step="0.01"
            value={salary}
            onChange={setSalary}
          />
          <TextInput
            label="Job title"
            value={staffRole}
            onChange={setStaffRole}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <TextInput
            label="Start date"
            type="date"
            value={startDate}
            onChange={setStartDate}
          />
          <SelectInput
            label="Location"
            value={locationId}
            onChange={setLocationId}
            options={[
              "",
              ...(locations ?? []).map((l) => String(l.location_id)),
            ]}
          />
        </div>
        <p className="text-xs text-text-body">
          Location is selected by ID:{" "}
          {(locations ?? [])
            .map((l) => `${l.location_id} = ${l.city}`)
            .join(", ") || "no locations loaded"}
        </p>
        <div className="flex justify-end gap-3 pt-2">
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton type="submit" disabled={saving}>
            {saving ? "Saving…" : "Save changes"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}

/* ----------------------------------------------------------------- Leases */

const LEASE_STATUSES = ["ACTIVE", "PENDING", "EXPIRED", "TERMINATED"];

export function Leases() {
  const { data, loading, error, reload } = useApi(() =>
    api.get<Lease[]>("/leases"),
  );
  const [creating, setCreating] = useState(false);
  const [statusFor, setStatusFor] = useState<Lease | null>(null);
  const [terminating, setTerminating] = useState<Lease | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  async function saveStatus(id: number, status: string) {
    setActionError(null);
    try {
      await api.patch(`/leases/${id}/status`, { status });
      setStatusFor(null);
      reload();
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "Couldn't update status.",
      );
    }
  }

  async function terminate(id: number) {
    setActionError(null);
    try {
      await api.post(`/leases/${id}/terminate`);
      setTerminating(null);
      reload();
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "Couldn't terminate lease.",
      );
    }
  }

  const columns: Column<Lease>[] = [
    { header: "ID", value: (l) => l.leaseID, className: "w-16" },
    { header: "Tenant", value: (l) => l.tenant_name ?? l.tenantID ?? "—" },
    {
      header: "Apartment",
      value: (l) => l.apartment_number ?? l.apartmentID ?? "—",
    },
    { header: "Start", value: (l) => formatDate(l.start_date) },
    { header: "End", value: (l) => formatDate(l.end_date) },
    { header: "Rent", value: (l) => formatMoney(l.monthly_rent) },
    { header: "Status", value: (l) => <Badge status={l.status} /> },
    {
      header: "",
      className: "w-44",
      value: (l) => (
        <div className="flex gap-2">
          <RowAction onClick={() => setStatusFor(l)}>Status</RowAction>
          {l.status !== "TERMINATED" && (
            <RowAction tone="danger" onClick={() => setTerminating(l)}>
              Terminate
            </RowAction>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Lease Tracking"
        subtitle="Agreements between tenants and units."
        action={
          <PrimaryButton onClick={() => setCreating(true)}>
            New lease
          </PrimaryButton>
        }
      />
      {actionError && (
        <p role="alert" className="mb-4 text-sm text-danger">
          {actionError}
        </p>
      )}
      <DataTable
        columns={columns}
        rows={data}
        rowKey={(l) => l.leaseID}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle="No leases yet"
      />

      <NewLeaseModal
        open={creating}
        onClose={() => setCreating(false)}
        onCreated={() => {
          setCreating(false);
          reload();
        }}
      />

      <LeaseStatusModal
        lease={statusFor}
        onClose={() => setStatusFor(null)}
        onSave={saveStatus}
      />

      <Modal
        open={terminating !== null}
        onClose={() => setTerminating(null)}
        title="Terminate lease"
      >
        <p className="text-sm text-text-body">
          Terminate lease #{terminating?.leaseID}? This sets the status to
          TERMINATED and records today as the termination date.
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <SecondaryButton onClick={() => setTerminating(null)}>
            Cancel
          </SecondaryButton>
          <button
            type="button"
            onClick={() => terminating && terminate(terminating.leaseID)}
            className="h-10 rounded-[10px] bg-danger px-4 text-sm font-semibold text-bg-white transition-opacity hover:opacity-90"
          >
            Terminate
          </button>
        </div>
      </Modal>
    </div>
  );
}

function LeaseStatusModal({
  lease,
  onClose,
  onSave,
}: {
  lease: Lease | null;
  onClose: () => void;
  onSave: (id: number, status: string) => void;
}) {
  const [status, setStatus] = useState("ACTIVE");

  return (
    <Modal
      open={lease !== null}
      onClose={onClose}
      title={`Lease #${lease?.leaseID ?? ""}`}
    >
      <div className="space-y-4">
        <SelectInput
          label="Status"
          value={status}
          onChange={setStatus}
          options={LEASE_STATUSES}
        />
        <div className="flex justify-end gap-3 pt-2">
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton onClick={() => lease && onSave(lease.leaseID, status)}>
            Save status
          </PrimaryButton>
        </div>
      </div>
    </Modal>
  );
}

function NewLeaseModal({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState({
    tenant_id: "",
    apartment_id: "",
    start_date: "",
    end_date: "",
    monthly_rent: "",
    deposit: "",
    term_months: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const set = (k: keyof typeof form) => (v: string) =>
    setForm((f) => ({ ...f, [k]: v }));

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      // The POST body uses the Pydantic model's field names (snake_case),
      // which differ from the camel-ish names the GET response returns.
      await api.post("/leases", {
        tenant_id: Number(form.tenant_id),
        apartment_id: Number(form.apartment_id),
        start_date: form.start_date,
        end_date: form.end_date,
        monthly_rent: Number(form.monthly_rent),
        deposit: Number(form.deposit),
        term_months: Number(form.term_months),
      });
      onCreated();
      setForm({
        tenant_id: "",
        apartment_id: "",
        start_date: "",
        end_date: "",
        monthly_rent: "",
        deposit: "",
        term_months: "",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't create lease.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="New lease">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <NumberInput
            label="Tenant ID"
            value={form.tenant_id}
            onChange={set("tenant_id")}
            required
          />
          <NumberInput
            label="Apartment ID"
            value={form.apartment_id}
            onChange={set("apartment_id")}
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <TextInput
            label="Start date"
            type="date"
            value={form.start_date}
            onChange={set("start_date")}
            required
          />
          <TextInput
            label="End date"
            type="date"
            value={form.end_date}
            onChange={set("end_date")}
            required
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <NumberInput
            label="Rent (£)"
            step="0.01"
            value={form.monthly_rent}
            onChange={set("monthly_rent")}
            required
          />
          <NumberInput
            label="Deposit (£)"
            step="0.01"
            value={form.deposit}
            onChange={set("deposit")}
            required
          />
          <NumberInput
            label="Term (months)"
            value={form.term_months}
            onChange={set("term_months")}
            required
          />
        </div>

        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton type="submit" disabled={saving}>
            {saving ? "Creating…" : "Create lease"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}
