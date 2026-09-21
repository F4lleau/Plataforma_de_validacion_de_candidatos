import { PageHeading } from "../components/forms/FormUI";
import { useState } from "react";
import { ReportFilters, Metrics } from "../components/reporting/ReportUI";
import { Feedback, Panel } from "../components/forms/FormUI";
import { useRemote } from "../hooks/useRemote";
import {
  emptyFilters,
  query,
  download,
  stateLabels,
  type Summary,
} from "../services/reporting.service";
export default function Reportes() {
  const [filters, setFilters] = useState(emptyFilters);
  const qs = query({ ...filters });
  const data = useRemote<Summary>(`/admin/reports?${qs}`);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function exportFile(format: string) {
    setBusy(true);
    try {
      await download(`/admin/exports/reports?${qs}&format=${format}`);
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
        eyebrow="Seguimiento"
        title="Reportes electorales"
        description="Explorá los indicadores y exportá la información del alcance seleccionado."
      />
      <Panel title="Filtros del reporte">
        <ReportFilters value={filters} onChange={setFilters} />
      </Panel>
      <div className="flex flex-wrap gap-3">
        <button
          className="secondary"
          disabled={busy}
          onClick={() => void exportFile("xlsx")}
        >
          Descargar Excel
        </button>
        <button
          className="secondary"
          disabled={busy}
          onClick={() => void exportFile("pdf")}
        >
          Descargar PDF
        </button>
        {busy && <p role="status">Preparando descarga...</p>}
      </div>
      <Feedback error={error || data.error} />
      {data.loading && <p role="status">Cargando...</p>}
      {data.data && (
        <>
          <Metrics data={data.data} />
          <p className="text-sm">
            Tasa = aprobadas / total de listas filtradas (
            {data.data.approval_denominator}). Los apoderados activos se cuentan
            dentro de las listas filtradas; sin filtros incluye todas las
            cuentas activas.
          </p>
          <div className="grid gap-6 lg:grid-cols-2">
            <Panel title="Distribución por estado">
              {Object.entries(stateLabels).map(([k, label]) => (
                <div key={k}>
                  <div className="flex justify-between text-sm">
                    <span>{label}</span>
                    <span>{data.data?.by_status[k] ?? 0}</span>
                  </div>
                  <div className="mt-1 h-3 rounded bg-muted">
                    <div
                      className="h-3 rounded bg-primary"
                      style={{
                        width: `${(100 * (data.data?.by_status[k] ?? 0)) / Math.max(data.data?.total_lists ?? 0, 1)}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </Panel>
            <Panel title="Listas y candidatos por cargo">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr>
                    <th>Cargo</th>
                    <th>Listas</th>
                    <th>Candidatos</th>
                  </tr>
                </thead>
                <tbody>
                  {data.data.by_office.map((o) => (
                    <tr key={o.office_id}>
                      <td className="py-3">{o.office_name}</td>
                      <td>
                        <span>{o.lists}</span>
                        <div
                          aria-hidden="true"
                          className="mt-1 h-2 rounded bg-primary"
                          style={{
                            width: `${(100 * o.lists) / Math.max(...data.data!.by_office.map((v) => v.lists), 1)}%`,
                          }}
                        />
                      </td>
                      <td>
                        <span>{o.candidates}</span>
                        <div
                          aria-hidden="true"
                          className="mt-1 h-2 rounded bg-secondary-foreground"
                          style={{
                            width: `${(100 * o.candidates) / Math.max(...data.data!.by_office.map((v) => v.candidates), 1)}%`,
                          }}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {data.data.total_lists === 0 && (
                <p>No hay datos para estos filtros.</p>
              )}
            </Panel>
          </div>
        </>
      )}
    </div>
  );
}
