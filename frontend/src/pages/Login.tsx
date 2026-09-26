import LegalAccess from "../components/legal/LegalAccess";
import { safeLoginDestination } from "../services/legal.service";
import Brand from "../components/layout/Brand";
import {
  Layers3,
  ClipboardCheck,
  ShieldCheck,
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
                <div className="grid gap-3 pt-1 sm:grid-cols-2">
                  <Link to="/recuperar-clave" className="login-pill-primary">
                    <LifeBuoy size={17} aria-hidden="true" />
                    Olvidé mi contraseña
                  </Link>
                  <button
                    type="button"
                    className="login-pill-secondary"
                    disabled={unlockLoading}
                    onClick={handleUnlockRequest}
                  >
                    <LockKeyhole size={17} aria-hidden="true" />
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
          <div className="mt-4">
            <LegalAccess key={user?.id ?? "public"} pending={pending} />
          </div>
          <p className="mt-7 border-t pt-5 text-center text-xs text-muted-foreground">
            Partido Justicialista · Distrito Chaco
          </p>
        </section>
      </div>
    </main>
  );
}
