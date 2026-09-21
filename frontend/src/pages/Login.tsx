import Brand from "../components/layout/Brand";
import { Layers3, ClipboardCheck, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../stores/auth.store";
import { ApiError } from "../services/api";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, isLoading } = useAuthStore();
  const [email, setEmail] = useState("");
  const [showPassword, setShowPassword] = useState(false);
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
    <main className="login-background flex min-h-screen items-center justify-center px-5 py-10 md:px-10">
      <div className="grid w-full max-w-5xl items-center gap-12 lg:grid-cols-2 lg:gap-20">
        <div className="hidden lg:block">
          <Brand />
          <p className="eyebrow mb-5 mt-20">Plataforma de gestión electoral</p>
          <h2 className="text-5xl font-semibold leading-[1.12]">
            Cada lista.
            <br />
            Cada candidato.
            <br />
            <span className="text-primary">Todo en su lugar.</span>
          </h2>
          <p className="mt-6 max-w-sm text-base leading-relaxed text-muted-foreground">
            Un espacio para organizar las listas, consultar validaciones y
            acompañar cada etapa del proceso electoral.
          </p>
          <div className="mt-10 space-y-4 border-t pt-6">
            {[
              { icon: Layers3, text: "Listas y candidatos organizados" },
              {
                icon: ClipboardCheck,
                text: "Validaciones y observaciones claras",
              },
              { icon: ShieldCheck, text: "Acceso según tu rol y asignaciones" },
            ].map(({ icon: Icon, text }) => (
              <p
                key={text}
                className="flex items-center gap-3 text-sm text-muted-foreground"
              >
                <Icon size={17} className="text-primary" aria-hidden="true" />
                {text}
              </p>
            ))}
          </div>
        </div>
        <section className="surface mx-auto w-full max-w-md p-6 sm:p-9">
          <div className="mb-8 lg:hidden">
            <Brand />
          </div>
          <p className="eyebrow">Acceso a la plataforma</p>
          <h1 className="mt-3 text-2xl font-semibold">
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
                className="field mt-2"
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
                className="field mt-2"
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
            <Link
              to="/recuperar-clave"
              className="block text-sm text-primary underline"
            >
              Olvidé mi contraseña
            </Link>
            {error && (
              <p
                role="alert"
                className="rounded-md bg-destructive/10 p-3 text-sm text-destructive"
              >
                {error}
              </p>
            )}
            <button type="submit" disabled={loading} className="action w-full">
              {loading ? "Ingresando..." : "Ingresar"}
            </button>
          </form>
          <p className="mt-7 border-t pt-5 text-center text-xs text-muted-foreground">
            Partido Justicialista · Distrito Chaco
          </p>
        </section>
      </div>
    </main>
  );
}
