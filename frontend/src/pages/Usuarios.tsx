import InvitationsAdmin from "./InvitationsAdmin";
import { Link } from "react-router-dom";
import { PageHeading } from "../components/forms/FormUI";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Field, Panel, Feedback } from "../components/forms/FormUI";
import { useRemote } from "../hooks/useRemote";
import {
  save,
  type Apoderado,
  type UnlockRequest,
  type Module,
  type Election,
  type Office,
  type Municipality,
  unlockUser,
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
          if (!user)
            await save("/auth/reauthenticate", { password: v.password });
          await save(
            user ? `/users/${user.id}` : "/admin/invitations",
            user
              ? {
                  username: v.username,
                  email: v.email,
                  full_name: v.full_name,
                  is_active: v.is_active,
                  modules,
                }
              : { email: v.email, modules },
            user ? "PUT" : "POST",
          );
          setError("");
          setMessage(
            user
              ? "Apoderado guardado. Los cambios de acceso son inmediatos."
              : "Invitación en cola. El destinatario completará sus datos y contraseña.",
          );
          f.setValue("password", "");
          changed();
        } catch (e) {
          setError((e as Error).message);
        }
      })}
    >
      <div className="grid gap-3 sm:grid-cols-2">
        {(user
          ? (["full_name", "username", "email"] as const)
          : (["email", "password"] as const)
        ).map((k) => (
          <Field
            key={k}
            label={
              {
                full_name: "Nombre completo",
                username: "Usuario",
                email: "Correo electrónico",
                password: "Tu contraseña de administrador",
              }[k]
            }
          >
            <input
              className="field"
              type={
                k === "password" ? "password" : k === "email" ? "email" : "text"
              }
              readOnly={!!user && k === "email"}
              autoComplete={k === "password" ? "current-password" : "off"}
              required
              maxLength={k === "password" ? 1024 : k === "username" ? 50 : 255}
              {...f.register(k)}
            />
          </Field>
        ))}
      </div>
      {user && (
        <label className="flex gap-2">
          <input type="checkbox" {...f.register("is_active")} />
          Cuenta activa
        </label>
      )}
      <p className="text-sm text-muted-foreground">
        {user
          ? "Desactivar retira el acceso y conserva las listas. Para recuperar acceso, enviá un enlace desde Seguridad de cuenta. El correo no se modifica desde esta pantalla."
          : "El destinatario recibirá un enlace de un solo uso. Elegirá su nombre y contraseña al aceptarlo. Asignar módulos no asigna listas automáticamente."}
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
        {user ? "Guardar apoderado" : "Enviar invitación"}
      </button>
    </form>
  );
}
function UnlockRequests({ revision, changed }: { revision: number; changed: () => void }) {
  const requests = useRemote<UnlockRequest[]>(
    "/admin/users/unlock-requests",
    revision,
  );
  const form = useForm({
    defaultValues: {
      password: "",
      reason: "Solicitud de desbloqueo iniciada por el usuario.",
    },
  });
  const [target, setTarget] = useState<UnlockRequest | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  return (
    <Panel title="Solicitudes de desbloqueo">
      <Feedback error={error || requests.error} message={message} />
      {requests.loading && <p role="status">Cargando solicitudes...</p>}
      {!requests.loading && !requests.data?.length && (
        <p className="text-sm text-muted-foreground">
          No hay solicitudes pendientes.
        </p>
      )}
      <div className="space-y-3">
        {requests.data?.map((request) => (
          <div
            key={request.id}
            className="flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-card p-4"
          >
            <div className="min-w-0">
              <p className="font-semibold">
                {request.user_full_name || request.email}
              </p>
              <p className="mt-1 text-sm text-muted-foreground">
                {request.email} ·{" "}
                {request.locked
                  ? `Bloqueado hasta ${new Date(
                      request.locked_until ?? "",
                    ).toLocaleString()}`
                  : `${request.failed_attempts} intentos fallidos`}
              </p>
              {request.note && (
                <p className="mt-2 text-sm text-muted-foreground">
                  {request.note}
                </p>
              )}
            </div>
            <button
              type="button"
              className="secondary"
              onClick={() => {
                setTarget(request);
                form.reset({
                  password: "",
                  reason: "Solicitud de desbloqueo iniciada por el usuario.",
                });
              }}
            >
              Revisar desbloqueo
            </button>
          </div>
        ))}
      </div>
      {target && (
        <form
          className="mt-4 max-w-xl space-y-3 rounded-lg border p-4"
          onSubmit={form.handleSubmit(async (values) => {
            setError("");
            setMessage("");
            try {
              await save("/auth/reauthenticate", {
                password: values.password,
              });
              await unlockUser(target.user_id, values.reason);
              setMessage("Usuario desbloqueado y solicitud resuelta.");
              setTarget(null);
              form.reset();
              changed();
            } catch (error) {
              setError((error as Error).message);
            }
          })}
        >
          <h3 className="font-semibold">
            Confirmar desbloqueo: {target.user_full_name || target.email}
          </h3>
          <Field label="Motivo del desbloqueo">
            <input
              className="field"
              minLength={5}
              maxLength={300}
              required
              {...form.register("reason")}
            />
          </Field>
          <Field label="Tu contraseña de administrador">
            <input
              className="field"
              type="password"
              autoComplete="current-password"
              required
              {...form.register("password")}
            />
          </Field>
          <div className="flex flex-wrap gap-2">
            <button className="action" disabled={form.formState.isSubmitting}>
              Confirmar desbloqueo
            </button>
            <button
              className="secondary"
              type="button"
              onClick={() => {
                setTarget(null);
                form.reset();
              }}
            >
              Cancelar
            </button>
          </div>
        </form>
      )}
    </Panel>
  );
}
export default function Usuarios() {
  const [revision, refresh] = useState(0);
  const data = useRemote<Apoderado[]>("/users/", revision);
  const [selected, setSelected] = useState<Apoderado>();
  const [tab, setTab] = useState<"accounts" | "invitations" | "unlock">(
    "accounts",
  );
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Administración"
        title="Gestión de usuarios"
        description="Administrá cuentas, apoderados, módulos habilitados y solicitudes de desbloqueo."
      />
      <Link className="secondary inline-flex" to="/seguridad">
        Bloqueos y recuperación de cuentas
      </Link>
      <Feedback error={data.error} />
      <div className="flex gap-2" aria-label="Vistas de apoderados">
        <button
          className={tab === "accounts" ? "action" : "secondary"}
          aria-pressed={tab === "accounts"}
          onClick={() => setTab("accounts")}
        >
          Cuentas
        </button>
        <button
          className={tab === "invitations" ? "action" : "secondary"}
          aria-pressed={tab === "invitations"}
          onClick={() => {
            setTab("invitations");
            setSelected(undefined);
          }}
        >
          Invitaciones
        </button>
        <button
          className={tab === "unlock" ? "action" : "secondary"}
          aria-pressed={tab === "unlock"}
          onClick={() => {
            setTab("unlock");
            setSelected(undefined);
          }}
        >
          Solicitudes de desbloqueo
        </button>
      </div>
      {tab === "accounts" ? (
        <Panel title="Cuentas">
          <button
            className="secondary"
            onClick={() => {
              setSelected(undefined);
              setTab("invitations");
            }}
          >
            Invitar apoderado
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
                  {u.email_verified_at
                    ? "Correo verificado"
                    : "Correo sin verificación histórica"}{" "}
                  · {u.modules.filter((m) => m.enabled).length} módulos
                </p>
              </div>
              <button className="secondary" onClick={() => setSelected(u)}>
                Editar {u.full_name}
              </button>
            </div>
          ))}
        </Panel>
      ) : tab === "invitations" ? (
        <InvitationsAdmin
          revision={revision}
          changed={() => refresh((v) => v + 1)}
        />
      ) : (
        <UnlockRequests
          revision={revision}
          changed={() => refresh((v) => v + 1)}
        />
      )}
      {(selected || tab === "invitations") && (
        <Panel title={selected ? "Editar apoderado" : "Invitar apoderado"}>
          <Editor
            key={selected?.id ?? "new"}
            user={selected}
            changed={() => refresh((v) => v + 1)}
          />
        </Panel>
      )}
    </div>
  );
}
