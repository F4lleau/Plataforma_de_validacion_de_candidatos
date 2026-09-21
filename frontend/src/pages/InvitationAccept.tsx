import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import Brand from "../components/layout/Brand";
import { Field, Feedback } from "../components/forms/FormUI";
import { invitationPost } from "../services/invitation.service";
import { captureLinkToken } from "../services/link-token";
import { passwordLengthError } from "../services/password-policy";
import { useAuthStore } from "../stores/auth.store";
const invitationToken = captureLinkToken("/invitacion");

export default function InvitationAccept() {
  const [context, setContext] = useState<{
    email: string;
    expires_at: string;
  } | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(Boolean(invitationToken));
  const [done, setDone] = useState(false);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const form = useForm({
    defaultValues: {
      full_name: "",
      username: "",
      password: "",
      confirmation: "",
    },
  });
  useEffect(() => {
    if (!invitationToken) return;
    let active = true;
    invitationPost<{ email: string; expires_at: string }>(
      "/auth/invitations/inspect",
      { token: invitationToken },
      false,
    )
      .then((value) => {
        if (active) setContext(value);
      })
      .catch((e) => {
        if (active) setError((e as Error).message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);
  return (
    <main className="login-background min-h-screen px-5 py-12">
      <section className="surface mx-auto max-w-lg space-y-6 p-7">
        <Brand />
        <h1 className="text-2xl font-semibold">Aceptá tu invitación</h1>
        {loading && <p role="status">Verificando invitación…</p>}
        {!invitationToken && !done && (
          <Feedback error="Abrí el enlace de tu correo. Si venció o ya no está disponible, pedí otra invitación al administrador." />
        )}
        {user && (
          <div className="rounded-lg border p-3 text-sm">
            <p>
              Tenés una sesión abierta como {user.full_name}. Aceptar esta
              invitación no cambia esa sesión.
            </p>
            <Link className="underline" to="/dashboard">
              Volver a mi cuenta
            </Link>
          </div>
        )}
        {context && !done && (
          <>
            <p className="break-words text-sm">
              Crearás una cuenta de apoderado para{" "}
              <strong>{context.email}</strong>. Este correo no puede
              modificarse.
            </p>
            <form
              className="space-y-4"
              onSubmit={form.handleSubmit(async (v) => {
                setError("");
                const invalid = passwordLengthError(v.password);
                if (invalid || v.password !== v.confirmation) {
                  setError(invalid ?? "Las contraseñas no coinciden.");
                  return;
                }
                try {
                  await invitationPost(
                    "/auth/invitations/accept",
                    {
                      token: invitationToken,
                      full_name: v.full_name,
                      username: v.username,
                      password: v.password,
                    },
                    false,
                  );
                  form.reset();
                  setDone(true);
                } catch (e) {
                  setError((e as Error).message);
                }
              })}
            >
              <Field label="Nombre completo">
                <input
                  className="field"
                  autoComplete="name"
                  required
                  maxLength={255}
                  {...form.register("full_name")}
                />
              </Field>
              <Field label="Nombre de usuario">
                <input
                  className="field"
                  autoComplete="username"
                  required
                  minLength={3}
                  maxLength={50}
                  pattern="[A-Za-z0-9_.\-]+"
                  {...form.register("username")}
                />
                <span>
                  De 3 a 50 letras, números, puntos, guiones o guiones bajos.
                </span>
              </Field>
              <p className="text-sm text-muted-foreground">
                Contraseña de 15 a 128 caracteres. Podés usar espacios y tu
                gestor de contraseñas.
              </p>
              <Field label="Contraseña inicial">
                <input
                  className="field"
                  type="password"
                  autoComplete="new-password"
                  required
                  maxLength={256}
                  {...form.register("password")}
                />
              </Field>
              <Field label="Repetir contraseña">
                <input
                  className="field"
                  type="password"
                  autoComplete="new-password"
                  required
                  maxLength={256}
                  {...form.register("confirmation")}
                />
              </Field>
              <button
                className="action w-full"
                disabled={form.formState.isSubmitting}
              >
                {form.formState.isSubmitting
                  ? "Creando cuenta…"
                  : "Crear mi cuenta"}
              </button>
            </form>
          </>
        )}
        <Feedback
          error={error}
          message={
            done
              ? "Cuenta creada. Iniciá sesión con el correo de la invitación y tu contraseña."
              : ""
          }
        />
        {done && user ? (
          <button
            className="action"
            onClick={async () => {
              try {
                await logout();
                navigate("/login");
              } catch (e) {
                setError((e as Error).message);
              }
            }}
          >
            Cerrar sesión actual e ir al ingreso
          </button>
        ) : (
          <Link className="text-sm text-primary underline" to="/login">
            Ir al ingreso
          </Link>
        )}
      </section>
    </main>
  );
}
