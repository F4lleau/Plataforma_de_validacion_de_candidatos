import { PageHeading } from "../components/forms/FormUI";
import { useState } from "react";
import {
  ReportFilters,
  ListTable,
  Pager,
} from "../components/reporting/ReportUI";
import { Feedback, Panel } from "../components/forms/FormUI";
import { useRemote } from "../hooks/useRemote";
import {
  emptyFilters,
  query,
  download,
  type ReportList,
  type Page,
} from "../services/reporting.service";
export default function Validaciones() {
  const [filters, setFilters] = useState(emptyFilters);
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const qs = query({ ...filters });
  const data = useRemote<Page<ReportList>>(`/admin/lists?${qs}&page=${page}`);
  async function exportFile(format: string) {
    setBusy(true);
    try {
      await download(`/admin/exports/lists?${qs}&format=${format}`);
      setError("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Revisión administrativa"
        title="Listas cargadas y validaciones"
      />
      <p>
        Supervisión de todas las listas. Abrí el detalle para ver composición y
        controles por candidato.
      </p>
      <Panel title="Filtros">
        <ReportFilters
          value={filters}
          onChange={(v) => {
            setFilters(v);
            setPage(1);
          }}
        />
      </Panel>
      <div className="flex flex-wrap gap-3">
        <button
          className="secondary"
          disabled={busy}
          onClick={() => void exportFile("xlsx")}
        >
          Exportar Excel
        </button>
        <button
          className="secondary"
          disabled={busy}
          onClick={() => void exportFile("csv")}
        >
          Exportar CSV
        </button>
        {busy && <p role="status">Preparando descarga...</p>}
      </div>
      <Feedback error={error || data.error} />
      {data.loading ? (
        <p role="status">Cargando...</p>
      ) : (
        data.data && (
          <>
            <ListTable items={data.data.items} />
            <Pager page={page} total={data.data.total} onChange={setPage} />
          </>
        )
      )}
    </div>
  );
}
