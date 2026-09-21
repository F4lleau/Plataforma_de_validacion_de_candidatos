import { useState } from "react";
import { useForm } from "react-hook-form";
import { Field, Feedback, Panel } from "../components/forms/FormUI";
import { useRemote } from "../hooks/useRemote";
import {
  type Invitation,
  invitationPost,
  invitationState,
  mailState,
} from "../services/invitation.service";

export default function InvitationsAdmin({
  revision,
  changed,
}: {
  revision: number;
  changed: () => void;
}) {
  const [offset, setOffset] = useState(0);
  const rows = useRemote<Invitation[]>(
    `/admin/invitations?offset=${offset}`,
    revision,
  );
  const [target, setTarget] = useState<{
    row: Invitation;
    action: "resend" | "cancel";
  } | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const form = useForm({ defaultValues: { password: "" } });
  return (
    <Panel title="Invitaciones">
      <p className="text-sm text-muted-foreground">
        Las invitaciones pendientes aún no son cuentas. Los enlaces vencen;
        reenviar reemplaza el enlace anterior.
      </p>
      <button className="secondary" onClick={changed}>
        Actualizar estado del correo
      </button>
      <Feedback error={error || rows.error} message={message} />
      {rows.loading ? (
        <p role="status">Cargando invitaciones…</p>
      ) : (
        !rows.data?.length && <p>No hay invitaciones en esta página.</p>
      )}
      {rows.data?.map((row) => (
        <div
          key={row.id}
          className="flex flex-wrap items-center justify-between gap-3 border-b py-4"
        >
          <div className="min-w-0 break-words">
            <p className="font-semibold">{row.email}</p>
            <p className="text-sm">
              {invitationState[row.state]} · {row.modules.length} módulos
            </p>
            <p className="text-sm">
              Vence: {new Date(row.expires_at + "Z").toLocaleString()}
            </p>
            <p className="text-sm text-muted-foreground">
              {row.mail_state
                ? mailState[row.mail_state]
                : "Sin envío registrado"}
            </p>
          </div>
          {(row.state === "pending" || row.state === "expired") && (
            <div className="flex flex-wrap gap-2">
              {(["resend", "cancel"] as const).map((action) => (
                <button
                  key={action}
                  className="secondary"
                  onClick={() => {
                    setTarget({ row, action });
                    setError("");
                    setMessage("");
                    form.reset();
                  }}
                >
                  {action === "resend" ? "Reenviar" : "Cancelar invitación"}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
      <div className="flex gap-2">
        <button
          className="secondary"
          disabled={!offset}
          onClick={() => setOffset((v) => v - 25)}
        >
          Anterior
        </button>
        <button
          className="secondary"
          disabled={(rows.data?.length ?? 0) < 25}
          onClick={() => setOffset((v) => v + 25)}
        >
          Siguiente
        </button>
      </div>
      {target && (
        <form
          className="space-y-3 rounded-lg border p-4"
          onSubmit={form.handleSubmit(async (v) => {
            setError("");
            setMessage("");
            try {
              await invitationPost("/auth/reauthenticate", {
                password: v.password,
              });
              await invitationPost(
                `/admin/invitations/${target.row.id}/${target.action}`,
                {},
              );
              setMessage(
                target.action === "resend"
                  ? "Nuevo enlace en cola. El anterior ya no sirve."
                  : "Invitación cancelada. El enlace ya no sirve.",
              );
              setTarget(null);
              form.reset();
              changed();
            } catch (e) {
              setError((e as Error).message);
            }
          })}
        >
          <p>
            {target.action === "resend"
              ? "Reenviar a"
              : "Cancelar invitación de"}{" "}
            {target.row.email}
          </p>
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
              Volver
            </button>
          </div>
        </form>
      )}
    </Panel>
  );
}
