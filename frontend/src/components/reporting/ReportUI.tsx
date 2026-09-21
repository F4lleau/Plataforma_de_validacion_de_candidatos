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
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {[
        ["Listas", data.total_lists],
        ["Candidatos", data.total_candidates],
        ["Enviadas", data.sent_lists],
        ["Aprobadas", data.approved_lists],
        ["Incompletas", data.incomplete_lists],
        ["Composición observada", data.rejected_lists],
        ...(data.active_apoderados === null
          ? []
          : [["Apoderados activos", data.active_apoderados]]),
        ["Aprobación", `${data.approval_rate}%`],
      ].map(([label, value]) => (
        <div className="rounded-xl border bg-card p-4" key={label}>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="mt-2 text-3xl font-bold">{value}</p>
        </div>
      ))}
    </div>
  );
}
export function ListTable({ items }: { items: ReportList[] }) {
  return (
    <div
      className="max-w-full overflow-x-auto"
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
                {stateLabels[l.status] ?? l.status}
              </td>
              <td className="border-b p-3">
                {l.apoderados.map((a) => a.name).join(", ") || "Sin asignar"}
              </td>
              <td className="border-b p-3">
                <Link className="text-primary underline" to={`/listas/${l.id}`}>
                  Ver lista
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {items.length === 0 && (
        <p className="p-4">No hay listas para estos filtros.</p>
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
      <span>
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
