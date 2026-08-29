import { useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/useApi";
import type { Apartment, Complaint, Location, Payment } from "../lib/types";
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

/* ---------------------------------------------------------------- Payments */

export function Payments() {
  const { data, loading, error, reload } = useApi(() =>
    api.get<Payment[]>("/payments"),
  );
  const [open, setOpen] = useState(false);

  const columns: Column<Payment>[] = [
    { header: "ID", value: (p) => p.payment_id, className: "w-16" },
    { header: "Invoice", value: (p) => p.invoice_id, className: "w-20" },
    { header: "Amount", value: (p) => formatMoney(p.amount_paid) },
    { header: "Date", value: (p) => formatDate(p.payment_date) },
    { header: "Method", value: (p) => p.payment_method ?? "—" },
    { header: "Reference", value: (p) => p.transaction_ref ?? "—" },
    { header: "Receipt", value: (p) => p.receipt_number ?? "—" },
  ];

  return (
    <div>
      <PageHeader
        title="Payments"
        subtitle="Money received against issued invoices."
        action={
          <PrimaryButton onClick={() => setOpen(true)}>
            Record payment
          </PrimaryButton>
        }
      />
      <DataTable
        columns={columns}
        rows={data}
        rowKey={(p) => p.payment_id}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle="No payments recorded"
        emptyHint="Payments appear here once they're logged against an invoice."
      />
      <RecordPaymentModal
        open={open}
        onClose={() => setOpen(false)}
        onCreated={() => {
          setOpen(false);
          reload();
        }}
      />
    </div>
  );
}

function RecordPaymentModal({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState({
    invoice_id: "",
    amount_paid: "",
    payment_date: "",
    payment_method: "Bank Transfer",
    transaction_ref: "",
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
      await api.post("/payments", {
        invoice_id: Number(form.invoice_id),
        amount_paid: Number(form.amount_paid),
        payment_date: form.payment_date,
        payment_method: form.payment_method,
        transaction_ref: form.transaction_ref,
      });
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't record payment.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Record payment">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <NumberInput
            label="Invoice ID"
            value={form.invoice_id}
            onChange={set("invoice_id")}
            required
          />
          <NumberInput
            label="Amount (£)"
            step="0.01"
            value={form.amount_paid}
            onChange={set("amount_paid")}
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <TextInput
            label="Payment date"
            type="date"
            value={form.payment_date}
            onChange={set("payment_date")}
            required
          />
          <SelectInput
            label="Method"
            value={form.payment_method}
            onChange={set("payment_method")}
            options={["Bank Transfer", "Card", "Cash", "Direct Debit"]}
          />
        </div>
        <TextInput
          label="Transaction reference"
          value={form.transaction_ref}
          onChange={set("transaction_ref")}
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
            {saving ? "Saving…" : "Record payment"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}

/* -------------------------------------------------------------- Complaints */

const COMPLAINT_STATUSES = ["Open", "In Progress", "Resolved", "Closed"];

export function Complaints() {
  const { data, loading, error, reload } = useApi(() =>
    api.get<Complaint[]>("/complaints"),
  );
  const [open, setOpen] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [editing, setEditing] = useState<Complaint | null>(null);

  async function updateStatus(id: number, status: string) {
    setActionError(null);
    try {
      await api.patch(`/complaints/${id}`, { status });
      setEditing(null);
      reload();
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "Couldn't update status.",
      );
    }
  }

  const columns: Column<Complaint>[] = [
    { header: "ID", value: (c) => c.complaint_id, className: "w-16" },
    { header: "Tenant", value: (c) => c.tenant_id, className: "w-20" },
    { header: "Subject", value: (c) => c.subject },
    { header: "Filed", value: (c) => formatDate(c.date_filed) },
    { header: "Status", value: (c) => <Badge status={c.status} /> },
    {
      header: "",
      className: "w-24",
      value: (c) => (
        <RowAction onClick={() => setEditing(c)}>Update</RowAction>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Complaints"
        subtitle="Issues raised by tenants and their current status."
        action={
          <PrimaryButton onClick={() => setOpen(true)}>
            Log complaint
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
        rowKey={(c) => c.complaint_id}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle="No complaints logged"
        emptyHint="Nothing outstanding — that's a good sign."
      />
      <LogComplaintModal
        open={open}
        onClose={() => setOpen(false)}
        onCreated={() => {
          setOpen(false);
          reload();
        }}
      />
      <UpdateStatusModal
        complaint={editing}
        onClose={() => setEditing(null)}
        onSave={updateStatus}
      />
    </div>
  );
}

function LogComplaintModal({
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
    subject: "",
    description: "",
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
      await api.post("/complaints", {
        tenant_id: Number(form.tenant_id),
        subject: form.subject,
        description: form.description,
      });
      onCreated();
      setForm({ tenant_id: "", subject: "", description: "" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't log complaint.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Log complaint">
      <form onSubmit={handleSubmit} className="space-y-4">
        <NumberInput
          label="Tenant ID"
          value={form.tenant_id}
          onChange={set("tenant_id")}
          required
        />
        <TextInput
          label="Subject"
          value={form.subject}
          onChange={set("subject")}
          required
        />
        <TextArea
          label="Description"
          value={form.description}
          onChange={set("description")}
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
            {saving ? "Logging…" : "Log complaint"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}

function UpdateStatusModal({
  complaint,
  onClose,
  onSave,
}: {
  complaint: Complaint | null;
  onClose: () => void;
  onSave: (id: number, status: string) => void;
}) {
  const [status, setStatus] = useState("Open");

  return (
    <Modal
      open={complaint !== null}
      onClose={onClose}
      title={`Update complaint #${complaint?.complaint_id ?? ""}`}
    >
      <div className="space-y-4">
        <p className="text-sm text-text-body">{complaint?.subject}</p>
        <SelectInput
          label="Status"
          value={status}
          onChange={setStatus}
          options={COMPLAINT_STATUSES}
        />
        <div className="flex justify-end gap-3 pt-2">
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton
            onClick={() =>
              complaint && onSave(complaint.complaint_id, status)
            }
          >
            Save status
          </PrimaryButton>
        </div>
      </div>
    </Modal>
  );
}

/* --------------------------------------------------------------- Locations */

export function Locations() {
  const { data, loading, error, reload } = useApi(() =>
    api.get<Location[]>("/locations"),
  );
  const [open, setOpen] = useState(false);

  const columns: Column<Location>[] = [
    { header: "ID", value: (l) => l.location_id, className: "w-16" },
    { header: "City", value: (l) => l.city },
    { header: "Manager", value: (l) => l.manager ?? "—" },
  ];

  return (
    <div>
      <PageHeader
        title="Locations"
        subtitle="Sites Paragon operates across."
        action={
          <PrimaryButton onClick={() => setOpen(true)}>
            Add location
          </PrimaryButton>
        }
      />
      <DataTable
        columns={columns}
        rows={data}
        rowKey={(l) => l.location_id}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle="No locations yet"
      />
      <AddLocationModal
        open={open}
        onClose={() => setOpen(false)}
        onCreated={() => {
          setOpen(false);
          reload();
        }}
      />
    </div>
  );
}

function AddLocationModal({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [city, setCity] = useState("");
  const [manager, setManager] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await api.post("/locations", { city, manager });
      setCity("");
      setManager("");
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't add location.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Add location">
      <form onSubmit={handleSubmit} className="space-y-4">
        <TextInput label="City" value={city} onChange={setCity} required />
        <TextInput
          label="Manager"
          value={manager}
          onChange={setManager}
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
            {saving ? "Adding…" : "Add location"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}

/* -------------------------------------------------------------- Apartments */

const OCCUPATION_STATUSES = ["Available", "Occupied", "Under Maintenance"];

export function Apartments() {
  const { data, loading, error, reload } = useApi(() =>
    api.get<Apartment[]>("/apartments"),
  );
  const [editing, setEditing] = useState<Apartment | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  async function saveStatus(id: number, status: string) {
    setActionError(null);
    try {
      await api.patch(`/apartments/${id}/status`, { status });
      setEditing(null);
      reload();
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "Couldn't update status.",
      );
    }
  }

  const columns: Column<Apartment>[] = [
    { header: "ID", value: (a) => a.apartment_id, className: "w-16" },
    { header: "Number", value: (a) => a.apartment_number },
    { header: "Type", value: (a) => a.type ?? "—" },
    { header: "Rooms", value: (a) => a.number_of_rooms ?? "—" },
    { header: "Sq ft", value: (a) => a.square_footage ?? "—" },
    { header: "Rent", value: (a) => formatMoney(a.monthly_rent) },
    {
      header: "Status",
      value: (a) => <Badge status={a.occupation_status} />,
    },
    {
      header: "",
      className: "w-24",
      value: (a) => (
        <RowAction onClick={() => setEditing(a)}>Update</RowAction>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Apartments"
        subtitle="Every unit across all locations."
      />
      {actionError && (
        <p role="alert" className="mb-4 text-sm text-danger">
          {actionError}
        </p>
      )}
      <DataTable
        columns={columns}
        rows={data}
        rowKey={(a) => a.apartment_id}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle="No apartments yet"
      />
      <ApartmentStatusModal
        apartment={editing}
        onClose={() => setEditing(null)}
        onSave={saveStatus}
      />
    </div>
  );
}

function ApartmentStatusModal({
  apartment,
  onClose,
  onSave,
}: {
  apartment: Apartment | null;
  onClose: () => void;
  onSave: (id: number, status: string) => void;
}) {
  const [status, setStatus] = useState("Available");

  return (
    <Modal
      open={apartment !== null}
      onClose={onClose}
      title={`Apartment ${apartment?.apartment_number ?? ""}`}
    >
      <div className="space-y-4">
        <SelectInput
          label="Occupation status"
          value={status}
          onChange={setStatus}
          options={OCCUPATION_STATUSES}
        />
        <div className="flex justify-end gap-3 pt-2">
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton
            onClick={() =>
              apartment && onSave(apartment.apartment_id, status)
            }
          >
            Save status
          </PrimaryButton>
        </div>
      </div>
    </Modal>
  );
}
