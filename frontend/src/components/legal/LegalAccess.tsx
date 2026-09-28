import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../../services/api";
import {
  getLegalDocuments,
  type LegalDocuments,
} from "../../services/legal.service";
import { useAuthStore } from "../../stores/auth.store";
import LegalModal from "./LegalModal";

export default function LegalAccess({
  pending = false,
  variant = "default",
}: {
  pending?: boolean;
  variant?: "default" | "footer" | "login";
}) {
  const [documents, setDocuments] = useState<LegalDocuments | null>(null);
  const [open, setOpen] = useState<keyof LegalDocuments | null>(null);
  const [checked, setChecked] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [loadError, setLoadError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const accept = useAuthStore((s) => s.acceptTerms);
  const logout = useAuthStore((s) => s.logout);
  const sync = useAuthStore((s) => s.syncProfile);
  useEffect(() => {
    let current = true;
    getLegalDocuments()
      .then((result) => {
        if (current) {
          setDocuments(result);
          setLoadError("");
        }
      })
      .catch(() => {
        if (current)
          setLoadError("No pudimos cargar los documentos. Intentá nuevamente.");
      });
    return () => {
      current = false;
    };
  }, [attempt]);
  const syncOnFocus = useCallback(() => {
    void sync().catch(() => {});
  }, [sync]);
  useEffect(() => {
    if (!pending) return;
    // A second tab/device can accept; always ask the server before granting access.
    window.addEventListener("focus", syncOnFocus);
    return () => window.removeEventListener("focus", syncOnFocus);
  }, [pending, syncOnFocus]);

  async function submit() {
    if (!documents || !checked || busy) return;
    setBusy(true);
    setError("");
    try {
      await accept(documents.terms);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "No se pudo guardar la aceptación.",
      );
      if (
        reason instanceof ApiError &&
        reason.code === "TERMS_DOCUMENT_CHANGED"
      ) {
        setChecked(false);
        setDocuments(null);
        setAttempt((value) => value + 1);
      }
    } finally {
      setBusy(false);
    }
  }
  const compact = variant === "footer" || variant === "login";
  const legalButtonClass =
    compact
      ? "inline-flex min-h-7 items-center rounded-full border border-[#9fc6d3] bg-white px-3 py-1 font-mono text-[10px] font-semibold uppercase tracking-[0.1em] text-[#00384a] shadow-sm transition-colors hover:border-[#5fa9c7] hover:bg-[#eaf6fa] disabled:opacity-50"
      : "text-primary underline disabled:opacity-50";
  return (
    <section aria-label="Términos y privacidad" className="space-y-3 text-sm">
      {pending && (
        <>
          <p role="status" className="font-medium">
            Antes de ingresar, aceptá los términos y condiciones.
          </p>
          <p className="text-xs text-muted-foreground">
            Tu identidad está verificada. Falta este paso para acceder a la
            plataforma.
          </p>
          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={checked}
              disabled={busy || !documents}
              onChange={(event) => setChecked(event.target.checked)}
              className="mt-1 size-4 accent-primary"
            />
            <span>He leído y acepto los términos y condiciones</span>
          </label>
        </>
      )}
      <div
        className={
          compact
            ? "flex flex-wrap items-center justify-center gap-2"
            : "flex flex-wrap gap-x-4 gap-y-2"
        }
      >
        <button
          type="button"
          disabled={!documents}
          className={legalButtonClass}
          onClick={() => setOpen("terms")}
        >
          {compact
            ? "Términos y condiciones"
            : "Ver términos y condiciones"}
        </button>
        {variant !== "login" && (
          <button
            type="button"
            disabled={!documents}
            className={legalButtonClass}
            onClick={() => setOpen("privacy")}
          >
            {variant === "footer"
              ? "Políticas de seguridad"
              : "Ver políticas de privacidad"}
          </button>
        )}
      </div>
      {!documents && !loadError && !compact && (
        <p role="status" className="text-xs text-muted-foreground">
          Cargando documentos...
        </p>
      )}
      {loadError && !compact && (
        <div role="alert">
          <p>{loadError}</p>
          <button
            type="button"
            className="text-primary underline"
            onClick={() => {
              setLoadError("");
              setAttempt((value) => value + 1);
            }}
          >
            Reintentar carga
          </button>
        </div>
      )}
      {error && (
        <p
          role="alert"
          className="rounded-md bg-destructive/10 p-3 text-destructive"
        >
          {error}
        </p>
      )}
      {pending && (
        <div className="space-y-3">
          <button
            type="button"
            className="action w-full"
            disabled={!checked || !documents || busy}
            onClick={() => void submit()}
          >
            {busy ? "Guardando aceptación..." : "Aceptar y continuar"}
          </button>
          <button
            type="button"
            disabled={busy}
            className="text-primary underline"
            onClick={() => {
              void logout().catch((reason: unknown) =>
                setError(
                  reason instanceof Error
                    ? reason.message
                    : "No pudimos confirmar el cierre de sesión.",
                ),
              );
            }}
          >
            Salir / usar otra cuenta
          </button>
        </div>
      )}
      {open && documents && (
        <LegalModal document={documents[open]} onClose={() => setOpen(null)} />
      )}
    </section>
  );
}
