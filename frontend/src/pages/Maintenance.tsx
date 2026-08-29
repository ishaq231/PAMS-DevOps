import { useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/useApi";
import { useAuth } from "../lib/useAuth";
import type {
  MaintenanceLog,
  MaintenanceRequest,
  MaintenanceStaff,
} from "../lib/types";
import { Badge, DataTable, type Column } from "../components/DataTable";
import { PageHeader } from "../components/PageHeader";
import { formatDate, formatMoney } from "../lib/format";
import {
  Modal,
  NumberInput,
  PrimaryButton,
  RowAction,
  SecondaryButton,
  SelectInput,
  TextArea,
  TextInput,
} from "../components/form";

const STATUSES = ["Pending", "In Progress", "Completed", "Cancelled"];
const PRIORITIES = ["Low", "Medium", "High", "Urgent"];
const CATEGORIES = [
  "General",
  "Plumbing",
  "Electrical",
  "Heating",
  "Appliance",
  "Structural",
];

/** Shared by the Manager's "Maintenance" screen and Maintenance Staff's
 *  "My Requests" — same table, different endpoint. */
function useMaintenanceRows(scope: "all" | "mine") {
  const { user } = useAuth();
  return useApi(
    () =>
      api.get<MaintenanceRequest[]>(
        scope === "mine" && user
          ? `/staff/${user.user_id}/maintenance`
          : "/maintenance",
      ),
    [scope, user?.user_id],
  );
}

export function Maintenance({ scope = "all" }: { scope?: "all" | "mine" }) {
  const { data, loading, error, reload } = useMaintenanceRows(scope);
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState<MaintenanceRequest | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const columns: Column<MaintenanceRequest>[] = [
    { header: "ID", value: (m) => m.request_id, className: "w-14" },
    {
      header: "Apartment",
      value: (m) => m.apartment_number ?? m.apartment_id ?? "—",
    },
    { header: "Tenant", value: (m) => m.tenant_name ?? m.tenant_id ?? "—" },
    {
      header: "Description",
      value: (m) => (
        <span className="line-clamp-2 block max-w-xs">{m.description}</span>
      ),
    },
    { header: "Category", value: (m) => m.category ?? "—" },
    { header: "Priority", value: (m) => <Badge status={m.priority} /> },
    { header: "Status", value: (m) => <Badge status={m.status} /> },
    { header: "Assigned", value: (m) => m.staff_name ?? "Unassigned" },
    { header: "Scheduled", value: (m) => formatDate(m.scheduled_date) },
    { header: "Cost", value: (m) => formatMoney(m.cost) },
    {
      header: "",
      className: "w-24",
      value: (m) => (
        <RowAction onClick={() => setEditing(m)}>Manage</RowAction>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title={scope === "mine" ? "My Requests" : "Maintenance"}
        subtitle={
          scope === "mine"
            ? "Jobs assigned to you."
            : "Repair and upkeep requests across all units."
        }
        action={
          scope === "all" ? (
            <PrimaryButton onClick={() => setCreating(true)}>
              New request
            </PrimaryButton>
          ) : undefined
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
        rowKey={(m) => m.request_id}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle={
          scope === "mine" ? "Nothing assigned to you" : "No requests logged"
        }
      />

      <NewRequestModal
        open={creating}
        onClose={() => setCreating(false)}
        onCreated={() => {
          setCreating(false);
          reload();
        }}
      />

      <ManageRequestModal
        request={editing}
        onClose={() => setEditing(null)}
        onChanged={reload}
        onError={setActionError}
      />
    </div>
  );
}

function NewRequestModal({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState({
    apartment_id: "",
    tenant_id: "",
    description: "",
    priority: "Low",
    category: "General",
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
      await api.post("/maintenance", {
        apartment_id: Number(form.apartment_id),
        tenant_id: Number(form.tenant_id),
        description: form.description,
        priority: form.priority,
        category: form.category,
      });
      onCreated();
      setForm({
        apartment_id: "",
        tenant_id: "",
        description: "",
        priority: "Low",
        category: "General",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't create request.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="New maintenance request">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <NumberInput
            label="Apartment ID"
            value={form.apartment_id}
            onChange={set("apartment_id")}
            required
          />
          <NumberInput
            label="Tenant ID"
            value={form.tenant_id}
            onChange={set("tenant_id")}
            required
          />
        </div>
        <TextArea
          label="Description"
          value={form.description}
          onChange={set("description")}
          rows={4}
          required
        />
        <div className="grid grid-cols-2 gap-4">
          <SelectInput
            label="Priority"
            value={form.priority}
            onChange={set("priority")}
            options={PRIORITIES}
          />
          <SelectInput
            label="Category"
            value={form.category}
            onChange={set("category")}
            options={CATEGORIES}
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
            {saving ? "Creating…" : "Create request"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}

/**
 * One modal covering every per-request action, because the API exposes them as
 * five separate narrow endpoints (status, priority, assign, schedule, cost)
 * rather than one update. Each section saves independently so a failed cost
 * update doesn't discard an unsaved status change.
 */
function ManageRequestModal({
  request,
  onClose,
  onChanged,
  onError,
}: {
  request: MaintenanceRequest | null;
  onClose: () => void;
  onChanged: () => void;
  onError: (m: string) => void;
}) {
  const [busy, setBusy] = useState<string | null>(null);
  const [loadedId, setLoadedId] = useState<number | null>(null);
  const [status, setStatus] = useState("Pending");
  const [priority, setPriority] = useState("Low");
  const [staffId, setStaffId] = useState("");
  const [scheduled, setScheduled] = useState("");
  const [cost, setCost] = useState("");

  const { data: staff } = useApi(() =>
    api.get<MaintenanceStaff[]>("/maintenance/staff"),
  );

  if (request && request.request_id !== loadedId) {
    setLoadedId(request.request_id);
    setStatus(request.status ?? "Pending");
    setPriority(request.priority ?? "Low");
    setStaffId(
      request.assignedStaff_id != null ? String(request.assignedStaff_id) : "",
    );
    setScheduled((request.scheduled_date ?? "").slice(0, 10));
    setCost(request.cost != null ? String(request.cost) : "");
  }
  if (!request && loadedId !== null) setLoadedId(null);

  async function run(key: string, fn: () => Promise<unknown>) {
    if (!request) return;
    setBusy(key);
    try {
      await fn();
      onChanged();
    } catch (err) {
      onError(err instanceof Error ? err.message : "Couldn't save change.");
    } finally {
      setBusy(null);
    }
  }

  const id = request?.request_id;

  return (
    <Modal
      open={request !== null}
      onClose={onClose}
      title={`Request #${id ?? ""}`}
    >
      <div className="space-y-5">
        <p className="rounded-[10px] bg-bg-surface p-3 text-sm text-text-body">
          {request?.description}
        </p>

        <Row
          label="Status"
          busy={busy === "status"}
          onSave={() =>
            run("status", () =>
              api.patch(`/maintenance/${id}/status`, { status }),
            )
          }
        >
          <SelectInput
            label=""
            value={status}
            onChange={setStatus}
            options={STATUSES}
          />
        </Row>

        <Row
          label="Priority"
          busy={busy === "priority"}
          onSave={() =>
            run("priority", () =>
              api.patch(`/maintenance/${id}/priority`, { priority }),
            )
          }
        >
          <SelectInput
            label=""
            value={priority}
            onChange={setPriority}
            options={PRIORITIES}
          />
        </Row>

        <Row
          label="Assigned staff"
          busy={busy === "assign"}
          onSave={() =>
            run("assign", () =>
              api.post(`/maintenance/${id}/assign`, {
                staff_id: Number(staffId),
              }),
            )
          }
        >
          <SelectInput
            label=""
            value={staffId}
            onChange={setStaffId}
            options={[
              "",
              ...(staff ?? []).map((s) => String(s.user_id)),
            ]}
          />
        </Row>

        <Row
          label="Scheduled date"
          busy={busy === "schedule"}
          onSave={() =>
            run("schedule", () =>
              api.patch(`/maintenance/${id}/schedule`, {
                scheduled_date: scheduled,
              }),
            )
          }
        >
          <TextInput
            label=""
            type="date"
            value={scheduled}
            onChange={setScheduled}
          />
        </Row>

        <Row
          label="Cost (£)"
          busy={busy === "cost"}
          onSave={() =>
            run("cost", () =>
              api.patch(`/maintenance/${id}/cost`, { cost: Number(cost) }),
            )
          }
        >
          <NumberInput label="" step="0.01" value={cost} onChange={setCost} />
        </Row>

        {id != null && <RequestLogs requestId={id} />}

        <div className="flex justify-end pt-2">
          <SecondaryButton onClick={onClose}>Close</SecondaryButton>
        </div>
      </div>
    </Modal>
  );
}

function Row({
  label,
  children,
  onSave,
  busy,
}: {
  label: string;
  children: React.ReactNode;
  onSave: () => void;
  busy: boolean;
}) {
  return (
    <div>
      <p className="mb-1 text-sm font-medium text-text-dark">{label}</p>
      <div className="flex items-end gap-3">
        <div className="flex-1">{children}</div>
        <PrimaryButton onClick={onSave} disabled={busy}>
          {busy ? "Saving…" : "Save"}
        </PrimaryButton>
      </div>
    </div>
  );
}

function RequestLogs({ requestId }: { requestId: number }) {
  const { data, loading, reload } = useApi(
    () => api.get<MaintenanceLog[]>(`/maintenance/${requestId}/logs`),
    [requestId],
  );
  const [description, setDescription] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function addLog() {
    setError(null);
    setSaving(true);
    try {
      await api.post(`/maintenance/${requestId}/logs`, {
        description,
        technician_notes: notes || null,
      });
      setDescription("");
      setNotes("");
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't add log.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="border-t border-border-light pt-4">
      <p className="mb-2 text-sm font-medium text-text-dark">Work log</p>

      {loading ? (
        <p className="text-sm text-text-body">Loading…</p>
      ) : (data ?? []).length === 0 ? (
        <p className="text-sm text-text-body">No entries yet.</p>
      ) : (
        <ul className="mb-3 space-y-2">
          {(data ?? []).map((l) => (
            <li
              key={l.log_id}
              className="rounded-[10px] bg-bg-surface px-3 py-2 text-sm text-text-body"
            >
              <p className="text-text-dark">{l.description}</p>
              {l.technician_notes && (
                <p className="mt-0.5 text-xs">{l.technician_notes}</p>
              )}
            </li>
          ))}
        </ul>
      )}

      <div className="space-y-3">
        <TextArea
          label="New entry"
          value={description}
          onChange={setDescription}
          rows={2}
        />
        <TextInput
          label="Technician notes"
          value={notes}
          onChange={setNotes}
        />
        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}
        <PrimaryButton
          onClick={addLog}
          disabled={saving || description.trim() === ""}
        >
          {saving ? "Adding…" : "Add log entry"}
        </PrimaryButton>
      </div>
    </div>
  );
}
