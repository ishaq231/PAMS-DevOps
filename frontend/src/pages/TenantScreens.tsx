import { useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/useApi";
import { useAuth } from "../lib/useAuth";
import type {
  Complaint,
  Invoice,
  Lease,
  MaintenanceRequest,
  Payment,
  Tenant,
} from "../lib/types";
import { Badge, DataTable, type Column } from "../components/DataTable";
import { PageHeader } from "../components/PageHeader";
import { formatDate, formatMoney, fullName } from "../lib/format";
import { EmptyState, LoadingState, ErrorState } from "../components/ui";
import {
  Modal,
  PrimaryButton,
  SecondaryButton,
  TextArea,
  TextInput,
} from "../components/form";

/* --------------------------------------------------------------- Register */

/** Front Desk / Manager screen. Posts to /tenants, which hardcodes the Tenant
 *  role, rather than /users where the role is chosen. */
export function Register() {
  const [form, setForm] = useState({
    fname: "",
    lname: "",
    email: "",
    phone: "",
    dob: "",
    username: "",
    password: "",
    occupation: "",
    ni_number: "",
    references: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  const set = (k: keyof typeof form) => (v: string) =>
    setForm((f) => ({ ...f, [k]: v }));

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setCreated(null);
    setSaving(true);
    try {
      const res = await api.post<{ tenant_id: number }>("/tenants", {
        ...form,
        occupation: form.occupation || null,
        ni_number: form.ni_number || null,
        references: form.references || null,
      });
      setCreated(res.tenant_id);
      setForm({
        fname: "",
        lname: "",
        email: "",
        phone: "",
        dob: "",
        username: "",
        password: "",
        occupation: "",
        ni_number: "",
        references: "",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't register tenant.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <PageHeader
        title="Register Tenant"
        subtitle="Create a tenant account and profile."
      />

      {created !== null && (
        <p className="mb-4 rounded-[10px] bg-success/10 px-3 py-2 text-sm text-success">
          Tenant registered successfully — ID {created}.
        </p>
      )}

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-card border border-border-light bg-bg-white p-6"
      >
        <div className="grid grid-cols-2 gap-4">
          <TextInput
            label="First name"
            value={form.fname}
            onChange={set("fname")}
            required
          />
          <TextInput
            label="Last name"
            value={form.lname}
            onChange={set("lname")}
            required
          />
        </div>
        <TextInput
          label="Email"
          type="email"
          value={form.email}
          onChange={set("email")}
          required
        />
        <div className="grid grid-cols-2 gap-4">
          <TextInput
            label="Phone"
            value={form.phone}
            onChange={set("phone")}
            required
          />
          <TextInput
            label="Date of birth"
            type="date"
            value={form.dob}
            onChange={set("dob")}
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <TextInput
            label="Occupation"
            value={form.occupation}
            onChange={set("occupation")}
          />
          <TextInput
            label="NI number"
            value={form.ni_number}
            onChange={set("ni_number")}
          />
        </div>
        <TextArea
          label="References"
          value={form.references}
          onChange={set("references")}
        />
        <div className="grid grid-cols-2 gap-4">
          <TextInput
            label="Username"
            value={form.username}
            onChange={set("username")}
            required
          />
          <TextInput
            label="Password"
            type="password"
            value={form.password}
            onChange={set("password")}
            required
          />
        </div>

        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}

        <div className="pt-2">
          <PrimaryButton type="submit" disabled={saving}>
            {saving ? "Registering…" : "Register tenant"}
          </PrimaryButton>
        </div>
      </form>
    </div>
  );
}

/* ---------------------------------------------------- Tenant role screens */

/** All four tenant screens read the id straight from the JWT rather than a URL
 *  param, so a tenant can only ever request their own data. The backend's
 *  require_staff_or_self enforces the same rule server-side. */
function useMe() {
  const { user } = useAuth();
  return user?.user_id ?? null;
}

export function MyLease() {
  const id = useMe();
  const { data, loading, error, reload } = useApi(
    () => api.get<Lease[]>(`/tenants/${id}/leases`),
    [id],
  );

  const columns: Column<Lease>[] = [
    { header: "ID", value: (l) => l.leaseID, className: "w-16" },
    { header: "Apartment", value: (l) => l.apartment_number ?? "—" },
    { header: "Start", value: (l) => formatDate(l.start_date) },
    { header: "End", value: (l) => formatDate(l.end_date) },
    { header: "Monthly rent", value: (l) => formatMoney(l.monthly_rent) },
    { header: "Status", value: (l) => <Badge status={l.status} /> },
  ];

  return (
    <div>
      <PageHeader title="My Lease" subtitle="Your current and past agreements." />
      <DataTable
        columns={columns}
        rows={data}
        rowKey={(l) => l.leaseID}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle="No lease on record"
        emptyHint="Speak to the front desk if you think this is wrong."
      />
    </div>
  );
}

export function MyPayments() {
  const id = useMe();
  const invoices = useApi(
    () => api.get<Invoice[]>(`/tenants/${id}/invoices`),
    [id],
  );
  const payments = useApi(
    () => api.get<Payment[]>(`/tenants/${id}/payments`),
    [id],
  );

  const invoiceCols: Column<Invoice>[] = [
    { header: "ID", value: (i) => i.invoiceID, className: "w-16" },
    { header: "Amount", value: (i) => formatMoney(i.amount) },
    { header: "Issued", value: (i) => formatDate(i.issue_date) },
    { header: "Due", value: (i) => formatDate(i.due_date) },
    { header: "Description", value: (i) => i.description ?? "—" },
    { header: "Status", value: (i) => <Badge status={i.status} /> },
  ];

  const paymentCols: Column<Payment>[] = [
    { header: "ID", value: (p) => p.payment_id, className: "w-16" },
    { header: "Invoice", value: (p) => p.invoice_id, className: "w-20" },
    { header: "Amount", value: (p) => formatMoney(p.amount_paid) },
    { header: "Date", value: (p) => formatDate(p.payment_date) },
    { header: "Method", value: (p) => p.payment_method ?? "—" },
    { header: "Receipt", value: (p) => p.receipt_number ?? "—" },
  ];

  const outstanding = (invoices.data ?? [])
    .filter((i) => (i.status ?? "").toLowerCase() !== "paid")
    .reduce((sum, i) => sum + Number(i.amount ?? 0), 0);

  return (
    <div className="space-y-8">
      <div>
        <PageHeader
          title="Payments"
          subtitle={
            invoices.loading
              ? "Loading your account…"
              : `Outstanding balance: ${formatMoney(outstanding)}`
          }
        />
        <h3 className="mb-2 text-sm font-semibold text-text-dark">Invoices</h3>
        <DataTable
          columns={invoiceCols}
          rows={invoices.data}
          rowKey={(i) => i.invoiceID}
          loading={invoices.loading}
          error={invoices.error}
          onRetry={invoices.reload}
          emptyTitle="No invoices"
        />
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-text-dark">
          Payment history
        </h3>
        <DataTable
          columns={paymentCols}
          rows={payments.data}
          rowKey={(p) => p.payment_id}
          loading={payments.loading}
          error={payments.error}
          onRetry={payments.reload}
          emptyTitle="No payments recorded"
        />
      </div>
    </div>
  );
}

export function MyMaintenance() {
  const id = useMe();
  const requests = useApi(
    () => api.get<MaintenanceRequest[]>(`/tenants/${id}/maintenance`),
    [id],
  );
  const complaints = useApi(
    () => api.get<Complaint[]>(`/tenants/${id}/complaints`),
    [id],
  );
  const [open, setOpen] = useState(false);

  const requestCols: Column<MaintenanceRequest>[] = [
    { header: "ID", value: (m) => m.request_id, className: "w-14" },
    { header: "Description", value: (m) => m.description },
    { header: "Category", value: (m) => m.category ?? "—" },
    { header: "Priority", value: (m) => <Badge status={m.priority} /> },
    { header: "Status", value: (m) => <Badge status={m.status} /> },
    { header: "Scheduled", value: (m) => formatDate(m.scheduled_date) },
  ];

  const complaintCols: Column<Complaint>[] = [
    { header: "ID", value: (c) => c.complaint_id, className: "w-14" },
    { header: "Subject", value: (c) => c.subject },
    { header: "Filed", value: (c) => formatDate(c.date_filed) },
    { header: "Status", value: (c) => <Badge status={c.status} /> },
  ];

  return (
    <div className="space-y-8">
      <div>
        <PageHeader
          title="Maintenance"
          subtitle="Repairs and issues you've reported."
          action={
            <PrimaryButton onClick={() => setOpen(true)}>
              Raise a complaint
            </PrimaryButton>
          }
        />
        <h3 className="mb-2 text-sm font-semibold text-text-dark">
          Maintenance requests
        </h3>
        <DataTable
          columns={requestCols}
          rows={requests.data}
          rowKey={(m) => m.request_id}
          loading={requests.loading}
          error={requests.error}
          onRetry={requests.reload}
          emptyTitle="No maintenance requests"
          emptyHint="Report an issue at the front desk and it'll appear here."
        />
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-text-dark">
          My complaints
        </h3>
        <DataTable
          columns={complaintCols}
          rows={complaints.data}
          rowKey={(c) => c.complaint_id}
          loading={complaints.loading}
          error={complaints.error}
          onRetry={complaints.reload}
          emptyTitle="No complaints raised"
        />
      </div>

      <RaiseComplaintModal
        open={open}
        tenantId={id}
        onClose={() => setOpen(false)}
        onCreated={() => {
          setOpen(false);
          complaints.reload();
        }}
      />
    </div>
  );
}

function RaiseComplaintModal({
  open,
  tenantId,
  onClose,
  onCreated,
}: {
  open: boolean;
  tenantId: number | null;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (tenantId == null) return;
    setError(null);
    setSaving(true);
    try {
      await api.post("/complaints", {
        tenant_id: tenantId,
        subject,
        description,
      });
      setSubject("");
      setDescription("");
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't raise complaint.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Raise a complaint">
      <form onSubmit={handleSubmit} className="space-y-4">
        <TextInput
          label="Subject"
          value={subject}
          onChange={setSubject}
          required
        />
        <TextArea
          label="What's the problem?"
          value={description}
          onChange={setDescription}
          rows={4}
          required
        />
        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}
        <div className="flex justify-end gap-3 pt-2">
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton type="submit" disabled={saving}>
            {saving ? "Sending…" : "Submit complaint"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}

export function MyProfile() {
  const id = useMe();
  const { data, loading, error, reload } = useApi(
    () => api.get<Tenant>(`/tenants/${id}`),
    [id],
  );
  const [changing, setChanging] = useState(false);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!data) return <EmptyState title="Profile not found" />;

  return (
    <div className="max-w-2xl">
      <PageHeader
        title="Profile"
        subtitle="Your account details."
        action={
          <PrimaryButton onClick={() => setChanging(true)}>
            Change password
          </PrimaryButton>
        }
      />

      <dl className="grid grid-cols-1 gap-px overflow-hidden rounded-card border border-border-light bg-border-light sm:grid-cols-2">
        <Detail label="Name" value={fullName(data)} />
        <Detail label="Username" value={data.username ?? "—"} />
        <Detail label="Email" value={data.email} />
        <Detail label="Phone" value={data.phone_number ?? "—"} />
        <Detail
          label="Date of birth"
          value={formatDate(data.date_of_birth)}
        />
        <Detail label="Occupation" value={data.occupation ?? "—"} />
        <Detail label="NI number" value={data.ni_number ?? "—"} />
        <Detail label="References" value={data.references ?? "—"} />
      </dl>

      <ChangePasswordModal
        open={changing}
        userId={id}
        onClose={() => setChanging(false)}
      />
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-bg-white px-4 py-3">
      <dt className="text-xs tracking-wide text-text-body uppercase">
        {label}
      </dt>
      <dd className="mt-0.5 text-sm text-text-dark">{value}</dd>
    </div>
  );
}

function ChangePasswordModal({
  open,
  userId,
  onClose,
}: {
  open: boolean;
  userId: number | null;
  onClose: () => void;
}) {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (newPassword !== confirm) {
      setError("New passwords don't match.");
      return;
    }
    if (userId == null) return;
    setSaving(true);
    try {
      await api.post(`/users/${userId}/change-password`, {
        old_password: oldPassword,
        new_password: newPassword,
      });
      setDone(true);
      setOldPassword("");
      setNewPassword("");
      setConfirm("");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Couldn't change password.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Change password">
      <form onSubmit={handleSubmit} className="space-y-4">
        {done && (
          <p className="rounded-[10px] bg-success/10 px-3 py-2 text-sm text-success">
            Password updated.
          </p>
        )}
        <TextInput
          label="Current password"
          type="password"
          value={oldPassword}
          onChange={setOldPassword}
          required
        />
        <TextInput
          label="New password"
          type="password"
          value={newPassword}
          onChange={setNewPassword}
          required
        />
        <TextInput
          label="Confirm new password"
          type="password"
          value={confirm}
          onChange={setConfirm}
          required
        />
        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}
        <div className="flex justify-end gap-3 pt-2">
          <SecondaryButton onClick={onClose}>Close</SecondaryButton>
          <PrimaryButton type="submit" disabled={saving}>
            {saving ? "Saving…" : "Change password"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}
