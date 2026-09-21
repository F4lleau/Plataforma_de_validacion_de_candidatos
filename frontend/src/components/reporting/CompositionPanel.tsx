import { useState } from "react";
import { Field, Feedback, Panel } from "../forms/FormUI";
import { save } from "../../services/management.service";
import {
  stateLabels,
  type Composition,
} from "../../services/reporting.service";
export default function CompositionPanel({
  listId,
  state,
  composition,
  changed,
}: {
  listId: number;
  state: string;
  composition: Composition;
  changed: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [confirm, setConfirm] = useState(false);
  const editable = ["borrador", "incompleta", "rechazada_composicion"].includes(
    state,
  );
  async function act(action: "evaluate" | "submit") {
    setBusy(true);
    setError("");
    try {
      const result = await save<{
        state: string;
        submitted?: boolean;
        approval_blockers?: string[];
        composition: Composition;
      }>(`/lists/${listId}/${action}`, {});
      setMessage(
        action === "submit"
          ? result.submitted
            ? `Lista ${stateLabels[result.state]}. ${(result.approval_blockers?.length ?? 0) > 0 ? "Los controles pendientes requieren revisión." : ""}`
            : "No se envió: corregí los incumplimientos de composición."
          : "Composición evaluada y registrada.",
      );
      setConfirm(false);
      changed();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Panel title="Composición y envío">
      <p>
        {editable
          ? composition.message
          : "Composición consultada en modo lectura."}
      </p>
      <div className="grid gap-2 sm:grid-cols-3">
        <p>
          Cargados:{" "}
          <strong>
            {composition.details.current_positions}/
            {composition.details.required_positions ?? "sin plantilla"}
          </strong>
        </p>
        <p>
          Género: F {composition.details.female ?? 0} / M{" "}
          {composition.details.male ?? 0} / otros{" "}
          {composition.details.other ?? 0}
        </p>
        <p>
          Alternancia:{" "}
          {composition.details.requires_alternation
            ? "obligatoria"
            : "no aplica"}
        </p>
      </div>
      {composition.details.groups_expected && (
        <p className="text-sm">
          Grupos:{" "}
          {Object.entries(composition.details.groups_expected)
            .map(
              ([k, n]) =>
                `${k}: ${composition.details.groups_actual?.[k] ?? 0}/${n}`,
            )
            .join(" · ")}
        </p>
      )}
      {composition.issues.length > 0 && (
        <ul className="list-disc space-y-1 pl-5">
          {composition.issues.map((i, n) => (
            <li key={n}>
              {i.message}
              {i.positions.length > 0
                ? ` Posiciones: ${i.positions.join(", ")}.`
                : ""}
            </li>
          ))}
        </ul>
      )}
      <Feedback error={error} message={message} />
      {editable ? (
        <>
          <p className="text-sm">
            Para enviar, la composición debe estar completa. Afiliación
            observada o RENAPER pendiente permiten enviar para revisión, pero no
            aprobar. Después del envío la lista queda en lectura.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              className="secondary"
              disabled={busy}
              onClick={() => void act("evaluate")}
            >
              Validar composición
            </button>
            <button
              className="action"
              disabled={busy || !composition.can_submit}
              onClick={() => setConfirm(true)}
            >
              Enviar lista
            </button>
          </div>
          {confirm && (
            <div className="space-y-3 rounded-lg border p-4">
              <Field label="Confirmación de envío">
                <span>
                  La lista quedará en lectura. ¿Confirmás el envío
                  administrativo?
                </span>
              </Field>
              <button
                className="action mr-3"
                disabled={busy}
                onClick={() => void act("submit")}
              >
                Confirmar envío
              </button>
              <button
                className="secondary"
                disabled={busy}
                onClick={() => setConfirm(false)}
              >
                Cancelar
              </button>
            </div>
          )}
        </>
      ) : (
        <p className="text-sm">
          Lista en lectura: {stateLabels[state] ?? state}.{" "}
          {state === "aprobada_sistema"
            ? "La aprobación registrada corresponde a los controles evaluados al enviar."
            : "El envío no equivale a aprobación; consultá los controles pendientes."}
        </p>
      )}
      {busy && <p role="status">Procesando...</p>}
    </Panel>
  );
}
