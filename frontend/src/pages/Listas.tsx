import StatusBadge from "../components/reporting/StatusBadge";
import { stateLabels } from "../services/reporting.service";
import { PageHeading } from "../components/forms/FormUI";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useForm, useWatch } from "react-hook-form";
import { useRemote } from "../hooks/useRemote";
import { Field, Panel, Feedback } from "../components/forms/FormUI";
import {
  save,
  type ListRow,
  type Module,
  type Election,
  type Office,
  type Municipality,
} from "../services/management.service";
import { useAuthStore } from "../stores/auth.store";

export default function Listas() {
  const admin = useAuthStore((s) => s.user?.role === "admin");
  const modules = useRemote<Module[]>("/auth/modules");
  const [page, setPage] = useState(1);
  const [revision, refresh] = useState(0);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const lists = useRemote<{ items: ListRow[]; total: number }>(
    `/lists/page?page=${page}&search=${encodeURIComponent(search)}&status=${status}`,
    revision,
  );
  const elections = useRemote<Election[]>("/elections/");
  const offices = useRemote<Office[]>("/offices/");
  const municipalities = useRemote<Municipality[]>("/municipalities/");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const f = useForm({
    defaultValues: {
      list_name: "",
      list_number: "",
      election_id: 0,
      office_id: 0,
      municipality_id: 0,
    },
  });
  const electionId = useWatch({ control: f.control, name: "election_id" });
  const officeId = useWatch({ control: f.control, name: "office_id" });
  const office = offices.data?.find((o) => o.id === Number(officeId));
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Gestión electoral"
        title="Listas electorales"
        description="Consultá tus listas, continuá la carga o creá una nueva."
      />
      <Panel title="Mis listas">
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Buscar nombre o número">
            <input
              className="field"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </Field>
          <Field label="Estado">
            <select
              className="field"
              value={status}
              onChange={(e) => {
                setStatus(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Todos</option>
              {[
                "borrador",
                "incompleta",
                "en_validacion",
                "rechazada_composicion",
                "enviada_admin",
                "aprobada_sistema",
              ].map((s) => (
                <option key={s} value={s}>
                  {stateLabels[s] ?? s}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <Feedback error={lists.error} />
        {lists.loading && <p role="status">Cargando...</p>}
        {lists.data?.items.length === 0 && (
          <p>
            No hay listas para estos filtros. El acceso requiere módulo
            habilitado y asignación por lista.
          </p>
        )}
        <div className="grid gap-3 lg:grid-cols-2">
          {lists.data?.items.map((l) => (
            <article
              className="space-y-3 rounded-xl border bg-muted/20 p-5"
              key={l.id}
            >
              <h3 className="text-lg font-semibold">
                {l.list_number ?? "Sin número"} · {l.list_name}
              </h3>
              <p>
                {offices.data?.find((o) => o.id === l.office_id)?.name} ·{" "}
                {municipalities.data?.find((m) => m.id === l.municipality_id)
                  ?.name ?? "Provincial"}
              </p>
              <p className="text-sm">
                <span className="mr-3 text-muted-foreground">
                  {l.candidate_count} candidatos
                </span>
                <StatusBadge status={l.status} />
              </p>
              <Link className="secondary inline-block" to={`/listas/${l.id}`}>
                {["borrador", "incompleta", "rechazada_composicion"].includes(
                  l.status,
                )
                  ? "Continuar carga"
                  : "Ver lista"}
              </Link>
            </article>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            className="secondary"
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
          >
            Anterior
          </button>
          <span>
            Página {page} · {lists.data?.total ?? 0} listas
          </span>
          <button
            className="secondary"
            disabled={page * 25 >= (lists.data?.total ?? 0)}
            onClick={() => setPage(page + 1)}
          >
            Siguiente
          </button>
        </div>
      </Panel>
      <Panel title="Crear lista">
        <form
          className="space-y-4"
          onSubmit={f.handleSubmit(async (v) => {
            try {
              const result = await save<ListRow>("/lists/", {
                ...v,
                election_id: Number(v.election_id),
                office_id: Number(v.office_id),
                municipality_id: office?.municipality_based
                  ? Number(v.municipality_id)
                  : null,
              });
              setError("");
              setMessage(`Lista ${result.list_name} creada en borrador.`);
              refresh((n) => n + 1);
              f.reset();
            } catch (e) {
              setError((e as Error).message);
            }
          })}
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label="Nombre de lista">
              <input
                className="field"
                required
                maxLength={255}
                {...f.register("list_name")}
              />
            </Field>
            <Field label="Número de lista">
              <input
                className="field"
                required
                maxLength={40}
                {...f.register("list_number")}
              />
            </Field>
            <Field label="Elección">
              <select className="field" required {...f.register("election_id")}>
                <option value="0">Seleccionar</option>
                {elections.data?.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Cargo">
              <select className="field" required {...f.register("office_id")}>
                <option value="0">Seleccionar</option>
                {offices.data
                  ?.filter(
                    (o) =>
                      admin ||
                      modules.data?.some(
                        (m) =>
                          m.election_id === Number(electionId) &&
                          m.office_id === o.id,
                      ),
                  )
                  .map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.name}
                    </option>
                  ))}
              </select>
            </Field>
            {office?.municipality_based && (
              <Field label="Distrito electoral">
                <select className="field" {...f.register("municipality_id")}>
                  <option value="0">Seleccionar</option>
                  {municipalities.data
                    ?.filter(
                      (v) =>
                        admin ||
                        modules.data?.some(
                          (m) =>
                            m.election_id === Number(electionId) &&
                            m.office_id === Number(officeId) &&
                            m.municipality_id === v.id,
                        ),
                    )
                    .map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name}
                      </option>
                    ))}
                </select>
              </Field>
            )}
          </div>
          <Feedback
            error={
              error || elections.error || offices.error || municipalities.error
            }
            message={message}
          />
          <button className="action" disabled={f.formState.isSubmitting}>
            Crear lista
          </button>
        </form>
      </Panel>
    </div>
  );
}
