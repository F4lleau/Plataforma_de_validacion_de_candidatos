import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useRemote } from "../hooks/useRemote";
import { Field, Feedback, Panel } from "../components/forms/FormUI";
import { Pager } from "../components/reporting/ReportUI";
import { query, type Page } from "../services/reporting.service";
const actionLabels: Record<string, string> = {
  "catalog.created": "Configuración creada",
  "catalog.updated": "Configuración actualizada",
  "rules.version_created": "Nueva versión de reglas",
  "user.created": "Apoderado creado",
  "user.updated": "Apoderado actualizado",
  "padron.imported": "Padrón importado",
  "list.created": "Lista creada",
  "list.updated": "Lista corregida",
  "list.assigned": "Asignaciones actualizadas",
  "list.rules_adopted": "Reglas vinculadas",
  "candidate.created": "Candidato registrado",
  "candidate.updated": "Candidato corregido",
  "candidate.revalidated": "Candidato revalidado",
  "candidate.validation_evaluated": "Controles del candidato evaluados",
  "list.composition_evaluated": "Composición evaluada",
  "list.submitted": "Lista enviada",
  "list.automatically_approved": "Aprobación automática",
  "export.generated": "Exportación generada",
};
interface Event {
  id: number;
  actor_id: number | null;
  actor_name: string;
  action: string;
  entity_type: string;
  entity_id: number | null;
  details: Record<string, unknown> | null;
  created_at: string;
}
export default function Auditoria() {
  const [params] = useSearchParams();
  const [filters, setFilters] = useState({
    actor_id: "",
    action: "",
    entity_type: params.get("entity_type") ?? "",
    entity_id: params.get("entity_id") ?? "",
    list_id: params.get("list_id") ?? "",
    date_from: "",
    date_to: "",
  });
  const [page, setPage] = useState(1);
  const data = useRemote<Page<Event>>(
    `/admin/audit?${query({ ...filters, page })}`,
  );
  return (
    <div className="space-y-6">
      <h1 className="font-heading text-3xl font-bold">Auditoría</h1>
      <p>
        Acciones registradas, con fecha local y actor. El historial se conserva
        aunque la cuenta esté desactivada.
      </p>
      <Panel title="Filtros">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {(
            [
              "actor_id",
              "action",
              "entity_type",
              "entity_id",
              "list_id",
              "date_from",
              "date_to",
            ] as const
          ).map((k, i) => (
            <Field
              key={k}
              label={
                [
                  "ID del actor",
                  "Acción exacta",
                  "Entidad",
                  "ID de entidad",
                  "Historial de lista (ID)",
                  "Desde",
                  "Hasta",
                ][i]
              }
            >
              <input
                className="field"
                type={
                  k.startsWith("date")
                    ? "date"
                    : k.endsWith("_id")
                      ? "number"
                      : "text"
                }
                min={k.endsWith("_id") ? 1 : undefined}
                value={filters[k]}
                onChange={(e) => {
                  setFilters({ ...filters, [k]: e.target.value });
                  setPage(1);
                }}
              />
            </Field>
          ))}
        </div>
      </Panel>
      <Feedback error={data.error} />
      {data.loading && <p role="status">Cargando historial...</p>}
      {data.data?.items.length === 0 && (
        <p>No hay eventos para estos filtros.</p>
      )}
      {data.data?.items.map((e) => (
        <article className="space-y-2 rounded-lg border bg-card p-4" key={e.id}>
          <p className="font-semibold">{actionLabels[e.action] ?? e.action}</p>
          <p className="text-sm">
            {e.actor_name} ·{" "}
            {new Date(e.created_at + "Z").toLocaleString("es-AR", {
              timeZone: "America/Argentina/Cordoba",
            }) + " (Argentina, UTC−3)"}{" "}
            · {e.entity_type} {e.entity_id ?? ""}
          </p>
          {e.entity_type === "electoral_lists" && e.entity_id && (
            <Link
              className="text-sm text-primary underline"
              to={`/listas/${e.entity_id}`}
            >
              Ver lista
            </Link>
          )}
          <details>
            <summary className="cursor-pointer text-sm">
              Cambios y referencias
            </summary>
            <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-words rounded bg-muted p-3 text-xs">
              {JSON.stringify(e.details, null, 2)}
            </pre>
          </details>
        </article>
      ))}
      {data.data && (
        <Pager page={page} total={data.data.total} onChange={setPage} />
      )}
    </div>
  );
}
