import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../stores/auth.store";
import { ApiError } from "../services/api";

import { useRemote } from "../hooks/useRemote";

export default function Login() {
  const support = useRemote<{ contact: string }>("/auth/support");
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, isLoading } = useAuthStore();
  const [email, setEmail] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [help, setHelp] = useState(false);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (isLoading)
    return (
      <p role="status" className="p-8 text-center">
        Verificando sesión...
      </p>
    );
  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      const destination =
        (location.state as { from?: string } | null)?.from || "/dashboard";
      navigate(destination, { replace: true });
    } catch (error) {
      setError(
        error instanceof ApiError && error.status === 401
          ? "El correo o la contraseña no son correctos."
          : error instanceof ApiError
            ? error.message
            : "No pudimos iniciar sesión. Intentá nuevamente.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4 py-10">
      <section className="w-full max-w-md rounded-xl border bg-card p-8 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">
          Junta Electoral
        </p>
        <h1 className="mt-4 font-heading text-3xl font-bold">
          Ingresar a la plataforma
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Accedé a la gestión de listas y candidatos.
        </p>
        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <label className="block text-sm font-medium">
            Correo electrónico
            <input
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-2 w-full rounded-md border px-3 py-2"
            />
          </label>
          <label className="block text-sm font-medium">
            Contraseña
            <input
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-2 w-full rounded-md border px-3 py-2"
            />
          </label>
          <button
            type="button"
            className="text-sm text-primary underline"
            aria-pressed={showPassword}
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
          </button>
          <button
            type="button"
            className="block text-sm text-primary underline"
            onClick={() => setHelp(!help)}
          >
            Olvidé mi contraseña
          </button>
          {help && (
            <p role="status" className="rounded-md bg-muted p-3 text-sm">
              Solicitá el restablecimiento al administrador de la Junta por tu
              canal habitual. El administrador puede asignarte una nueva
              contraseña desde Gestión de apoderados, luego de verificar tu
              identidad. No se envían correos automáticos.{" "}
              {support.data?.contact && `Contacto: ${support.data.contact}`}
            </p>
          )}
          {error && (
            <p
              role="alert"
              className="rounded-md bg-destructive/10 p-3 text-sm text-destructive"
            >
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground disabled:opacity-60"
          >
            {loading ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
      </section>
    </main>
  );
}
