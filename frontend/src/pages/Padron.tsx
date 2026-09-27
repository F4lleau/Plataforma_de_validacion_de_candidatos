import { useState } from "react";
import { Download, History, Loader2, Search, Upload } from "lucide-react";
import { Field, Feedback, PageHeading, Panel } from "../components/forms/FormUI";
import { ActionButton, Modal } from "../components/ui/ActionUI";
import { DataTable, type DataColumn } from "../components/ui/DataTable";
import { Pagination } from "../components/ui/Pagination";
import { useRemote } from "../hooks/useRemote";
import { importPadron } from "../services/padron.service";
import { download } from "../services/reporting.service";
import { formatDateTime } from "../utils/date";

interface Batch {
  id: number;
  file_name: string;
  status: string;
  valid_rows: number;
  invalid_rows: number;
  imported_at: string;
  notes: string;
  is_current: boolean;
}

interface PadronRow extends Record<string, string | number | null> {
  id: number;
}

interface PadronData {
  items: PadronRow[];
  total: number;
  page: number;
  page_size: number;
  sections: number;
  total_members: number;
  current_batch: Batch | null;
}

interface PadronCatalog {
  sections: {
    id: string;
    name: string;
    code: string | null;
  }[];
  circuits: {
    id: string;
    name: string;
    code: string | null;
    section: string | null;
    section_code: string | null;
  }[];
}

const pageSize = 10;
const numberFormat = new Intl.NumberFormat("es-AR");

const columns: DataColumn<PadronRow>[] = [
  { key: "section", label: "Sección" },
  { key: "section_code", label: "Cod. Sección" },
  { key: "circuit", label: "Circuito" },
  { key: "circuit_code", label: "Cod. Circuito" },
  { key: "last_name", label: "Apellido" },
  { key: "first_name", label: "Nombre" },
  { key: "gender", label: "Género" },
  { key: "document_type", label: "Tipo documento" },
  { key: "dni", label: "Matrícula" },
  { key: "birth_date", label: "Fecha nacimiento" },
  { key: "birth_class", label: "Clase" },
  { key: "elector_status", label: "Estado actual elector" },
  { key: "affiliation_status", label: "Estado afiliación" },
  { key: "affiliation_date", label: "Fecha afiliación" },
  { key: "illiterate", label: "Analfabeto" },
  { key: "profession", label: "Profesión" },
  { key: "address_date", label: "Fecha domicilio" },
  { key: "address", label: "Domicilio" },
];

