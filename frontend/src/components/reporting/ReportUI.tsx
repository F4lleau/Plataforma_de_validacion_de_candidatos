import {
  Files,
  Users,
  Send,
  CircleCheck,
  CircleDashed,
  ClipboardList,
  UserRoundCheck,
  Percent,
  ArrowUpRight,
  Inbox,
} from "lucide-react";
import StatusBadge from "./StatusBadge";
import { Link } from "react-router-dom";
import { Field } from "../forms/FormUI";
import { useRemote } from "../../hooks/useRemote";
import type {
  Election,
  Office,
  Municipality,
  Apoderado,
} from "../../services/management.service";
import {
  stateLabels,
  type Filters,
  type ReportList,
  type Summary,
} from "../../services/reporting.service";
export function ReportFilters({
  value,
  onChange,
}: {
  value: Filters;
  onChange: (v: Filters) => void;
}) {
  const elections = useRemote<Election[]>("/elections/");
  const offices = useRemote<Office[]>("/offices/");
  const municipalities = useRemote<Municipality[]>("/municipalities/");
  const users = useRemote<Apoderado[]>("/users/");
  const options = [
    [
      "election_id",
      "Elección",
      elections.data?.map((e) => ({ id: e.id, name: e.name })),
    ],
    [
      "office_id",
      "Cargo",
      offices.data?.map((o) => ({ id: o.id, name: o.name })),
    ],
    [
      "municipality_id",
      "Localidad",
      municipalities.data?.map((m) => ({ id: m.id, name: m.name })),
    ],
    [
      "apoderado_id",
      "Apoderado",
      users.data?.map((u) => ({ id: u.id, name: u.full_name })),
    ],
  ] as const;
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {options.map(([key, label, items]) => (
        <Field label={label} key={key}>
          <select
            className="field"
            value={value[key]}
            onChange={(e) => onChange({ ...value, [key]: e.target.value })}
          >
            <option value="">Todos</option>
            {items?.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>
        </Field>
      ))}
      <Field label="Estado">
        <select
          className="field"
          value={value.status}
          onChange={(e) => onChange({ ...value, status: e.target.value })}
        >
          <option value="">Todos</option>
          {Object.entries(stateLabels).map(([k, l]) => (
            <option key={k} value={k}>
              {l}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Nombre o número">
        <input
          className="field"
          value={value.search}
          onChange={(e) => onChange({ ...value, search: e.target.value })}
        />
      </Field>
      {(elections.error ||
        offices.error ||
        municipalities.error ||
        users.error) && (
        <p role="alert">
          No se pudieron cargar todos los filtros. Recargá la página.
        </p>
      )}
    </div>
  );
}
export function Metrics({ data }: { data: Summary }) {
  const metrics = [
    {
      label: "Listas electorales",
      value: data.total_lists,
      icon: Files,
      detail: "En el alcance seleccionado",
    },
    {
      label: "Candidatos",
      value: data.total_candidates,
      icon: Users,
      detail: "Registrados en las listas",
    },
    {
      label: "Enviadas",
      value: data.sent_lists,
      icon: Send,
      detail: "Para revisión administrativa",
    },
    {
      label: "Aprobadas",
      value: data.approved_lists,
      icon: CircleCheck,
      detail: "Por los controles del sistema",
    },
    {
      label: "Incompletas",
      value: data.incomplete_lists,
      icon: CircleDashed,
      detail: "Con carga pendiente",
    },
    {
      label: "Composición observada",
      value: data.rejected_lists,
      icon: ClipboardList,
      detail: "Requieren correcciones",
    },
    ...(data.active_apoderados === null
      ? []
      : [
          {
            label: "Apoderados activos",
            value: data.active_apoderados,
            icon: UserRoundCheck,
            detail: "Dentro del alcance consultado",
          },
        ]),
    {
      label: "Aprobación",
      value: `${data.approval_rate}%`,
      icon: Percent,
      detail: "Del total de listas",
    },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
      {metrics.map(({ label, value, icon: Icon, detail }, i) => (
        <div
          className={`surface p-4 md:p-5 ${i === metrics.length - 1 && metrics.length % 2 !== 0 ? "col-span-2" : ""} ${i === 0 ? "!border-primary/25 bg-gradient-to-br from-accent/70 to-card" : ""}`}
          key={label}
        >
          <div className="flex items-center justify-between gap-2">
            <p className="text-xs font-medium text-muted-foreground">{label}</p>
            <Icon
              size={17}
              strokeWidth={1.6}
              className={i === 0 ? "text-primary" : "text-muted-foreground/70"}
              aria-hidden="true"
            />
          </div>
          <p className="mt-4 font-mono text-3xl font-medium tracking-tight">
            {typeof value === "number" ? value.toLocaleString("es-AR") : value}
          </p>
          <p className="mt-2 text-[11px] text-muted-foreground">{detail}</p>
        </div>
      ))}
    </div>
  );
}
export function ListTable({ items }: { items: ReportList[] }) {
  return (
    <div
      className="max-w-full overflow-x-auto rounded-xl border bg-card"
      tabIndex={0}
      role="region"
      aria-label="Listas electorales"
    >
      <table className="w-full text-left text-sm">
        <thead>
          <tr>
            {[
              "Número / Lista",
              "Cargo / Localidad",
              "Candidatos",
              "Estado",
              "Apoderados",
              "Acción",
            ].map((h) => (
              <th key={h} className="border-b p-3">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((l) => (
            <tr key={l.id}>
              <td className="border-b p-3">
                <p className="font-semibold">
                  {l.list_number ?? "Sin número"} · {l.list_name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {l.election_name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {l.created_at
                    ? `Creada: ${new Date(l.created_at + "Z").toLocaleString()}`
                    : "Fecha histórica no disponible"}
                </p>
              </td>
              <td className="border-b p-3">
                {l.office_name}
                <br />
                {l.municipality_name}
              </td>
              <td className="border-b p-3">{l.candidate_count}</td>
              <td className="border-b p-3">
                <StatusBadge status={l.status} />
              </td>
              <td className="border-b p-3">
                {l.apoderados.map((a) => a.name).join(", ") || "Sin asignar"}
              </td>
              <td className="border-b p-3">
                <Link
                  className="text-link whitespace-nowrap"
                  to={`/listas/${l.id}`}
                >
                  Ver lista <ArrowUpRight size={14} aria-hidden="true" />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {items.length === 0 && (
        <div className="flex flex-col items-center gap-3 p-10 text-center text-sm text-muted-foreground">
          <Inbox size={28} strokeWidth={1.4} aria-hidden="true" />
          <p>No hay listas para estos filtros.</p>
        </div>
      )}
    </div>
  );
}
export function Pager({
  page,
  total,
  onChange,
}: {
  page: number;
  total: number;
  onChange: (n: number) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <button
        className="secondary"
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
      >
        Anterior
      </button>
      <span className="text-xs text-muted-foreground">
        Página {page} · {total} resultados
      </span>
      <button
        className="secondary"
        disabled={page * 25 >= total}
        onClick={() => onChange(page + 1)}
      >
        Siguiente
      </button>
    </div>
  );
}
