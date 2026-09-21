import { passwordLengthError } from "../services/password-policy";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import Brand from "../components/layout/Brand";
import { Feedback, Field } from "../components/forms/FormUI";
import { apiFetch, clearSession } from "../services/api";

import { captureLinkToken } from "../services/link-token";
const resetToken = captureLinkToken("/restablecer-clave");

export default function PasswordRecovery({
  reset = false,
}: {
  reset?: boolean;
}) {
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [done, setDone] = useState(false);
  const form = useForm({
    defaultValues: { email: "", password: "", confirmation: "" },
  });
  return (
    <main className="login-background min-h-screen px-5 py-12">
      <section className="surface mx-auto max-w-md space-y-6 p-7">
        <Brand />
        <h1 className="text-2xl font-semibold">
          {reset ? "Crear nueva contraseña" : "Recuperar acceso"}
        </h1>
        <p className="text-sm text-muted-foreground">
          {reset
            ? "Usá entre 15 y 128 caracteres. Podés incluir espacios y usar tu gestor de contraseñas."
            : "Ingresá tu correo y te enviaremos las instrucciones si tu cuenta permite recuperar el acceso."}
        </p>
        {reset && !resetToken ? (
          <Feedback error="El enlace no es válido. Solicitá uno nuevo." />
        ) : (
          !done && (
            <form
              className="space-y-4"
              onSubmit={form.handleSubmit(async (v) => {
                setError("");
                if (reset && passwordLengthError(v.password)) {
                  setError(passwordLengthError(v.password)!);
                  return;
                }
                if (reset && v.password !== v.confirmation) {
                  setError("Las contraseñas no coinciden.");
                  return;
                }
                try {
                  const result = await apiFetch<{ message: string }>(
                    reset ? "/auth/password/reset" : "/auth/password/forgot",
                    {
                      method: "POST",
                      body: JSON.stringify(
                        reset
                          ? { token: resetToken, new_password: v.password }
                          : { email: v.email },
                      ),
                    },
                    false,
                  );
                  setMessage(result.message);
                  setDone(true);
                  form.reset();
                  if (reset) clearSession();
                } catch (e) {
                  setError((e as Error).message);
                }
              })}
            >
              {!reset ? (
                <Field label="Correo electrónico">
                  <input
                    className="field"
                    type="email"
                    autoComplete="email"
                    required
                    {...form.register("email")}
                  />
                </Field>
              ) : (
                <>
                  <Field label="Nueva contraseña">
                    <input
                      className="field"
                      type="password"
                      autoComplete="new-password"
                      maxLength={256}
                      required
                      {...form.register("password")}
                    />
                  </Field>
                  <Field label="Repetir contraseña">
                    <input
                      className="field"
                      type="password"
                      autoComplete="new-password"
                      maxLength={256}
                      required
                      {...form.register("confirmation")}
                    />
                  </Field>
                </>
              )}
              <button
                className="action w-full"
                disabled={form.formState.isSubmitting}
              >
                {reset ? "Guardar contraseña" : "Enviar instrucciones"}
              </button>
            </form>
          )
        )}
        <Feedback error={error} message={message} />
        <div className="flex flex-wrap gap-4 text-sm text-primary underline">
          <Link to="/login">Volver al ingreso</Link>
          {reset && <Link to="/recuperar-clave">Solicitar otro enlace</Link>}
        </div>
      </section>
    </main>
  );
}
