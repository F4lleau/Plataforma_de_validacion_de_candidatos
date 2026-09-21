import type { ReactNode } from "react";
export function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="grid gap-1 text-sm font-medium">
      {label}
      {children}
    </label>
  );
}
export function Panel({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="space-y-4 rounded-xl border bg-card p-5">
      <h2 className="font-heading text-xl font-semibold">{title}</h2>
      {children}
    </section>
  );
}
export function Feedback({
  error,
  message,
}: {
  error?: string;
  message?: string;
}) {
  return (
    <>
      {error && (
        <p
          role="alert"
          className="rounded-md bg-destructive/10 p-3 text-destructive"
        >
          {error}
        </p>
      )}
      {message && (
        <p role="status" className="rounded-md bg-primary/10 p-3">
          {message}
        </p>
      )}
    </>
  );
}
