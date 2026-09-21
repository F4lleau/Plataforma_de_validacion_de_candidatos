import { stateLabels } from "../../services/reporting.service";
const labels: Record<string, string> = {
  ...stateLabels,
  ok: "Verificado",
  warning: "Observación",
  pendiente: "Pendiente",
  error: "Error",
};
const tones: Record<string, string> = {
  borrador: "border-slate-200 bg-slate-50 text-slate-600",
  incompleta: "border-amber-200 bg-amber-50 text-amber-800",
  en_validacion: "border-blue-200 bg-blue-50 text-blue-800",
  rechazada_composicion: "border-amber-200 bg-amber-50 text-amber-800",
  enviada_admin: "border-blue-200 bg-blue-50 text-blue-800",
  aprobada_sistema: "border-emerald-200 bg-emerald-50 text-emerald-800",
  ok: "border-emerald-200 bg-emerald-50 text-emerald-800",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  pendiente: "border-slate-200 bg-slate-50 text-slate-600",
  error: "border-red-200 bg-red-50 text-red-800",
};
export default function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-flex max-w-full items-center gap-1.5 rounded-md border px-2 py-1 text-[11px] font-medium leading-tight ${tones[status] ?? tones.borrador}`}
    >
      <span
        className="size-1.5 shrink-0 rounded-full bg-current"
        aria-hidden="true"
      />
      {labels[status] ?? status}
    </span>
  );
}
