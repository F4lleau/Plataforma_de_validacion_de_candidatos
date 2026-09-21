import { useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import type { LegalDocument } from "../../services/legal.service";

export default function LegalModal({
  document: content,
  onClose,
}: {
  document: LegalDocument;
  onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const title = useId();
  useEffect(() => {
    const element = dialog.current!;
    const origin =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;
    const overflow = document.body.style.overflow;
    element.showModal();
    document.body.style.overflow = "hidden";
    return () => {
      element.close();
      document.body.style.overflow = overflow;
      origin?.focus();
    };
  }, []);
  return createPortal(
    <dialog
      ref={dialog}
      aria-labelledby={title}
      onKeyDown={(event) => {
        if (event.key !== "Tab") return;
        const buttons = event.currentTarget.querySelectorAll<HTMLButtonElement>(
          "button:not(:disabled)",
        );
        const first = buttons[0];
        const last = buttons[buttons.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      className="m-auto max-h-[85dvh] w-[calc(100%-2rem)] max-w-2xl overflow-y-auto rounded-2xl border bg-card p-6 text-foreground shadow-xl backdrop:bg-black/50 sm:p-8"
    >
      <div className="flex items-start justify-between gap-4">
        <h2 id={title} className="text-xl font-semibold">
          {content.title}
        </h2>
        <button
          type="button"
          autoFocus
          className="secondary shrink-0 !p-2"
          aria-label="Cerrar documento"
          onClick={onClose}
        >
          <X size={20} aria-hidden="true" />
        </button>
      </div>
      <p className="mt-2 text-xs text-muted-foreground">
        Versión {content.version} · Publicado el{" "}
        {content.published_on.split("-").reverse().join("/")}
      </p>
      <p className="my-6 rounded-lg border border-primary/20 bg-primary/5 p-4 text-sm">
        {content.notice}
      </p>
      <div className="space-y-4 text-sm leading-relaxed">
        {content.paragraphs.map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
      </div>
      <button type="button" className="secondary mt-7" onClick={onClose}>
        Cerrar
      </button>
    </dialog>,
    document.body,
  );
}
