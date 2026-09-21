import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../stores/auth.store";
import { useRemote } from "../hooks/useRemote";
import { Field, Feedback, Panel } from "../components/forms/FormUI";
import { Metrics, ListTable } from "../components/reporting/ReportUI";
import type { Election } from "../services/management.service";
import type { Summary } from "../services/reporting.service";
export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const [election, setElection] = useState("");
  const elections = useRemote<Election[]>("/elections/");
  const data = useRemote<Summary>(
    `/dashboard/summary${election ? `?election_id=${election}` : ""}`,
  );
  return (
    <div className="space-y-6">
      <h1 className="font-heading text-3xl font-bold">
        Bienvenido, {user?.full_name}
      </h1>
      <Field label="Alcance electoral">
        <select
          className="field max-w-xl"
          value={election}
          onChange={(e) => setElection(e.target.value)}
        >
          <option value="">Todas las elecciones autorizadas</option>
          {elections.data?.map((e) => (
            <option key={e.id} value={e.id}>
              {e.name}
            </option>
          ))}
        </select>
      </Field>
      <Feedback error={data.error || elections.error} />
      {data.loading && <p role="status">Cargando resumen...</p>}
      {data.data && (
        <>
          <Metrics data={data.data} />
          <p className="text-sm text-muted-foreground">
            Aprobación = listas aprobadas / {data.data.approval_denominator}{" "}
            listas en el alcance seleccionado. Estados mutuamente excluyentes.
          </p>
          {user?.role === "apoderado" && (
            <Panel title="Mis módulos">
              {data.data.modules?.length === 0 ? (
                <p>
                  No tenés módulos habilitados. Solicitá la asignación al
                  administrador.
                </p>
              ) : (
                data.data.modules?.map((m) => (
                  <article className="rounded-lg border p-3" key={m.id}>
                    <p className="font-semibold">
                      {m.office_name} · {m.municipality_name}
                    </p>
                    <p className="text-sm">{m.election_name}</p>
                  </article>
                ))
              )}
              <Link className="action inline-block" to="/listas">
                Crear lista / continuar carga
              </Link>
            </Panel>
          )}
          <Panel title="Últimas listas">
            <ListTable items={data.data.recent_lists ?? []} />
            <Link
              className="text-primary underline"
              to={user?.role === "admin" ? "/validaciones" : "/listas"}
            >
              Ver todas las listas
            </Link>
          </Panel>
        </>
      )}
    </div>
  );
}
