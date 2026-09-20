import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../stores/auth.store";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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
    } catch {
      setError("No pudimos validar tus credenciales.");
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
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-2 w-full rounded-md border px-3 py-2"
            />
          </label>
          <label className="block text-sm font-medium">
            Contraseña
            <input
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-2 w-full rounded-md border px-3 py-2"
            />
          </label>
          {error && (
            <p className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
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
