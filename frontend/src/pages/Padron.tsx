import { PageHeading } from "../components/forms/FormUI";
import { download } from "../services/reporting.service";
import { useState } from "react";
import { importPadron } from "../services/padron.service";
import { useRemote } from "../hooks/useRemote";
import { Field, Panel, Feedback } from "../components/forms/FormUI";
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
interface PadronData {
  items: Record<string, string | number | null>[];
  total: number;
  page: number;
  page_size: number;
  sections: number;
  total_members: number;
  current_batch: Batch | null;
}
const columns = [
  ["section", "Sección"],
  ["section_code", "Cod. Sección"],
  ["circuit", "Circuito"],
  ["circuit_code", "Cod. Circuito"],
  ["last_name", "Apellido"],
  ["first_name", "Nombre"],
  ["gender", "Género"],
  ["document_type", "Tipo documento"],
  ["dni", "Matrícula"],
  ["birth_date", "Fecha nacimiento"],
  ["birth_class", "Clase"],
  ["elector_status", "Estado elector"],
  ["affiliation_status", "Estado afiliación"],
  ["affiliation_date", "Fecha afiliación"],
  ["illiterate", "Analfabeto"],
  ["profession", "Profesión"],
  ["address_date", "Fecha domicilio"],
  ["address", "Domicilio"],
];
export default function Padron() {
  const [revision, refresh] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    search: "",
    section: "",
    circuit: "",
    state: "",
  });
  const [query, setQuery] = useState("");
  const data = useRemote<PadronData>(`/padron?page=${page}&${query}`, revision);
  const batches = useRemote<Batch[]>("/padron/batches", revision);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Afiliación partidaria"
        title="Padrón de afiliados"
        description="Importá el padrón y consultá los registros vigentes de afiliación."
      />
      <div className="grid gap-3 sm:grid-cols-3">
        {[
          ["Registros vigentes", data.data?.total_members ?? 0],
          ["Secciones", data.data?.sections ?? 0],
          [
            "Última actualización",
            data.data?.current_batch
              ? new Date(
                  data.data.current_batch.imported_at + "Z",
                ).toLocaleString()
              : "Sin importación",
          ],
        ].map(([label, value]) => (
          <div className="rounded-lg border bg-card p-4" key={label}>
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className="mt-2 font-semibold">{value}</p>
          </div>
        ))}
      </div>
      <Panel title="Importar Excel">
        <form
          className="space-y-3"
          onSubmit={async (e) => {
            e.preventDefault();
            if (!file) return;
            setBusy(true);
            setError("");
            try {
              const result = await importPadron(file);
              setMessage(
                `Importación ${result.status}: ${result.valid_rows} válidas, ${result.invalid_rows} inválidas. Revise el historial para ver los detalles.`,
              );
              refresh((v) => v + 1);
              setPage(1);
            } catch (e) {
              setError((e as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <Field label="Archivo XLSX (máximo 20 MB)">
            <input
              className="field"
              type="file"
              accept=".xlsx"
              required
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </Field>
          <p className="text-sm text-muted-foreground">
            Matrícula se interpreta como documento. Se conserva compatibilidad
            con DNI, Nombre y Apellido. Si hay filas inválidas o duplicadas, el
            padrón vigente permanece sin cambios.
          </p>
          <button className="action" disabled={busy}>
            {busy ? "Importando..." : "Importar padrón"}
          </button>
          <Feedback error={error} message={message} />
        </form>
      </Panel>
      <Panel title="Consultar padrón vigente">
        <form
          className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5"
          onSubmit={(e) => {
            e.preventDefault();
            setPage(1);
            setQuery(new URLSearchParams(filters).toString());
          }}
        >
          {(["search", "section", "circuit", "state"] as const).map((k, i) => (
            <Field
              label={
                [
                  "Nombre, apellido o matrícula",
                  "Sección exacta",
                  "Circuito exacto",
                  "Estado afiliación exacto",
                ][i]
              }
              key={k}
            >
              <input
                className="field"
                value={filters[k]}
                onChange={(e) =>
                  setFilters({ ...filters, [k]: e.target.value })
                }
              />
            </Field>
          ))}
          <button className="secondary">Buscar</button>
        </form>
        <div className="flex flex-wrap gap-3">
          {(["xlsx", "csv"] as const).map((format) => (
            <button
              key={format}
              className="secondary"
              disabled={busy}
              onClick={async () => {
                setBusy(true);
                setError("");
                try {
                  await download(
                    `/admin/exports/padron?format=${format}&${query}`,
                  );
                } catch (e) {
                  setError((e as Error).message);
                } finally {
                  setBusy(false);
                }
              }}
            >
              Exportar {format.toUpperCase()}
            </button>
          ))}
        </div>
        <Feedback error={data.error} />
        {data.loading && <p role="status">Cargando...</p>}
        <div
          className="max-w-full overflow-x-auto"
          tabIndex={0}
          role="region"
          aria-label="Tabla del padrón"
        >
          <table className="w-full whitespace-nowrap text-left text-sm">
            <thead>
              <tr>
                {columns.map(([k, l]) => (
                  <th className="border-b p-3" key={k}>
                    {l}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.data?.items.map((row) => (
                <tr key={row.id}>
                  {columns.map(([k]) => (
                    <td className="border-b p-3" key={k}>
                      {row[k] ?? "—"}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {data.data?.total === 0 && <p>No hay resultados.</p>}
        <div className="flex flex-wrap items-center gap-3">
          <button
            className="secondary"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            Anterior
          </button>
          <span>
            Página {page} · {data.data?.total ?? 0} resultados
          </span>
          <button
            className="secondary"
            disabled={page * 25 >= (data.data?.total ?? 0)}
            onClick={() => setPage(page + 1)}
          >
            Siguiente
          </button>
        </div>
      </Panel>
      <Panel title="Historial de importaciones">
        <Feedback error={batches.error} />
        {batches.data?.map((b) => (
          <article className="border-b py-3 text-sm" key={b.id}>
            <p className="font-semibold">
              {b.file_name} · {b.status}
              {b.is_current ? " · Vigente" : ""}
            </p>
            <p>
              {b.valid_rows} válidas · {b.invalid_rows} inválidas ·{" "}
              {new Date(b.imported_at + "Z").toLocaleString()}
            </p>
            <p>{b.notes}</p>
          </article>
        ))}
      </Panel>
    </div>
  );
}
