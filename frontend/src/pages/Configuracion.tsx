import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Field, Panel, Feedback } from "../components/forms/FormUI";
import { useRemote } from "../hooks/useRemote";
import {
  save,
  type Election,
  type Office,
  type Municipality,
  type RuleVersion,
  type Rules,
} from "../services/management.service";

const electionSchema = z
  .object({
    name: z.string().trim().min(1),
    election_type: z.string().min(1),
    election_date: z.string().min(1),
    loading_opens: z.string().min(1),
    loading_closes: z.string().min(1),
    active: z.boolean(),
  })
  .refine(
    (v) =>
      v.loading_opens <= v.loading_closes &&
      v.loading_closes <= v.election_date,
    {
      message: "Apertura ≤ cierre ≤ fecha electoral",
      path: ["loading_closes"],
    },
  );
type ElectionForm = z.infer<typeof electionSchema>;
function ElectionEditor({
  election,
  changed,
}: {
  election?: Election;
  changed: () => void;
}) {
  const form = useForm<ElectionForm>({
    resolver: zodResolver(electionSchema),
    defaultValues: {
      name: election?.name ?? "",
      election_type: election?.election_type ?? "interna",
      election_date: election?.election_date ?? "",
      loading_opens: election?.loading_opens ?? "",
      loading_closes: election?.loading_closes ?? "",
      active: election?.active ?? true,
    },
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  return (
    <form
      className="space-y-4"
      onSubmit={form.handleSubmit(async (values) => {
        try {
          setError("");
          await save(
            `/elections/${election?.id ?? ""}`,
            values,
            election ? "PUT" : "POST",
          );
          setMessage("Elección guardada.");
          changed();
        } catch (e) {
          setError((e as Error).message);
        }
      })}
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Nombre">
          <input className="field" {...form.register("name")} />
        </Field>
        <Field label="Tipo">
          <input className="field" {...form.register("election_type")} />
        </Field>
        {(["election_date", "loading_opens", "loading_closes"] as const).map(
          (k, i) => (
            <Field
              key={k}
              label={
                ["Fecha electoral", "Apertura de carga", "Cierre de carga"][i]
              }
            >
              <input type="date" className="field" {...form.register(k)} />
            </Field>
          ),
        )}
      </div>
      <label className="flex gap-2">
        <input type="checkbox" {...form.register("active")} />
        Activa
      </label>
      <p className="text-sm text-muted-foreground">
        Fechas inclusivas, hora de Argentina. Pueden coexistir varias elecciones
        activas.
      </p>
      {Object.values(form.formState.errors).map((e, i) => (
        <p role="alert" key={i}>
          {e.message}
        </p>
      ))}
      <Feedback error={error} message={message} />
      <button className="action" disabled={form.formState.isSubmitting}>
        Guardar elección
      </button>
    </form>
  );
}
function OfficeEditor({
  office,
  changed,
}: {
  office?: Office;
  changed: () => void;
}) {
  const f = useForm<Omit<Office, "id">>({
    defaultValues: office ?? {
      code: "",
      name: "",
      scope_type: "provincial",
      municipality_based: false,
      required_positions: 24,
      requires_parity: true,
      requires_alternation: false,
      active: true,
    },
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  return (
    <form
      className="space-y-3"
      onSubmit={f.handleSubmit(async ({ ...v }) => {
        try {
          const { id: ignored, ...body } = v as Office;
          void ignored;
          await save(
            `/offices/${office?.id ?? ""}`,
            body,
            office ? "PUT" : "POST",
          );
          setError("");
          setMessage("Cargo guardado.");
          changed();
        } catch (e) {
          setError((e as Error).message);
        }
      })}
    >
      <div className="grid gap-3 sm:grid-cols-2">
        {(["code", "name", "scope_type"] as const).map((k, i) => (
          <Field
            key={k}
            label={["Código estable", "Nombre del cargo", "Ámbito"][i]}
          >
            <input
              className="field"
              required
              readOnly={k === "code" && !!office}
              {...f.register(k)}
            />
          </Field>
        ))}
        <Field label="Cantidad de posiciones">
          <input
            className="field"
            type="number"
            min="1"
            max="200"
            {...f.register("required_positions", { valueAsNumber: true })}
          />
        </Field>
      </div>
      {(
        [
          "municipality_based",
          "requires_parity",
          "requires_alternation",
          "active",
        ] as const
      ).map((k, i) => (
        <label key={k} className="flex gap-2">
          <input
            type="checkbox"
            disabled={k === "municipality_based" && !!office}
            {...f.register(k)}
          />
          {["Es municipal", "Paridad", "Alternancia", "Activo"][i]}
        </label>
      ))}
      <Feedback error={error} message={message} />
      <button className="action" disabled={f.formState.isSubmitting}>
        Guardar cargo
      </button>
    </form>
  );
}
function RulesEditor({
  electionId,
  office,
}: {
  electionId: number;
  office: Office;
}) {
  const [version, refresh] = useState(0);
  const remote = useRemote<RuleVersion[]>(
    `/elections/${electionId}/rules`,
    version,
  );
  const latest = remote.data?.filter((r) => r.office_id === office.id).at(-1);
  return (
    <>
      <Feedback error={remote.error} />
      <p className="text-sm">
        {latest
          ? `Versión actual: ${latest.version}. Las listas existentes conservan su versión.`
          : "Sin reglas configuradas para este cargo."}
      </p>
      <RulesForm
        key={`${office.id}-${latest?.id ?? "new"}`}
        electionId={electionId}
        office={office}
        latest={latest}
        changed={() => refresh((v) => v + 1)}
      />
    </>
  );
}
function RulesForm({
  electionId,
  office,
  latest,
  changed,
}: {
  electionId: number;
  office: Office;
  latest?: RuleVersion;
  changed: () => void;
}) {
  const f = useForm<Rules & { enabled: boolean }>({
    defaultValues: latest
      ? { ...latest.rules, enabled: latest.enabled }
      : {
          enabled: true,
          minimum_age: office.municipality_based ? 21 : 25,
          age_reference: "unconfirmed",
          required_positions: office.municipality_based ? 22 : 24,
          requires_parity: true,
          requires_alternation: office.municipality_based,
          requires_affiliation: true,
          requires_renaper: true,
          other_requirements_confirmed: false,
          template_is_test: true,
          positions: [],
        },
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [template, setTemplate] = useState(
    latest?.rules.positions.map((p) => `${p.group} | ${p.name}`).join("\n") ??
      "",
  );
  function demo() {
    const n = Number(f.getValues("required_positions"));
    setTemplate(
      Array.from({ length: n }, (_, i) =>
        office.municipality_based
          ? `prueba | Cargo de prueba ${i + 1}`
          : `${i < 16 ? "titulares" : "suplentes"} | Diputado de prueba ${i + 1}`,
      ).join("\n"),
    );
    f.setValue("template_is_test", true);
  }
  return (
    <form
      className="space-y-4"
      onSubmit={f.handleSubmit(async (v) => {
        try {
          const positions = template
            .trim()
            .split("\n")
            .filter(Boolean)
            .map((line, i) => {
              const [group, ...name] = line.split("|");
              return {
                position: i + 1,
                group: group.trim(),
                name: name.join("|").trim(),
              };
            });
          await save(`/elections/${electionId}/rules/${office.id}`, {
            ...v,
            positions,
          });
          setError("");
          setMessage("Nueva versión guardada.");
          changed();
        } catch (e) {
          setError((e as Error).message);
        }
      })}
    >
      <div className="grid gap-4 sm:grid-cols-3">
        <Field label="Edad mínima">
          <input
            className="field"
            type="number"
            min="18"
            max="100"
            {...f.register("minimum_age", { valueAsNumber: true })}
          />
        </Field>
        <Field label="Fecha de cómputo">
          <select className="field" {...f.register("age_reference")}>
            <option value="unconfirmed">Pendiente de confirmar</option>
            <option value="election_date">Día electoral</option>
            <option value="loading_closes">Cierre de carga</option>
          </select>
        </Field>
        <Field label="Posiciones requeridas">
          <input
            className="field"
            type="number"
            min="1"
            max="200"
            {...f.register("required_positions", { valueAsNumber: true })}
          />
        </Field>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {(
          [
            "enabled",
            "requires_parity",
            "requires_alternation",
            "requires_affiliation",
            "requires_renaper",
            "other_requirements_confirmed",
            "template_is_test",
          ] as const
        ).map((k, i) => (
          <label key={k} className="flex gap-2">
            <input type="checkbox" {...f.register(k)} />
            {
              [
                "Cargo habilitado",
                "Paridad 50/50",
                "Alternancia",
                "Afiliación requerida",
                "RENAPER requerido",
                "Otros requisitos confirmados",
                "Plantilla de prueba",
              ][i]
            }
          </label>
        ))}
      </div>
      <Field label="Plantilla ordenada (una línea por posición: grupo | denominación)">
        <textarea
          className="field min-h-48"
          value={template}
          onChange={(e) => setTemplate(e.target.value)}
        />
      </Field>
      <button className="secondary" type="button" onClick={demo}>
        Generar plantilla de prueba
      </button>
      <p className="text-sm text-muted-foreground">
        Los datos de prueba y requisitos pendientes no habilitan aprobación
        real.
      </p>
      <Feedback error={error} message={message} />
      <button className="action" disabled={f.formState.isSubmitting}>
        Guardar nueva versión de reglas
      </button>
    </form>
  );
}
function MunicipalityEditor({
  item,
  changed,
}: {
  item?: Municipality;
  changed: () => void;
}) {
  const f = useForm({
    defaultValues: { name: item?.name ?? "", active: item?.active ?? true },
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  return (
    <form
      className="flex flex-wrap items-end gap-3"
      onSubmit={f.handleSubmit(async (v) => {
        try {
          await save(
            `/municipalities/${item?.id ?? ""}`,
            v,
            item ? "PUT" : "POST",
          );
          setMessage("Localidad guardada.");
          setError("");
          changed();
        } catch (e) {
          setError((e as Error).message);
        }
      })}
    >
      <Field label="Localidad">
        <input className="field" required {...f.register("name")} />
      </Field>
      <label>
        <input type="checkbox" {...f.register("active")} /> Activa
      </label>
      <button className="action" disabled={f.formState.isSubmitting}>
        Guardar localidad
      </button>
      <Feedback error={error} message={message} />
    </form>
  );
}
export default function Configuracion() {
  const [revision, refresh] = useState(0);
  const elections = useRemote<Election[]>("/elections/", revision);
  const offices = useRemote<Office[]>("/offices/", revision);
  const municipalities = useRemote<Municipality[]>(
    "/municipalities/",
    revision,
  );
  const [electionId, setElection] = useState(0);
  const [officeId, setOffice] = useState(0);
  const [municipalityId, setMunicipality] = useState(0);
  const changed = () => refresh((v) => v + 1);
  const election = elections.data?.find((e) => e.id === electionId);
  const office = offices.data?.find((o) => o.id === officeId);
  return (
    <div className="space-y-6">
      <h1 className="font-heading text-3xl font-bold">
        Configuración electoral
      </h1>
      <Feedback
        error={elections.error || offices.error || municipalities.error}
      />
      <Panel title="Proceso electoral">
        <Field label="Elección">
          <select
            className="field"
            value={electionId}
            onChange={(e) => setElection(Number(e.target.value))}
          >
            <option value="0">Crear elección</option>
            {elections.data?.map((e) => (
              <option key={e.id} value={e.id}>
                {e.name}
              </option>
            ))}
          </select>
        </Field>
        <ElectionEditor
          key={electionId}
          election={election}
          changed={changed}
        />
      </Panel>
      <Panel title="Catálogo de cargos">
        <Field label="Cargo">
          <select
            className="field"
            value={officeId}
            onChange={(e) => setOffice(Number(e.target.value))}
          >
            <option value="0">Crear cargo</option>
            {offices.data?.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>
        </Field>
        <OfficeEditor key={officeId} office={office} changed={changed} />
      </Panel>
      {election && office && (
        <Panel title={`Reglas: ${election.name} / ${office.name}`}>
          <RulesEditor
            key={`${electionId}-${officeId}`}
            electionId={electionId}
            office={office}
          />
        </Panel>
      )}
      <Panel title="Localidades">
        <Field label="Localidad a editar">
          <select
            className="field"
            value={municipalityId}
            onChange={(e) => setMunicipality(Number(e.target.value))}
          >
            <option value="0">Crear localidad</option>
            {municipalities.data?.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </Field>
        <MunicipalityEditor
          key={municipalityId}
          item={municipalities.data?.find((m) => m.id === municipalityId)}
          changed={changed}
        />
      </Panel>
    </div>
  );
}
