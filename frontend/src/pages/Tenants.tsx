import { useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/useApi";
import type { Tenant } from "../lib/types";
import { DataTable, type Column } from "../components/DataTable";
import { PageHeader } from "../components/PageHeader";
import { formatDate, fullName } from "../lib/format";
import {
  Modal,
  PrimaryButton,
  SecondaryButton,
  TextInput,
} from "../components/form";

const columns: Column<Tenant>[] = [
  { header: "ID", value: (t) => t.tenant_id ?? t.user_id, className: "w-16" },
  { header: "Name", value: (t) => fullName(t) },
  { header: "Email", value: (t) => t.email },
  { header: "Phone", value: (t) => t.phone_number ?? "—" },
  { header: "Date of birth", value: (t) => formatDate(t.date_of_birth) },
  { header: "Occupation", value: (t) => t.occupation ?? "—" },
];

export function Tenants() {
  const { data, loading, error, reload } = useApi(() =>
    api.get<Tenant[]>("/tenants"),
  );
  const [open, setOpen] = useState(false);

  return (
    <div>
      <PageHeader
        title="Tenants"
        subtitle="Everyone currently registered on a lease."
        action={
          <PrimaryButton onClick={() => setOpen(true)}>
            Add tenant
          </PrimaryButton>
        }
      />

      <DataTable
        columns={columns}
        rows={data}
        rowKey={(t) => t.tenant_id ?? t.user_id}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle="No tenants yet"
        emptyHint="Add the first tenant to get started."
        emptyAction={
          <PrimaryButton onClick={() => setOpen(true)}>
            Add tenant
          </PrimaryButton>
        }
      />

      <AddTenantModal
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

function AddTenantModal({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState({
    fname: "",
    lname: "",
    email: "",
    phone: "",
    dob: "",
    username: "",
    password: "",
    occupation: "",
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
      // Empty optional fields are sent as null rather than "", so the database
      // stores a real absence instead of an empty string.
      await api.post("/tenants", {
        ...form,
        occupation: form.occupation || null,
      });
      onCreated();
      setForm({
        fname: "",
        lname: "",
        email: "",
        phone: "",
        dob: "",
        username: "",
        password: "",
        occupation: "",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't add tenant.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Add tenant">
      <form onSubmit={handleSubmit} className="space-y-4">
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
          {/* type="date" gives a real date picker and sends YYYY-MM-DD, which
              avoids the malformed-date problem you can hit typing by hand. */}
          <TextInput
            label="Date of birth"
            type="date"
            value={form.dob}
            onChange={set("dob")}
            required
          />
        </div>
        <TextInput
          label="Occupation"
          value={form.occupation}
          onChange={set("occupation")}
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

        <div className="flex justify-end gap-3 pt-2">
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton type="submit" disabled={saving}>
            {saving ? "Adding…" : "Add tenant"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}
