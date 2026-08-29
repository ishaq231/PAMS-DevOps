import { useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/useApi";
import type { Invoice } from "../lib/types";
import { Badge, DataTable, type Column } from "../components/DataTable";
import {
  PageHeader,
  formatDate,
  formatMoney,
} from "../components/PageHeader";
import {
  Modal,
  NumberInput,
  PrimaryButton,
  RowAction,
  SecondaryButton,
  TextArea,
  TextInput,
} from "../components/form";

export function Invoices() {
  const { data, loading, error, reload } = useApi(() =>
    api.get<Invoice[]>("/invoices"),
  );
  const [open, setOpen] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  async function markPaid(id: number) {
    setActionError(null);
    try {
      await api.post(`/invoices/${id}/mark-paid`);
      reload();
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "Couldn't mark as paid.",
      );
    }
  }

  const columns: Column<Invoice>[] = [
    { header: "ID", value: (i) => i.invoiceID, className: "w-16" },
    { header: "Lease", value: (i) => i.lease_id, className: "w-20" },
    { header: "Amount", value: (i) => formatMoney(i.amount) },
    { header: "Issued", value: (i) => formatDate(i.issue_date) },
    { header: "Due", value: (i) => formatDate(i.due_date) },
    { header: "Status", value: (i) => <Badge status={i.status} /> },
    {
      header: "",
      className: "w-28",
      value: (i) =>
        (i.status ?? "").toLowerCase() === "paid" ? null : (
          <RowAction onClick={() => markPaid(i.invoiceID)}>
            Mark paid
          </RowAction>
        ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Invoices"
        subtitle="Rent and charges raised against active leases."
        action={
          <PrimaryButton onClick={() => setOpen(true)}>
            New invoice
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
        rowKey={(i) => i.invoiceID}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle="No invoices yet"
        emptyHint="Raise an invoice against a lease to see it here."
      />

      <NewInvoiceModal
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

function NewInvoiceModal({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState({
    lease_id: "",
    amount: "",
    issue_date: "",
    due_date: "",
    description: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const set = (key: keyof typeof form) => (v: string) =>
    setForm((f) => ({ ...f, [key]: v }));

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      // Inputs always hand back strings; the API's Pydantic model expects
      // lease_id as int and amount as float, so convert before sending
      // rather than letting it come back as a 422.
      await api.post("/invoices", {
        lease_id: Number(form.lease_id),
        amount: Number(form.amount),
        issue_date: form.issue_date,
        due_date: form.due_date,
        description: form.description || null,
      });
      onCreated();
      setForm({
        lease_id: "",
        amount: "",
        issue_date: "",
        due_date: "",
        description: "",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't create invoice.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="New invoice">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <NumberInput
            label="Lease ID"
            value={form.lease_id}
            onChange={set("lease_id")}
            required
          />
          <NumberInput
            label="Amount (£)"
            step="0.01"
            value={form.amount}
            onChange={set("amount")}
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <TextInput
            label="Issue date"
            type="date"
            value={form.issue_date}
            onChange={set("issue_date")}
            required
          />
          <TextInput
            label="Due date"
            type="date"
            value={form.due_date}
            onChange={set("due_date")}
            required
          />
        </div>
        <TextArea
          label="Description"
          value={form.description}
          onChange={set("description")}
        />

        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton type="submit" disabled={saving}>
            {saving ? "Creating…" : "Create invoice"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}
