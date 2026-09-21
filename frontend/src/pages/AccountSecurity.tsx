import { passwordLengthError } from "../services/password-policy";
import { useState } from "react";
import { useForm } from "react-hook-form";
import {
  Field,
  Feedback,
  Panel,
  PageHeading,
} from "../components/forms/FormUI";
import { useRemote } from "../hooks/useRemote";
import { apiFetch, clearSession } from "../services/api";
import { useAuthStore } from "../stores/auth.store";

type Session = {
  id: string;
  current: boolean;
  created_at: string;
  last_used_at: string;
  expires_at: string;
};
type Account = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  locked: boolean;
  locked_until: string | null;
  failed_attempts: number;
};
const post = <T,>(url: string, body: unknown = {}) =>
  apiFetch<T>(url, { method: "POST", body: JSON.stringify(body) });
const date = (value: string) => new Date(value + "Z").toLocaleString();

function AdminLocks() {
  const [revision, refresh] = useState(0);
  const [lockedOnly, setLockedOnly] = useState(true);
  const [offset, setOffset] = useState(0);
  const [target, setTarget] = useState<Account | null>(null);
  const [action, setAction] = useState<"unlock" | "password-recovery">(
    "unlock",
  );
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const form = useForm({ defaultValues: { password: "", reason: "" } });
  const accounts = useRemote<Account[]>(
    `/admin/users/locks?locked_only=${lockedOnly}&offset=${offset}`,
    revision,
  );
  return (
    <Panel title="Seguridad de cuentas · Administración">
      <label className="flex gap-2">
        <input
          type="checkbox"
          checked={lockedOnly}
          onChange={(e) => {
            setLockedOnly(e.target.checked);
            setOffset(0);
          }}
        />{" "}
        Solo bloqueadas
      </label>
      <Feedback error={accounts.error || error} message={message} />
      {accounts.loading ? (
        <p role="status">Cargando cuentas...</p>
      ) : (
        !accounts.data?.length && (
          <p className="py-4 text-muted-foreground">
            No hay cuentas para este filtro.
          </p>
        )
      )}
      {accounts.data?.map((a) => (
        <div
          key={a.id}
          className="flex flex-wrap items-center justify-between gap-3 border-b py-4"
        >
          <div>
            <p className="font-semibold">
              {a.full_name} · {a.role}
            </p>
            <p className="text-sm">
              {a.email} ·{" "}
              {!a.is_active
                ? "Desactivada"
                : a.locked
                  ? "Bloqueada temporalmente"
                  : "Activa"}
            </p>
            {a.locked && a.locked_until && (
              <p className="text-sm">
                Reintentos: {a.failed_attempts}. Hasta {date(a.locked_until)}.
              </p>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {(a.locked || a.failed_attempts > 0) && (
              <button
                className="secondary"
                onClick={() => {
                  setTarget(a);
                  setAction("unlock");
                  form.reset();
                }}
              >
                Desbloquear
              </button>
            )}
            <button
              className="secondary"
              disabled={!a.is_active}
              onClick={() => {
                setTarget(a);
                setAction("password-recovery");
                form.reset();
              }}
            >
              Enviar recuperación
            </button>
          </div>
        </div>
      ))}
      <div className="mt-3 flex gap-2">
        <button
          className="secondary"
          disabled={!offset}
          onClick={() => setOffset((v) => v - 25)}
        >
          Anterior
        </button>
        <button
          className="secondary"
          disabled={(accounts.data?.length ?? 0) < 25}
          onClick={() => setOffset((v) => v + 25)}
        >
          Siguiente
        </button>
      </div>
      {target && (
        <form
          className="mt-5 space-y-3 rounded-lg border p-4"
          onSubmit={form.handleSubmit(async (v) => {
            setError("");
            setMessage("");
            try {
              await post("/auth/reauthenticate", { password: v.password });
              const result = await post<{ message: string }>(
                `/admin/users/${target.id}/${action}`,
                action === "unlock" ? { reason: v.reason } : {},
              );
              setMessage(result.message);
              setTarget(null);
              form.reset();
              refresh((v) => v + 1);
            } catch (e) {
              setError((e as Error).message);
            }
          })}
        >
          <h3 className="font-semibold">
            Confirmar {action === "unlock" ? "desbloqueo" : "recuperación"}:{" "}
            {target.full_name}
          </h3>
          {action === "unlock" && (
            <Field label="Motivo del desbloqueo">
              <input
                className="field"
                minLength={5}
                maxLength={300}
                required
                {...form.register("reason")}
              />
            </Field>
          )}
          <Field label="Tu contraseña de administrador">
            <input
              className="field"
              type="password"
              autoComplete="current-password"
              required
              {...form.register("password")}
            />
          </Field>
          <div className="flex gap-2">
            <button className="action" disabled={form.formState.isSubmitting}>
              Confirmar
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

export default function AccountSecurity() {
  const user = useAuthStore((s) => s.user);
  const [revision, refresh] = useState(0);
  const sessions = useRemote<Session[]>("/auth/sessions", revision);
  const [error, setError] = useState("");
  const [all, setAll] = useState(false);
  const form = useForm({
    defaultValues: { password: "", new_password: "", confirmation: "" },
  });
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Mi cuenta"
        title="Seguridad de acceso"
        description="Administrá tu contraseña y las sesiones abiertas."
      />
      <Feedback error={error || sessions.error} />
      <Panel title="Mi perfil">
        <p>
          {user?.full_name} · {user?.username}
        </p>
        <p className="break-words">
          {user?.email} · {user?.role}
        </p>
        <p className="text-sm text-muted-foreground">
          {user?.email_verified_at
            ? "Correo verificado al aceptar la invitación."
            : "Cuenta existente sin verificación histórica de correo registrada."}
        </p>
        {user?.role === "admin" && (
          <a className="text-sm underline" href="/usuarios">
            Gestionar cuentas e invitaciones pendientes
          </a>
        )}
      </Panel>
      <Panel title="Sesiones abiertas">
        {sessions.loading && <p role="status">Cargando sesiones...</p>}
        {sessions.data?.map((s) => (
          <div
            key={s.id}
            className="flex flex-wrap items-center justify-between gap-3 border-b py-4"
          >
            <div>
              <p className="font-semibold">
                {s.current ? "Esta sesión" : "Otra sesión"}
              </p>
              <p className="text-sm">
                Inicio: {date(s.created_at)} · Actividad: {date(s.last_used_at)}
              </p>
            </div>
            <button
              className="secondary"
              onClick={async () => {
                try {
                  await apiFetch(`/auth/sessions/${s.id}`, {
                    method: "DELETE",
                  });
                  if (s.current) clearSession();
                  else refresh((v) => v + 1);
                } catch (e) {
                  setError((e as Error).message);
                }
              }}
            >
              Cerrar sesión
            </button>
          </div>
        ))}
        <button
          className="secondary mt-4"
          onClick={() => {
            setAll(true);
            form.reset();
          }}
        >
          Cerrar todas las sesiones
        </button>
      </Panel>
      <Panel
        title={
          all ? "Confirmar cierre de todas las sesiones" : "Cambiar contraseña"
        }
      >
        <form
          className="max-w-lg space-y-4"
          onSubmit={form.handleSubmit(async (v) => {
            setError("");
            if (!all && passwordLengthError(v.new_password)) {
              setError(passwordLengthError(v.new_password)!);
              return;
            }
            if (!all && v.new_password !== v.confirmation) {
              setError("Las contraseñas no coinciden.");
              return;
            }
            try {
              if (all) {
                await post("/auth/reauthenticate", { password: v.password });
                await post("/auth/logout-all");
              } else
                await post("/auth/password/change", {
                  password: v.password,
                  new_password: v.new_password,
                });
              form.reset();
              clearSession();
            } catch (e) {
              setError((e as Error).message);
            }
          })}
        >
          <p className="text-sm text-muted-foreground">
            Se cerrarán todas tus sesiones. Deberás ingresar nuevamente.
          </p>
          <Field label="Contraseña actual">
            <input
              className="field"
              type="password"
              autoComplete="current-password"
              required
              {...form.register("password")}
            />
          </Field>
          {!all && (
            <>
              <Field label="Nueva contraseña (15 a 128 caracteres)">
                <input
                  className="field"
                  type="password"
                  autoComplete="new-password"
                  required
                  maxLength={256}
                  {...form.register("new_password")}
                />
              </Field>
              <Field label="Repetir nueva contraseña">
                <input
                  className="field"
                  type="password"
                  autoComplete="new-password"
                  required
                  {...form.register("confirmation")}
                />
              </Field>
            </>
          )}
          <button className="action" disabled={form.formState.isSubmitting}>
            {all ? "Confirmar cierre" : "Actualizar contraseña"}
          </button>
          {all && (
            <button
              className="secondary ml-3"
              type="button"
              onClick={() => {
                setAll(false);
                form.reset();
              }}
            >
              Cancelar
            </button>
          )}
        </form>
      </Panel>
      {user?.role === "admin" && <AdminLocks />}
    </div>
  );
}
