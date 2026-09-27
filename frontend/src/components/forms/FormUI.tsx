import type { ReactNode } from "react";
import { CircleAlert, CircleCheck } from "lucide-react";
export function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="grid min-w-0 gap-2 text-xs font-medium text-muted-foreground">
      {label}
      {children}
    </label>
  );
}
export function PageHeading({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string;
  title: string;
  description?: string;
  children?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-5">
      <div className="min-w-0">
        <p className="eyebrow mb-3 flex items-center gap-2">
          <span className="size-1.5 rounded-full bg-primary" />
          {eyebrow}
        </p>
        <h1 className="text-2xl font-semibold leading-tight md:text-3xl">
          {title}
        </h1>
        {description && (
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            {description}
          </p>
        )}
      </div>
      {children}
    </div>
  );
}
export function Panel({
  title,
  action,
  children,
}: {
  title: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="surface space-y-5 p-5 md:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b pb-4">
        <h2 className="text-base font-semibold">{title}</h2>
        {action}
      </div>
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
          className="flex items-start gap-2 rounded-lg border border-destructive/20 bg-destructive/5 p-3 text-sm leading-relaxed text-destructive"
        >
          <CircleAlert
            size={18}
            className="mt-0.5 shrink-0"
            aria-hidden="true"
          />
          {error}
        </p>
      )}
      {message && (
        <p
          role="status"
          className="flex items-start gap-2 rounded-lg border border-primary/20 bg-accent p-3 text-sm leading-relaxed text-accent-foreground"
        >
          <CircleCheck
            size={18}
            className="mt-0.5 shrink-0"
            aria-hidden="true"
          />
          {message}
        </p>
      )}
    </>
  );
}
