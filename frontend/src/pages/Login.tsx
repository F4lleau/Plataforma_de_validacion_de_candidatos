import LegalAccess from "../components/legal/LegalAccess";
import { safeLoginDestination } from "../services/legal.service";
import Brand from "../components/layout/Brand";
import {
  Eye,
  EyeOff,
  LockKeyhole,
  LifeBuoy,
} from "lucide-react";
import { useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../stores/auth.store";
import { ApiError } from "../services/api";
import { requestUnlock } from "../services/auth.service";

export default function Login() {
  const location = useLocation();
  const { login, isAuthenticated, isLoading, user } = useAuthStore();
  const [email, setEmail] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [unlockLoading, setUnlockLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  if (isLoading)
    return (
      <p role="status" className="p-8 text-center">
        Verificando sesión...
      </p>
    );
  const destination = safeLoginDestination(
    (location.state as { from?: string } | null)?.from,
  );
  const pending = isAuthenticated && !user?.terms_accepted_at;
  if (isAuthenticated && !pending) return <Navigate to={destination} replace />;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (pending || loading) return;
    setLoading(true);
    setError("");
    setMessage("");
    try {
      await login(email, password);
      setPassword("");
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

  const handleUnlockRequest = async () => {
    if (!email.trim()) {
      setError("Ingresá tu correo electrónico para solicitar el desbloqueo.");
      return;
    }
    setUnlockLoading(true);
    setError("");
    setMessage("");
    try {
      const result = await requestUnlock(email);
      setMessage(result.message);
    } catch (error) {
      setError(
        error instanceof ApiError
          ? error.message
          : "No pudimos enviar la solicitud de desbloqueo.",
      );
    } finally {
      setUnlockLoading(false);
    }
  };

  return (
    <main className="login-background flex min-h-screen items-center justify-center px-5 py-6 md:px-10">
      <div className="grid w-full max-w-5xl items-center gap-10 lg:grid-cols-2 lg:gap-16">
        <div className="hidden lg:block">
          <Brand />
          <p className="eyebrow mb-4 mt-16">Plataforma de gestión electoral</p>
          <h2 className="text-5xl font-semibold leading-[1.1]">
            Gestión electoral
            <br />
            clara y segura.
          </h2>
          <p className="mt-6 max-w-sm text-base leading-relaxed text-muted-foreground">
            Un acceso único para administrar listas, validar candidatos y
            consultar el estado del proceso.
          </p>
        </div>
        <section className="surface mx-auto w-full max-w-md p-6 sm:p-8">
          <div className="mb-6 lg:hidden">
            <Brand />
          </div>
          <h1 className="mt-3 text-2xl font-semibold">
            Ingreso a la plataforma
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Accedé con tu correo y contraseña.
          </p>
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            {!pending && (
              <>
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
                  <span className="relative mt-2 block">
                    <input
                      type={showPassword ? "text" : "password"}
                      autoComplete="current-password"
                      required
                      value={password}
                      onChange={(event) => setPassword(event.target.value)}
                      className="field pr-12"
                    />
                    <button
                      type="button"
                      className="absolute right-2 top-1/2 inline-flex size-8 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                      aria-label={
                        showPassword
                          ? "Ocultar contraseña"
                          : "Mostrar contraseña"
                      }
                      aria-pressed={showPassword}
                      title={
                        showPassword
                          ? "Ocultar contraseña"
                          : "Mostrar contraseña"
                      }
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff size={18} aria-hidden="true" />
                      ) : (
                        <Eye size={18} aria-hidden="true" />
                      )}
                    </button>
                  </span>
                </label>
                <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
                  <Link
                    to="/recuperar-clave"
                    className="inline-flex min-h-8 items-center gap-2 rounded-full bg-[#030817] px-3 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-[0.08em] text-white shadow-sm transition-colors hover:bg-[#00384a]"
                  >
                    <LifeBuoy size={14} aria-hidden="true" />
                    Olvidé mi contraseña
                  </Link>
                  <button
                    type="button"
                    className="inline-flex min-h-8 items-center gap-2 rounded-full border border-[#9fc6d3] bg-white px-3 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-[0.08em] text-[#00384a] shadow-sm transition-colors hover:border-[#5fa9c7] hover:bg-[#eaf6fa] disabled:opacity-50"
                    disabled={unlockLoading}
                    onClick={handleUnlockRequest}
                  >
                    <LockKeyhole size={14} aria-hidden="true" />
                    {unlockLoading ? "Enviando..." : "Desbloquear usuario"}
                  </button>
                </div>
                {error && (
                  <p
                    role="alert"
                    className="rounded-md bg-destructive/10 p-3 text-sm text-destructive"
                  >
                    {error}
                  </p>
                )}
                {message && (
                  <p
                    role="status"
                    className="rounded-md bg-success/10 p-3 text-sm text-success"
                  >
                    {message}
                  </p>
                )}
              </>
            )}
            <button
              type="submit"
              disabled={loading || pending}
              className="action w-full"
            >
              {pending
                ? "Identidad verificada"
                : loading
                  ? "Ingresando..."
                  : "Ingresar"}
            </button>
          </form>
          <div className="mt-4 flex justify-center">
            <LegalAccess
              key={user?.id ?? "public"}
              pending={pending}
              variant={pending ? "default" : "login"}
            />
          </div>
        </section>
      </div>
    </main>
  );
}
