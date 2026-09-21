import { useState } from "react";
import { Link } from "react-router-dom";
import { useRemote } from "../hooks/useRemote";
import { Feedback } from "../components/forms/FormUI";
import { Pager } from "../components/reporting/ReportUI";
import type { Page } from "../services/reporting.service";
interface Review {
  id: number;
  first_name: string;
  last_name: string;
  dni: string;
  status: string;
  lists: { id: number; name: string }[];
}
export default function CandidatosRevision() {
  const [page, setPage] = useState(1);
  const data = useRemote<Page<Review>>(`/admin/candidate-review?page=${page}`);
  return (
    <div className="space-y-6">
      <h1 className="font-heading text-3xl font-bold">
        Candidatos en revisión
      </h1>
      <p>
        Observaciones vigentes. Una advertencia conserva al candidato y permite
        continuar con la carga.
      </p>
      <Feedback error={data.error} />
      {data.loading && <p role="status">Cargando...</p>}
      {data.data?.items.length === 0 && (
        <p>No hay candidatos con observaciones.</p>
      )}
      {data.data?.items.map((c) => (
        <article className="space-y-2 rounded-lg border bg-card p-4" key={c.id}>
          <h2 className="font-semibold">
            {c.last_name}, {c.first_name}
          </h2>
          <p>
            DNI {c.dni} · {c.status.replaceAll("_", " ")}
          </p>
          {c.lists.length ? (
            c.lists.map((l) => (
              <Link
                className="mr-3 text-primary underline"
                key={l.id}
                to={`/listas/${l.id}#candidato-${c.id}`}
              >
                {l.name}
              </Link>
            ))
          ) : (
            <p className="text-sm">Registro histórico sin lista vinculada.</p>
          )}
          <Link
            className="block text-sm text-primary underline"
            to={`/auditoria?entity_type=candidates&entity_id=${c.id}`}
          >
            Historial del candidato
          </Link>
        </article>
      ))}
      {data.data && (
        <Pager page={page} total={data.data.total} onChange={setPage} />
      )}
    </div>
  );
}
