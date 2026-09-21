import { PageHeading } from "../components/forms/FormUI";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Field, Panel, Feedback } from "../components/forms/FormUI";
import { useRemote } from "../hooks/useRemote";
import {
  save,
  type Apoderado,
  type Module,
  type Election,
  type Office,
  type Municipality,
} from "../services/management.service";
function Editor({ user, changed }: { user?: Apoderado; changed: () => void }) {
  const f = useForm({
    defaultValues: {
      username: user?.username ?? "",
      email: user?.email ?? "",
      full_name: user?.full_name ?? "",
      password: "",
      is_active: user?.is_active ?? true,
    },
  });
  const [modules, setModules] = useState<Module[]>(
    user?.modules.map((m) => ({
      election_id: m.election_id,
      office_id: m.office_id,
      municipality_id: m.municipality_id,
      enabled: m.enabled,
    })) ?? [],
  );
  const elections = useRemote<Election[]>("/elections/");
  const offices = useRemote<Office[]>("/offices/");
  const municipalities = useRemote<Municipality[]>("/municipalities/");
  const [module, setModule] = useState<Module>({
    election_id: 0,
    office_id: 0,
    municipality_id: null,
    enabled: true,
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const office = offices.data?.find((o) => o.id === module.office_id);
  return (
    <form
      className="space-y-4"
      onSubmit={f.handleSubmit(async (v) => {
        try {
          await save(
            `/users/${user?.id ?? ""}`,
            { ...v, password: v.password || null, modules },
            user ? "PUT" : "POST",
          );
          setError("");
          setMessage(
            "Apoderado guardado. Los cambios de acceso son inmediatos.",
          );
          f.setValue("password", "");
          changed();
        } catch (e) {
          setError((e as Error).message);
        }
      })}
    >
      <div className="grid gap-3 sm:grid-cols-2">
        {(["full_name", "username", "email", "password"] as const).map(
          (k, i) => (
            <Field
              key={k}
              label={
                [
                  "Nombre completo",
                  "Usuario",
                  "Correo electrónico",
                  user ? "Nueva contraseña (opcional)" : "Contraseña inicial",
                ][i]
              }
            >
              <input
                className="field"
                type={
                  k === "password"
                    ? "password"
                    : k === "email"
                      ? "email"
                      : "text"
                }
                autoComplete={k === "password" ? "new-password" : "off"}
                required={k !== "password" || !user}
                minLength={k === "password" ? 10 : 1}
                maxLength={k === "password" ? 72 : 255}
                {...f.register(k)}
              />
            </Field>
          ),
        )}
      </div>
      <label className="flex gap-2">
        <input type="checkbox" {...f.register("is_active")} />
        Cuenta activa
      </label>
      <p className="text-sm text-muted-foreground">
        Desactivar retira el acceso en la próxima solicitud y conserva las
        listas. Una contraseña nueva reemplaza la anterior. Entregala por el
        canal acordado con el apoderado.
      </p>
      <fieldset className="space-y-3 rounded-md border p-3">
        <legend>Módulos habilitados</legend>
        <div className="grid gap-3 sm:grid-cols-3">
          <Field label="Elección del módulo">
            <select
              className="field"
              value={module.election_id}
              onChange={(e) =>
                setModule({ ...module, election_id: Number(e.target.value) })
              }
            >
              <option value="0">Seleccionar</option>
              {elections.data?.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Cargo del módulo">
            <select
              className="field"
              value={module.office_id}
              onChange={(e) =>
                setModule({
                  ...module,
                  office_id: Number(e.target.value),
                  municipality_id: null,
                })
              }
            >
              <option value="0">Seleccionar</option>
              {offices.data?.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.name}
                </option>
              ))}
            </select>
          </Field>
          {office?.municipality_based && (
            <Field label="Municipio del módulo">
              <select
                className="field"
                value={module.municipality_id ?? 0}
                onChange={(e) =>
                  setModule({
                    ...module,
                    municipality_id: Number(e.target.value) || null,
                  })
                }
              >
                <option value="0">Seleccionar</option>
                {municipalities.data?.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
              </select>
            </Field>
          )}
        </div>
        <button
          className="secondary"
          type="button"
          disabled={
            !module.election_id ||
            !module.office_id ||
            (office?.municipality_based && !module.municipality_id)
          }
          onClick={() => {
            if (
              !modules.some(
                (m) =>
                  m.election_id === module.election_id &&
                  m.office_id === module.office_id &&
                  m.municipality_id === module.municipality_id,
              )
            )
              setModules([...modules, module]);
          }}
        >
          Agregar módulo
        </button>
        {modules.map((m, i) => (
          <div
            key={`${m.election_id}-${m.office_id}-${m.municipality_id}`}
            className="flex flex-wrap items-center justify-between gap-2 rounded-md bg-muted p-3"
          >
            <span>
              {elections.data?.find((e) => e.id === m.election_id)?.name} ·{" "}
              {offices.data?.find((o) => o.id === m.office_id)?.name} ·{" "}
              {municipalities.data?.find((v) => v.id === m.municipality_id)
                ?.name ?? "Provincial"}
            </span>
            <button
              className="secondary"
              type="button"
              onClick={() => setModules(modules.filter((_, n) => n !== i))}
            >
              Retirar módulo
            </button>
          </div>
        ))}
      </fieldset>
      <Feedback
        error={
          error || elections.error || offices.error || municipalities.error
        }
        message={message}
      />
      <button className="action" disabled={f.formState.isSubmitting}>
        Guardar apoderado
      </button>
    </form>
  );
}
export default function Usuarios() {
  const [revision, refresh] = useState(0);
  const data = useRemote<Apoderado[]>("/users/", revision);
  const [selected, setSelected] = useState<Apoderado>();
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Administración"
        title="Gestión de apoderados"
        description="Administrá las cuentas, los módulos habilitados y sus asignaciones."
      />
      <Feedback error={data.error} />
      <Panel title="Cuentas">
        <button className="secondary" onClick={() => setSelected(undefined)}>
          Nuevo apoderado
        </button>
        {data.loading && <p role="status">Cargando...</p>}
        {data.data?.map((u) => (
          <div
            key={u.id}
            className="flex flex-wrap items-center justify-between gap-3 border-b py-3"
          >
            <div>
              <p className="font-semibold">{u.full_name}</p>
              <p className="text-sm">
                {u.email} · {u.is_active ? "Activo" : "Inactivo"} ·{" "}
                {u.modules.filter((m) => m.enabled).length} módulos
              </p>
            </div>
            <button className="secondary" onClick={() => setSelected(u)}>
              Editar {u.full_name}
            </button>
          </div>
        ))}
      </Panel>
      <Panel title={selected ? "Editar apoderado" : "Crear apoderado"}>
        <Editor
          key={selected?.id ?? "new"}
          user={selected}
          changed={() => refresh((v) => v + 1)}
        />
      </Panel>
    </div>
  );
}
