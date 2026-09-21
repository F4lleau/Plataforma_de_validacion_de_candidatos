import { stateLabels } from "../services/reporting.service";
import CompositionPanel from "../components/reporting/CompositionPanel";
import { useState, useEffect } from "react";
import { Link, useParams, useLocation } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useRemote } from "../hooks/useRemote";
import { Field, Panel, Feedback } from "../components/forms/FormUI";
import {
  save,
  type ListDetail,
  type CandidateData,
  type Apoderado,
} from "../services/management.service";
import { useAuthStore } from "../stores/auth.store";
const resultLabels: Record<string, string> = {
  ok: "Verificado",
  warning: "Observación",
  pendiente: "Pendiente",
  error: "Error",
};

function CandidateEditor({
  list,
  candidate,
  changed,
}: {
  list: ListDetail;
  candidate?: CandidateData;
  changed: () => void;
}) {
  const f = useForm({
    defaultValues: {
      dni: candidate?.person.dni ?? "",
      first_name: candidate?.person.first_name ?? "",
      last_name: candidate?.person.last_name ?? "",
      birth_date: candidate?.person.birth_date ?? "",
      gender: candidate?.person.gender ?? "F",
      address: candidate?.person.address ?? "",
      position: candidate?.position ?? 0,
    },
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  async function submit(action: "draft" | "validate") {
    await f.handleSubmit(async (v) => {
      try {
        await save(
          `/lists/${list.id}/candidates${candidate ? `/${candidate.id}` : ""}`,
          {
            ...v,
            position: Number(v.position),
            address: v.address || null,
            municipality_id: candidate?.person.municipality_id ?? null,
            action,
          },
          candidate ? "PUT" : "POST",
        );
        setError("");
        setMessage(
          action === "draft"
            ? "Borrador guardado; afiliación registrada."
            : "Guardado y validado. Revise los resultados de cada control.",
        );
        changed();
      } catch (e) {
        setError((e as Error).message);
      }
    })();
  }
  return (
    <form
      className="space-y-4"
      onSubmit={(e) => {
        e.preventDefault();
        void submit("validate");
      }}
    >
      <div className="grid gap-3 sm:grid-cols-2">
        {(
          ["dni", "first_name", "last_name", "birth_date", "address"] as const
        ).map((k, i) => (
          <Field
            key={k}
            label={
              [
                "DNI",
                "Nombre",
                "Apellido",
                "Fecha de nacimiento",
                "Domicilio (opcional)",
              ][i]
            }
          >
            <input
              className="field"
              type={k === "birth_date" ? "date" : "text"}
              pattern={k === "dni" ? "[0-9]{7,9}" : undefined}
              required={k !== "address"}
              {...f.register(k, {
                required: k !== "address" ? "Completá este campo." : false,
              })}
            />
            {f.formState.errors[k] && (
              <span role="alert" className="text-destructive">
                {f.formState.errors[k]?.message}
              </span>
            )}
          </Field>
        ))}
        <Field label="Género">
          <select className="field" {...f.register("gender")}>
            <option value="F">Femenino</option>
            <option value="M">Masculino</option>
            <option value="X">X</option>
          </select>
        </Field>
        <Field label="Posición en la lista">
          <select className="field" {...f.register("position")}>
            <option value="0">Seleccionar posición</option>
            {list.rule?.rules.positions.map((p) => (
              <option key={p.position} value={p.position}>
                {p.position}. {p.name} ({p.group})
              </option>
            ))}
          </select>
        </Field>
      </div>
      <p className="text-sm text-muted-foreground">
        La ausencia en padrón genera una advertencia y permite guardar. RENAPER
        permanece pendiente hasta contar con el proveedor.
      </p>
      <Feedback error={error} message={message} />
      <div className="flex flex-wrap gap-3">
        <button
          className="secondary"
          type="button"
          disabled={f.formState.isSubmitting}
          onClick={() => void submit("draft")}
        >
          Guardar borrador
        </button>
        <button className="action" disabled={f.formState.isSubmitting}>
          Guardar y validar
        </button>
      </div>
    </form>
  );
}
function Assignments({
  list,
  changed,
}: {
  list: ListDetail;
  changed: () => void;
}) {
  const users = useRemote<Apoderado[]>("/users/");
  const [ids, setIds] = useState(list.assigned_user_ids);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <Panel title="Apoderados asignados">
      <p className="text-sm">
        La asignación requiere también un módulo habilitado para esta elección,
        cargo y distrito.
      </p>
      {users.data?.map((u) => (
        <label className="flex gap-2" key={u.id}>
          <input
            type="checkbox"
            checked={ids.includes(u.id)}
            onChange={(e) =>
              setIds(
                e.target.checked
                  ? [...ids, u.id]
                  : ids.filter((id) => id !== u.id),
              )
            }
          />
          {u.full_name}
        </label>
      ))}
      <Feedback error={error || users.error} />
      <button
        className="action"
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          try {
            await save(
              `/lists/${list.id}/assignments`,
              { user_ids: ids },
              "PUT",
            );
            setError("");
            changed();
          } catch (e) {
            setError((e as Error).message);
          } finally {
            setBusy(false);
          }
        }}
      >
        Guardar asignaciones
      </button>
    </Panel>
  );
}
function ListEditor({
  list,
  changed,
}: {
  list: ListDetail;
  changed: () => void;
}) {
  const f = useForm({
    defaultValues: {
      list_name: list.list_name,
      list_number: list.list_number ?? "",
    },
  });
  const [error, setError] = useState("");
  return (
    <form
      className="flex flex-wrap items-end gap-3"
      onSubmit={f.handleSubmit(async (v) => {
        try {
          await save(`/lists/${list.id}`, v, "PUT");
          setError("");
          changed();
        } catch (e) {
          setError((e as Error).message);
        }
      })}
    >
      <Field label="Nombre">
        <input className="field" required {...f.register("list_name")} />
      </Field>
      <Field label="Número">
        <input className="field" required {...f.register("list_number")} />
      </Field>
      <button className="secondary" disabled={f.formState.isSubmitting}>
        Guardar datos de lista
      </button>
      <Feedback error={error} />
    </form>
  );
}
export default function ListaDetalle() {
  const { id } = useParams();
  const { hash } = useLocation();
  const [revision, refresh] = useState(0);
  const remote = useRemote<ListDetail>(`/lists/${id}`, revision);
  const admin = useAuthStore((s) => s.user?.role === "admin");
  const [selected, setSelected] = useState<CandidateData>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const list = remote.data;
  const changed = () => refresh((v) => v + 1);
  useEffect(() => {
    if (list && hash) document.getElementById(hash.slice(1))?.scrollIntoView();
  }, [list, hash]);
  if (!list)
    return (
      <Feedback
        error={remote.error}
        message={remote.loading ? "Cargando lista..." : undefined}
      />
    );
  const editable = ["borrador", "incompleta", "rechazada_composicion"].includes(
    list.status,
  );
  return (
    <div className="space-y-6">
      <Link className="text-primary underline" to="/listas">
        Volver a listas
      </Link>
      <h1 className="font-heading text-3xl font-bold">{list.list_name}</h1>
      <p>
        {stateLabels[list.status] ?? list.status} · {list.candidate_count}{" "}
        candidatos ·{" "}
        {list.rule
          ? `Reglas versión ${list.rule.version}`
          : "Sin reglas vinculadas"}
      </p>
      {list.rule?.rules.template_is_test && (
        <p
          role="status"
          className="rounded-md border border-amber-400 bg-amber-50 p-3 text-amber-950"
        >
          Plantilla de prueba. No representa cargos oficiales ni habilita
          aprobación real.
        </p>
      )}
      <Feedback error={error || remote.error} />
      {editable && (
        <Panel title="Datos de la lista">
          <ListEditor list={list} changed={changed} />
        </Panel>
      )}
      {admin && (
        <Assignments
          key={`${list.id}-${list.assigned_user_ids.join(",")}`}
          list={list}
          changed={changed}
        />
      )}
      <CompositionPanel
        listId={list.id}
        state={list.status}
        composition={list.composition}
        changed={changed}
      />
      {admin && (
        <Link
          className="text-primary underline"
          to={`/auditoria?list_id=${list.id}`}
        >
          Historial de esta lista
        </Link>
      )}
      {list.submitted_at && (
        <p>Enviada: {new Date(list.submitted_at + "Z").toLocaleString()}</p>
      )}
      <Panel title="Candidatos y validaciones">
        {list.candidates.length === 0 && <p>Sin candidatos cargados.</p>}
        {list.candidates.map((c) => (
          <article
            id={`candidato-${c.id}`}
            className="space-y-3 rounded-lg border p-4"
            key={c.id}
          >
            <h3 className="font-semibold">
              {c.position}. {c.person.last_name}, {c.person.first_name} · DNI{" "}
              {c.person.dni} · Género {c.person.gender}
            </h3>
            {c.validations.length === 0 && (
              <p>Datos históricos sin validaciones vigentes.</p>
            )}
            <div className="grid gap-3 lg:grid-cols-3">
              {c.validations.map((v) => (
                <div key={v.type} className="rounded-md bg-muted p-3 text-sm">
                  <p className="font-semibold">
                    {v.type === "afiliacion"
                      ? "Afiliación"
                      : v.type === "renaper"
                        ? "RENAPER"
                        : "Edad y requisitos"}{" "}
                    · {resultLabels[v.status] ?? v.status}
                  </p>
                  <p>{v.message}</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {new Date(v.validated_at + "Z").toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
            {c.history && c.history.length > 0 && (
              <details>
                <summary className="cursor-pointer text-sm">
                  Historial de validaciones
                </summary>
                {c.history.map((v) => (
                  <p className="py-1 text-xs" key={v.id}>
                    {v.type} · revisión {v.revision ?? "histórica"} · {v.status}
                    : {v.message} (
                    {new Date(v.validated_at + "Z").toLocaleString()})
                  </p>
                ))}
              </details>
            )}
            {admin && (
              <Link
                className="text-sm text-primary underline"
                to={`/auditoria?entity_type=candidates&entity_id=${c.id}`}
              >
                Auditoría del candidato
              </Link>
            )}
            {editable && (
              <div className="flex gap-3">
                <button className="secondary" onClick={() => setSelected(c)}>
                  Editar candidato
                </button>
                <button
                  className="secondary"
                  disabled={busy}
                  onClick={async () => {
                    setBusy(true);
                    try {
                      await save(
                        `/lists/${list.id}/candidates/${c.id}/validate`,
                        {},
                      );
                      setError("");
                      changed();
                    } catch (e) {
                      setError((e as Error).message);
                    } finally {
                      setBusy(false);
                    }
                  }}
                >
                  Volver a validar
                </button>
              </div>
            )}
          </article>
        ))}
      </Panel>
      {editable && list.rule && (
        <Panel title={selected ? "Editar candidato" : "Agregar candidato"}>
          <button className="secondary" onClick={() => setSelected(undefined)}>
            Nuevo candidato
          </button>
          <CandidateEditor
            key={`${selected?.id ?? "new"}-${selected?.revision ?? 0}`}
            list={list}
            candidate={selected}
            changed={changed}
          />
        </Panel>
      )}
      {!list.rule && (
        <Panel title="Plantilla pendiente">
          <p>
            Esta lista histórica conserva sus datos. Para cargar nuevos
            candidatos, configure reglas y cree una lista nueva. Una lista vacía
            puede adoptar la versión actual.
          </p>
          {admin && editable && list.candidate_count === 0 && (
            <button
              className="secondary"
              onClick={async () => {
                try {
                  await save(`/lists/${list.id}/rules/adopt`, {});
                  changed();
                } catch (e) {
                  setError((e as Error).message);
                }
              }}
            >
              Adoptar reglas actuales
            </button>
          )}
        </Panel>
      )}
      <p className="text-sm text-muted-foreground">
        La aprobación requiere controles obligatorios vigentes. Un envío con
        pendientes conserva la revisión administrativa.
      </p>
    </div>
  );
}
