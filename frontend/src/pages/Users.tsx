import { useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/useApi";
import { useAuth } from "../lib/useAuth";
import type { Role, User } from "../lib/types";
import { Badge, DataTable, type Column } from "../components/DataTable";
import { PageHeader } from "../components/PageHeader";
import { fullName } from "../lib/format";
import {
  Modal,
  PrimaryButton,
  RowAction,
  SecondaryButton,
  SelectInput,
  TextInput,
} from "../components/form";

const ROLES: Role[] = [
  "Administrator",
  "Manager",
  "Front Desk Staff",
  "Finance Manager",
  "Maintenance Staff",
  "Tenant",
];

const EMPTY = {
  fname: "",
  lname: "",
  email: "",
  phone: "",
  dob: "",
  role: "Tenant" as Role,
  username: "",
  password: "",
  occupation: "",
};

export function Users() {
  const { user: me } = useAuth();
  const { data, loading, error, reload } = useApi(() =>
    api.get<User[]>("/users"),
  );

  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<User | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  async function handleDelete(id: number) {
    setActionError(null);
    try {
      await api.delete(`/users/${id}`);
      setConfirmDelete(null);
      reload();
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "Couldn't delete user.",
      );
    }
  }

  const columns: Column<User>[] = [
    { header: "ID", value: (u) => u.user_id, className: "w-16" },
    { header: "Name", value: (u) => fullName(u) },
    { header: "Username", value: (u) => u.username ?? "—" },
    { header: "Email", value: (u) => u.email },
    { header: "Phone", value: (u) => u.phone_number ?? "—" },
    { header: "Role", value: (u) => <Badge status={u.role} /> },
    {
      header: "",
      className: "w-40",
      value: (u) => (
        <div className="flex gap-2">
          <RowAction onClick={() => setEditing(u)}>Edit</RowAction>
          {/* Deleting your own account would log you out mid-session and
              orphan the JWT, so that row's delete is hidden. */}
          {u.user_id !== me?.user_id && (
            <RowAction tone="danger" onClick={() => setConfirmDelete(u)}>
              Delete
            </RowAction>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="User Management"
        subtitle="Every account on the system, across all roles."
        action={
          <PrimaryButton onClick={() => setCreating(true)}>
            Add user
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
        rowKey={(u) => u.user_id}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyTitle="No users found"
      />

      <UserFormModal
        open={creating}
        title="Add user"
        onClose={() => setCreating(false)}
        onSaved={() => {
          setCreating(false);
          reload();
        }}
      />

      <UserFormModal
        open={editing !== null}
        title={`Edit ${editing ? fullName(editing) : "user"}`}
        existing={editing}
        onClose={() => setEditing(null)}
        onSaved={() => {
          setEditing(null);
          reload();
        }}
      />

      <Modal
        open={confirmDelete !== null}
        onClose={() => setConfirmDelete(null)}
        title="Delete user"
      >
        <p className="text-sm text-text-body">
          Delete {confirmDelete ? fullName(confirmDelete) : "this user"}? This
          removes the account permanently.
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <SecondaryButton onClick={() => setConfirmDelete(null)}>
            Cancel
          </SecondaryButton>
          <button
            type="button"
            onClick={() =>
              confirmDelete && handleDelete(confirmDelete.user_id)
            }
            className="h-10 rounded-[10px] bg-danger px-4 text-sm font-semibold text-bg-white transition-opacity hover:opacity-90"
          >
            Delete user
          </button>
        </div>
      </Modal>
    </div>
  );
}

function UserFormModal({
  open,
  title,
  existing,
  onClose,
  onSaved,
}: {
  open: boolean;
  title: string;
  existing?: User | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const isEdit = Boolean(existing);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  // Tracks which record the form was last filled from, so switching between
  // two users repopulates instead of keeping the first one's values.
  const [loadedId, setLoadedId] = useState<number | null>(null);

  if (existing && existing.user_id !== loadedId) {
    setLoadedId(existing.user_id);
    setForm({
      fname: existing.fname ?? "",
      lname: existing.lname ?? "",
      email: existing.email ?? "",
      phone: existing.phone_number ?? "",
      dob: (existing.date_of_birth ?? "").slice(0, 10),
      role: existing.role,
      username: existing.username ?? "",
      password: "",
      occupation: existing.occupation ?? "",
    });
  }
  if (!existing && loadedId !== null) {
    setLoadedId(null);
    setForm(EMPTY);
  }

  const set = (k: keyof typeof form) => (v: string) =>
    setForm((f) => ({ ...f, [k]: v }));

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      const shared = {
        fname: form.fname,
        lname: form.lname,
        email: form.email,
        phone: form.phone,
        dob: form.dob,
        role: form.role,
        username: form.username,
        occupation: form.occupation || null,
      };
      if (isEdit && existing) {
        // PUT /users/{id} replaces the whole record and takes no password —
        // password changes go through /users/{id}/change-password instead.
        await api.put(`/users/${existing.user_id}`, shared);
      } else {
        await api.post("/users", { ...shared, password: form.password });
      }
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't save user.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title={title}>
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
          <TextInput
            label="Date of birth"
            type="date"
            value={form.dob}
            onChange={set("dob")}
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectInput
            label="Role"
            value={form.role}
            onChange={(v) => setForm((f) => ({ ...f, role: v as Role }))}
            options={ROLES}
          />
          <TextInput
            label="Occupation"
            value={form.occupation}
            onChange={set("occupation")}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <TextInput
            label="Username"
            value={form.username}
            onChange={set("username")}
            required
          />
          {!isEdit && (
            <TextInput
              label="Password"
              type="password"
              value={form.password}
              onChange={set("password")}
              required
            />
          )}
        </div>

        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton type="submit" disabled={saving}>
            {saving ? "Saving…" : isEdit ? "Save changes" : "Add user"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}
