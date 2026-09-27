import type { ButtonHTMLAttributes, ReactNode } from "react";
import { X } from "lucide-react";

type ButtonVariant = "primary" | "secondary" | "ghost";

export function ActionButton({
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant }) {
  const base =
    "inline-flex min-h-9 items-center justify-center gap-2 rounded-full px-3.5 py-2 font-mono text-[11px] font-semibold uppercase tracking-[0.09em] transition-all disabled:opacity-50";
  const styles = {
    primary: "bg-[#00384a] text-white shadow-sm hover:bg-[#005a72]",
    secondary:
      "border border-[#9fc6d3] bg-white text-[#00384a] shadow-sm hover:border-[#5fa9c7] hover:bg-[#eaf6fa]",
    ghost: "text-[#00384a] hover:bg-[#eaf6fa]",
  };
  return (
    <button
      className={`${base} ${styles[variant]} ${className}`}
      {...props}
    />
  );
}

export function BadgeLink({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white px-2.5 py-1 font-mono text-[11px] font-medium uppercase tracking-[0.12em] text-slate-700">
      {children}
    </span>
  );
}

export function Modal({
  title,
  children,
  onClose,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/30 px-4 py-8"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      onKeyDown={(event) => {
        if (event.key === "Escape") onClose();
      }}
    >
      <div className="surface max-h-full w-full max-w-2xl overflow-auto p-0">
        <div className="flex items-center justify-between border-b px-5 py-4">
          <h2 id="modal-title" className="text-base font-semibold">
            {title}
          </h2>
          <ActionButton
            type="button"
            variant="ghost"
            className="!min-h-9 !px-2.5"
            aria-label="Cerrar"
            onClick={onClose}
          >
            <X size={16} aria-hidden="true" />
          </ActionButton>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}
