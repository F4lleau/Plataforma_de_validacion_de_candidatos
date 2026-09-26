import { useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { BriefcaseBusiness, Edit3, MapPin, Plus, Trash2 } from "lucide-react";
import { Field, Feedback, PageHeading, Panel } from "../components/forms/FormUI";
import { ActionButton, BadgeLink, Modal } from "../components/ui/ActionUI";
import { useRemote } from "../hooks/useRemote";
import { apiFetch } from "../services/api";
import {
  save,
  type Election,
  type Municipality,
  type Office,
  type OfficeType,
} from "../services/management.service";

type Mode = "cargos" | "proceso" | "localidades";

const electionSchema = z
  .object({
    name: z.string().trim().min(1, "Ingresá un nombre."),
    loading_opens: z.string().min(1, "Indicá la apertura de carga."),
    loading_closes: z.string().min(1, "Indicá el cierre de carga."),
    election_date: z.string().min(1, "Indicá la fecha electoral estimada."),
    active: z.boolean(),
  })
  .refine(
    (value) =>
      value.loading_opens <= value.loading_closes &&
      value.loading_closes <= value.election_date,
    {
      message: "Las fechas deben respetar apertura, cierre y fecha electoral.",
      path: ["loading_closes"],
    },
  );
type ElectionForm = z.infer<typeof electionSchema>;

type OfficeForm = {
  name: string;
  election_id: number;
  office_type_id: number;
  scope_type: string;
  municipality_based: boolean;
  required_positions: number;
  requires_parity: boolean;
  requires_alternation: boolean;
  active: boolean;
};

function tableDate(value?: string | null) {
  return value
    ? new Date(`${value}T00:00:00`).toLocaleDateString()
    : "Sin definir";
}

function headerCopy(mode: Mode) {
  if (mode === "cargos")
    return {
      title: "Cargos",
      description: "Cargos habilitados para cada proceso electoral.",
      action: "Crear cargo",
    };
  if (mode === "localidades")
    return {
      title: "Localidades habilitadas",
      description: "Definí dónde se desarrolla cada proceso electoral.",
      action: "Habilitar localidad",
    };
  return {
    title: "Proceso electoral",
    description: "Fechas y estado de los procesos electorales internos.",
    action: "Crear elección",
  };
}

function ElectionModal({
  election,
  onClose,
  changed,
}: {
  election?: Election;
  onClose: () => void;
  changed: () => void;
}) {
  const form = useForm<ElectionForm>({
    resolver: zodResolver(electionSchema),
    defaultValues: {
      name: election?.name ?? "",
      loading_opens: election?.loading_opens ?? "",
      loading_closes: election?.loading_closes ?? "",
      election_date: election?.election_date ?? "",
      active: election?.active ?? true,
    },
  });
  const [error, setError] = useState("");
  return (
    <Modal title={election ? "Editar elección" : "Crear elección"} onClose={onClose}>
      <form
        className="space-y-4"
        onSubmit={form.handleSubmit(async (values) => {
          try {
            await save(
              `/elections/${election?.id ?? ""}`,
              { ...values, election_type: "interna" },
              election ? "PUT" : "POST",
            );
            changed();
            onClose();
          } catch (error) {
            setError((error as Error).message);
          }
        })}
      >
        <Feedback
          error={
            error ||
            Object.values(form.formState.errors)
              .map((item) => item.message)
              .filter(Boolean)
              .join(" ")
          }
        />
        <Field label="Nombre del proceso">
          <input className="field" {...form.register("name")} />
        </Field>
        <BadgeLink>Tipo interna</BadgeLink>
        <div className="grid gap-3 sm:grid-cols-3">
          <Field label="Apertura de carga">
            <input
              type="date"
              className="field"
              {...form.register("loading_opens")}
            />
          </Field>
          <Field label="Cierre de carga">
            <input
              type="date"
              className="field"
              {...form.register("loading_closes")}
            />
          </Field>
          <Field label="Fecha electoral estimada">
            <input
              type="date"
              className="field"
              {...form.register("election_date")}
            />
          </Field>
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" {...form.register("active")} />
          Proceso activo
        </label>
        <div className="flex justify-end gap-2">
          <ActionButton type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </ActionButton>
          <ActionButton disabled={form.formState.isSubmitting}>
            Guardar
          </ActionButton>
        </div>
      </form>
    </Modal>
  );
}

function OfficeModal({
  office,
  elections,
  officeTypes,
  onClose,
  changed,
}: {
  office?: Office;
  elections: Election[];
  officeTypes: OfficeType[];
  onClose: () => void;
  changed: () => void;
}) {
  const form = useForm<OfficeForm>({
    defaultValues: {
      name: office?.name ?? "",
      election_id: office?.election_ids?.[0] ?? elections[0]?.id ?? 0,
      office_type_id: office?.office_type_id ?? officeTypes[0]?.id ?? 0,
      scope_type: office?.scope_type ?? "provincial",
      municipality_based: office?.municipality_based ?? false,
      required_positions: office?.required_positions ?? 1,
      requires_parity: office?.requires_parity ?? true,
      requires_alternation: office?.requires_alternation ?? false,
      active: office?.active ?? true,
    },
  });
  const [error, setError] = useState("");
  return (
    <Modal title={office ? "Editar cargo" : "Crear cargo"} onClose={onClose}>
      <form
        className="space-y-4"
        onSubmit={form.handleSubmit(async (values) => {
          try {
            await save(
              `/offices/${office?.id ?? ""}`,
              values,
              office ? "PUT" : "POST",
            );
            changed();
            onClose();
          } catch (error) {
            setError((error as Error).message);
          }
        })}
      >
        <Feedback error={error} />
        <Field label="Proceso electoral">
          <select
            className="field"
            required
            {...form.register("election_id", { valueAsNumber: true })}
          >
            <option value="0">Seleccionar proceso</option>
            {elections.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </Field>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Nombre del cargo">
            <input className="field" required {...form.register("name")} />
          </Field>
          <Field label="Tipo de cargo">
            <select
              className="field"
              required
              {...form.register("office_type_id", { valueAsNumber: true })}
            >
              <option value="0">Seleccionar tipo</option>
              {officeTypes.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Ámbito">
            <select className="field" {...form.register("scope_type")}>
              <option value="provincial">Provincial</option>
              <option value="municipal">Municipal</option>
            </select>
          </Field>
          <Field label="Cantidad de lugares">
            <input
              className="field"
              type="number"
              min="1"
              max="200"
              {...form.register("required_positions", { valueAsNumber: true })}
            />
          </Field>
        </div>
        <div className="grid gap-2 text-sm sm:grid-cols-2">
          <label className="flex items-center gap-2">
            <input type="checkbox" {...form.register("municipality_based")} />
            Asociado a localidad
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" {...form.register("requires_parity")} />
            Requiere paridad
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" {...form.register("requires_alternation")} />
            Requiere alternancia
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" {...form.register("active")} />
            Cargo activo
          </label>
        </div>
        <div className="flex justify-end gap-2">
          <ActionButton type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </ActionButton>
          <ActionButton disabled={form.formState.isSubmitting}>
            Guardar
          </ActionButton>
        </div>
      </form>
    </Modal>
  );
}

function ProcessTable({
  elections,
  onEdit,
  changed,
}: {
  elections: Election[];
  onEdit: (election: Election) => void;
  changed: () => void;
}) {
  const [error, setError] = useState("");
  return (
    <Panel title="Procesos cargados">
      <Feedback error={error} />
      <table className="data-table">
        <thead>
          <tr>
            <th>Proceso</th>
            <th>Carga</th>
            <th>Fecha estimada</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {elections.map((item) => (
            <tr key={item.id}>
              <td className="font-medium">{item.name}</td>
              <td>
                {tableDate(item.loading_opens)} - {tableDate(item.loading_closes)}
              </td>
              <td>{tableDate(item.election_date)}</td>
              <td>
                <BadgeLink>{item.active ? "Activo" : "Inactivo"}</BadgeLink>
              </td>
              <td>
                <div className="flex flex-wrap gap-2">
                  <ActionButton
                    type="button"
                    variant="secondary"
                    onClick={() => onEdit(item)}
                  >
                    <Edit3 size={14} /> Editar
                  </ActionButton>
                  <ActionButton
                    type="button"
                    variant="ghost"
                    onClick={async () => {
                      if (!confirm("¿Desactivar este proceso electoral?")) return;
                      try {
                        await apiFetch(`/elections/${item.id}`, {
                          method: "DELETE",
                        });
                        changed();
                      } catch (error) {
                        setError((error as Error).message);
                      }
                    }}
                  >
                    <Trash2 size={14} /> Eliminar
                  </ActionButton>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  );
}

function OfficeTable({
  offices,
  elections,
  onEdit,
  changed,
}: {
  offices: Office[];
  elections: Election[];
  onEdit: (office: Office) => void;
  changed: () => void;
}) {
  const [error, setError] = useState("");
  const electionById = useMemo(
    () => Object.fromEntries(elections.map((item) => [item.id, item.name])),
    [elections],
  );
  return (
    <Panel title="Cargos cargados">
      <Feedback error={error} />
      <table className="data-table">
        <thead>
          <tr>
            <th>Cargo</th>
            <th>Tipo</th>
            <th>Proceso</th>
            <th>Lugares</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {offices.map((item) => (
            <tr key={item.id}>
              <td className="font-medium">{item.name}</td>
              <td>{item.office_type_name ?? "Sin tipo"}</td>
              <td>
                {item.election_ids?.length
                  ? item.election_ids.map((id) => electionById[id]).join(", ")
                  : "Sin proceso"}
              </td>
              <td>{item.required_positions}</td>
              <td>
                <BadgeLink>{item.active ? "Activo" : "Inactivo"}</BadgeLink>
              </td>
              <td>
                <div className="flex flex-wrap gap-2">
                  <ActionButton
                    type="button"
                    variant="secondary"
                    onClick={() => onEdit(item)}
                  >
                    <Edit3 size={14} /> Editar
                  </ActionButton>
                  <ActionButton
                    type="button"
                    variant="ghost"
                    onClick={async () => {
                      if (!confirm("¿Desactivar este cargo?")) return;
                      try {
                        await apiFetch(`/offices/${item.id}`, { method: "DELETE" });
                        changed();
                      } catch (error) {
                        setError((error as Error).message);
                      }
                    }}
                  >
                    <Trash2 size={14} /> Eliminar
                  </ActionButton>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  );
}

function MunicipalitiesPanel({
  elections,
  municipalities,
  revision,
  changed,
}: {
  elections: Election[];
  municipalities: Municipality[];
  revision: number;
  changed: () => void;
}) {
  const [electionId, setElectionId] = useState(elections[0]?.id ?? 0);
  const enabled = useRemote<Municipality[]>(
    electionId ? `/elections/${electionId}/municipalities` : "",
    revision + electionId,
  );
  const selected = new Set(enabled.data?.map((item) => item.id) ?? []);
  const [draft, setDraft] = useState<number[]>([]);
  const [error, setError] = useState("");
  const activeSelection = draft.length ? new Set(draft) : selected;
  return (
    <Panel title="Localidades por proceso">
      <Feedback error={error || enabled.error} />
      <div className="grid gap-3 md:grid-cols-[1fr_auto_auto]">
        <Field label="Proceso electoral">
          <select
            className="field"
            value={electionId}
            onChange={(event) => {
              setElectionId(Number(event.target.value));
              setDraft([]);
            }}
          >
            {elections.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </Field>
        <ActionButton
          type="button"
          variant="secondary"
          onClick={() => setDraft(municipalities.map((item) => item.id))}
        >
          Todas
        </ActionButton>
        <ActionButton type="button" variant="secondary" onClick={() => setDraft([])}>
          Limpiar selección
        </ActionButton>
      </div>
      <div className="grid max-h-80 gap-2 overflow-auto rounded-lg border p-3 sm:grid-cols-2 lg:grid-cols-3">
        {municipalities.map((item) => (
          <label
            key={item.id}
            className="flex items-center gap-2 rounded-md border bg-white px-3 py-2 text-sm"
          >
            <input
              type="checkbox"
              checked={activeSelection.has(item.id)}
              onChange={(event) => {
                const next = new Set(activeSelection);
                if (event.target.checked) next.add(item.id);
                else next.delete(item.id);
                setDraft([...next]);
              }}
            />
            {item.name}
          </label>
        ))}
      </div>
      <ActionButton
        type="button"
        disabled={!electionId}
        onClick={async () => {
          try {
            await apiFetch(`/elections/${electionId}/municipalities`, {
              method: "PUT",
              body: JSON.stringify({ municipality_ids: [...activeSelection] }),
            });
            setDraft([]);
            changed();
          } catch (error) {
            setError((error as Error).message);
          }
        }}
      >
        <MapPin size={15} /> Guardar localidades
      </ActionButton>
    </Panel>
  );
}

export default function Configuracion() {
  const location = useLocation();
  const mode: Mode = location.pathname.includes("localidades")
    ? "localidades"
    : location.pathname.includes("cargos")
      ? "cargos"
      : "proceso";
  const copy = headerCopy(mode);
  const [revision, refresh] = useState(0);
  const [modal, setModal] = useState<"election" | "office" | null>(null);
  const [selectedElection, setSelectedElection] = useState<Election>();
  const [selectedOffice, setSelectedOffice] = useState<Office>();
  const elections = useRemote<Election[]>("/elections/", revision);
  const offices = useRemote<Office[]>("/offices/", revision);
  const officeTypes = useRemote<OfficeType[]>("/offices/types", revision);
  const municipalities = useRemote<Municipality[]>("/municipalities/", revision);
  const changed = () => refresh((value) => value + 1);
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Configuración"
        title={copy.title}
        description={copy.description}
      >
        <ActionButton
          type="button"
          onClick={() => {
            if (mode === "cargos") {
              setSelectedOffice(undefined);
              setModal("office");
            } else if (mode === "proceso") {
              setSelectedElection(undefined);
              setModal("election");
            }
          }}
          disabled={mode === "localidades"}
        >
          {mode === "cargos" ? <BriefcaseBusiness size={15} /> : <Plus size={15} />}
          {copy.action}
        </ActionButton>
      </PageHeading>
      <Feedback
        error={
          elections.error ||
          offices.error ||
          officeTypes.error ||
          municipalities.error
        }
      />
      {mode === "proceso" && (
        <ProcessTable
          elections={elections.data ?? []}
          changed={changed}
          onEdit={(election) => {
            setSelectedElection(election);
            setModal("election");
          }}
        />
      )}
      {mode === "cargos" && (
        <OfficeTable
          offices={offices.data ?? []}
          elections={elections.data ?? []}
          changed={changed}
          onEdit={(office) => {
            setSelectedOffice(office);
            setModal("office");
          }}
        />
      )}
      {mode === "localidades" && (
        <MunicipalitiesPanel
          elections={elections.data ?? []}
          municipalities={municipalities.data ?? []}
          revision={revision}
          changed={changed}
        />
      )}
      {modal === "election" && (
        <ElectionModal
          election={selectedElection}
          changed={changed}
          onClose={() => setModal(null)}
        />
      )}
      {modal === "office" && (
        <OfficeModal
          office={selectedOffice}
          elections={elections.data ?? []}
          officeTypes={officeTypes.data ?? []}
          changed={changed}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  );
}
