import { useEffect, useRef, type ReactNode } from "react";

/**
 * Dialog shell used by every create/edit form.
 *
 * <dialog> is used rather than a hand-rolled div because the browser gives us
 * focus trapping, Escape-to-close, and the backdrop for free — all things that
 * are easy to get subtly wrong when built by hand, and which matter for anyone
 * navigating by keyboard.
 */
export function Modal({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      onClick={(e) => {
        // Clicking the backdrop closes; clicking the panel shouldn't.
        if (e.target === ref.current) onClose();
      }}
      className="m-auto w-full max-w-lg rounded-card border border-border-light bg-bg-white p-0 backdrop:bg-black/40"
    >
      <div className="flex items-center justify-between border-b border-border-light px-5 py-4">
        <h2 className="font-semibold text-text-dark">{title}</h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="flex h-8 w-8 items-center justify-center rounded-[10px] text-text-body transition-colors hover:bg-bg-surface"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            aria-hidden="true"
          >
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div className="max-h-[70vh] overflow-y-auto px-5 py-5">{children}</div>
    </dialog>
  );
}

const inputClass =
  "mt-1 h-10 w-full rounded-[10px] border border-border-light px-3 text-sm text-text-dark outline-none focus:border-accent focus:ring-2 focus:ring-accent/30";

export function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-text-dark">{label}</span>
      {children}
    </label>
  );
}

export function TextInput({
  label,
  value,
  onChange,
  type = "text",
  required,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
  placeholder?: string;
}) {
  return (
    <Field label={label}>
      <input
        type={type}
        value={value}
        required={required}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className={inputClass}
      />
    </Field>
  );
}

export function NumberInput({
  label,
  value,
  onChange,
  step = "1",
  required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  step?: string;
  required?: boolean;
}) {
  return (
    <Field label={label}>
      <input
        type="number"
        step={step}
        value={value}
        required={required}
        onChange={(e) => onChange(e.target.value)}
        className={inputClass}
      />
    </Field>
  );
}

export function SelectInput({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <Field label={label}>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={inputClass}
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </Field>
  );
}

export function TextArea({
  label,
  value,
  onChange,
  required,
  rows = 3,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  rows?: number;
}) {
  return (
    <Field label={label}>
      <textarea
        value={value}
        rows={rows}
        required={required}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-[10px] border border-border-light px-3 py-2 text-sm text-text-dark outline-none focus:border-accent focus:ring-2 focus:ring-accent/30"
      />
    </Field>
  );
}

export function PrimaryButton({
  children,
  onClick,
  type = "button",
  disabled,
}: {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className="h-10 rounded-[10px] bg-accent px-4 text-sm font-semibold text-bg-darkest transition-colors hover:bg-accent-hover focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:outline-none disabled:opacity-60"
    >
      {children}
    </button>
  );
}

export function SecondaryButton({
  children,
  onClick,
}: {
  children: ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="h-10 rounded-[10px] border border-border-light px-4 text-sm font-medium text-text-body transition-colors hover:bg-bg-surface"
    >
      {children}
    </button>
  );
}

/** Small inline action used inside table rows. */
export function RowAction({
  children,
  onClick,
  tone = "accent",
}: {
  children: ReactNode;
  onClick: () => void;
  tone?: "accent" | "danger";
}) {
  const tones = {
    accent: "border-accent text-accent hover:bg-accent hover:text-bg-darkest",
    danger: "border-danger text-danger hover:bg-danger hover:text-bg-white",
  };
  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      className={`rounded-[8px] border px-2.5 py-1 text-[11px] font-medium transition-colors ${tones[tone]}`}
    >
      {children}
    </button>
  );
}