export default function Padron() {
  const [revision, refresh] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    search: "",
    section_id: "",
    circuit_id: "",
  });
  const [query, setQuery] = useState("");
  const data = useRemote<PadronData>(
    `/padron?page=${page}&page_size=${pageSize}&${query}`,
    revision,
  );
  const catalog = useRemote<PadronCatalog>("/padron/catalog", revision);
  const batches = useRemote<Batch[]>("/padron/batches", revision);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [historyOpen, setHistoryOpen] = useState(false);

  function buildFilterParams() {
    const selectedCircuit = catalog.data?.circuits.find(
      (item) => item.id === filters.circuit_id,
    );
    const selectedSection = catalog.data?.sections.find(
      (item) => item.id === filters.section_id,
    );
    const params = new URLSearchParams();
    if (filters.search.trim()) params.set("search", filters.search.trim());
    if (selectedSection?.code) params.set("section_code", selectedSection.code);
    if (selectedSection && !selectedSection.code) {
      params.set("section", selectedSection.name);
    }
    if (selectedCircuit?.section_code) {
      params.set("section_code", selectedCircuit.section_code);
    }
    if (selectedCircuit?.code) params.set("circuit_code", selectedCircuit.code);
    if (selectedCircuit && !selectedCircuit.code) {
      params.set("circuit", selectedCircuit.name);
    }
    return params.toString();
  }

  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Afiliación partidaria"
        title="Padrón de afiliados"
        description="Importá el padrón y consultá los registros vigentes de afiliación."
      />

      <div className="grid gap-3 sm:grid-cols-3">
        {[
          ["Registros vigentes", numberFormat.format(data.data?.total_members ?? 0)],
          ["Secciones", numberFormat.format(data.data?.sections ?? 0)],
          [
            "Última actualización",
            data.data?.current_batch
              ? formatDateTime(data.data.current_batch.imported_at)
              : "Sin importación",
          ],
        ].map(([label, value]) => (
          <div className="rounded-lg border border-[#cfe1e7] bg-white p-4" key={label}>
            <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-[#5f8fa1]">
              {label}
            </p>
            <p className="mt-2 font-mono text-sm font-semibold text-[#00384a]">
              {value}
            </p>
          </div>
        ))}
      </div>

      <Panel
        title="Importar padrón"
        action={
          <ActionButton
            type="button"
            variant="secondary"
            onClick={() => setHistoryOpen(true)}
          >
            <History size={16} aria-hidden="true" />
            Historial
          </ActionButton>
        }
      >
        <form
          className="grid items-end gap-3 lg:grid-cols-[minmax(0,1fr)_auto]"
          onSubmit={async (e) => {
            e.preventDefault();
            if (!file) return;
            setBusy(true);
            setError("");
            setMessage("");
            try {
              const result = await importPadron(file);
              setMessage(
                `Importación ${result.status}: ${numberFormat.format(
                  result.valid_rows,
                )} válidas, ${numberFormat.format(
                  result.invalid_rows,
                )} inválidas. Revise el historial para ver los detalles.`,
              );
              refresh((value) => value + 1);
              setPage(1);
            } catch (err) {
              setError((err as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <label className="grid min-w-0 gap-2 text-xs font-medium text-muted-foreground">
            Archivo de padrón (máximo 20 MB)
            <span className="flex min-h-10 min-w-0 items-center gap-3 rounded-lg border border-input bg-card px-2 py-1.5">
              <span className="inline-flex min-h-8 shrink-0 cursor-pointer items-center rounded-full bg-[#00384a] px-4 py-2 font-mono text-[11px] font-semibold uppercase tracking-[0.08em] text-white">
                Seleccionar archivo
              </span>
              <span className="min-w-0 flex-1 truncate font-mono text-[11px] text-[#00384a]">
                {file?.name ?? "Ningún archivo seleccionado"}
              </span>
              <span className="hidden shrink-0 font-mono text-[10px] uppercase tracking-[0.08em] text-[#5f8fa1] md:inline">
                XLSX, XLSM, XLS, ODS, CSV, TSV, TXT
              </span>
              <input
                className="sr-only"
                type="file"
                required
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </span>
          </label>
          <ActionButton disabled={busy}>
            {busy ? (
              <Loader2 size={16} className="animate-spin" aria-hidden="true" />
            ) : (
              <Upload size={16} aria-hidden="true" />
            )}
            {busy ? "Importando..." : "Importar padrón"}
          </ActionButton>
          <Feedback error={error} message={message} />
        </form>
      </Panel>

      <Panel title="Consultar padrón vigente">
        <form
          className="grid gap-3 lg:grid-cols-[minmax(260px,1.4fr)_repeat(2,minmax(190px,1fr))_auto]"
          onSubmit={(e) => {
            e.preventDefault();
            setPage(1);
            setQuery(buildFilterParams());
          }}
        >
          <Field label="Nombre, apellido o DNI">
            <input
              className="field"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </Field>
          <Field label="Circuito">
            <select
              className="field"
              value={filters.circuit_id}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  circuit_id: e.target.value,
                  section_id: "",
                })
              }
            >
              <option value="">Todos</option>
              {catalog.data?.circuits.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                  {item.code ? ` · ${item.code}` : ""}
                  {item.section ? ` · ${item.section}` : ""}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Sección / departamento">
            <select
              className="field"
              value={filters.section_id}
              disabled={!!filters.circuit_id}
              onChange={(e) =>
                setFilters({ ...filters, section_id: e.target.value })
              }
            >
              <option value="">Todas</option>
              {catalog.data?.sections.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                  {item.code ? ` · ${item.code}` : ""}
                </option>
              ))}
            </select>
          </Field>
          <ActionButton className="self-end">
            <Search size={16} aria-hidden="true" />
            Buscar
          </ActionButton>
        </form>

        <div className="flex flex-wrap gap-3">
          {(["xlsx", "csv"] as const).map((format) => (
            <ActionButton
              key={format}
              type="button"
              variant="secondary"
              disabled={busy}
              onClick={async () => {
                setBusy(true);
                setError("");
                try {
                  await download(
                    `/admin/exports/padron?format=${format}&${query}`,
                  );
                } catch (err) {
                  setError((err as Error).message);
                } finally {
                  setBusy(false);
                }
              }}
            >
              <Download size={16} aria-hidden="true" />
              Exportar {format.toUpperCase()}
            </ActionButton>
          ))}
        </div>

        <Feedback error={data.error} />
        {data.loading && (
          <p className="font-mono text-xs uppercase tracking-[0.12em] text-[#5f8fa1]">
            Cargando...
          </p>
        )}

        <DataTable
          columns={columns}
          rows={data.data?.items ?? []}
          rowKey={(row) => row.id}
          emptyText="No hay resultados"
        />

        <Pagination
          page={page}
          pageSize={pageSize}
          total={data.data?.total ?? 0}
          onPageChange={setPage}
        />
      </Panel>

      {historyOpen && (
        <Modal title="Historial de importaciones" onClose={() => setHistoryOpen(false)}>
          <div className="max-h-[70vh] overflow-auto pr-1">
            <Feedback error={batches.error} />
            {batches.data?.map((batch) => (
              <article
                className="border-b border-[#d8e8ee] py-4 text-sm"
                key={batch.id}
              >
                <p className="font-mono text-xs font-semibold uppercase tracking-[0.1em] text-[#00384a]">
                  {batch.file_name} · {batch.status}
                  {batch.is_current ? " · Vigente" : ""}
                </p>
                <p className="mt-1 text-muted-foreground">
                  {numberFormat.format(batch.valid_rows)} válidas ·{" "}
                  {numberFormat.format(batch.invalid_rows)} inválidas ·{" "}
                  {formatDateTime(batch.imported_at)}
                </p>
                <p className="mt-1 text-muted-foreground">{batch.notes}</p>
              </article>
            ))}
            {batches.data?.length === 0 && (
              <p className="font-mono text-xs uppercase tracking-[0.12em] text-muted-foreground">
                No hay importaciones registradas.
              </p>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}
