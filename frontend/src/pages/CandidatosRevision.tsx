import { useEffect, useState } from "react";
import { apiFetch } from "../services/api";

interface CandidateReview {
  id: number;
  person_id: number;
  office_id: number;
  election_id: number;
  candidate_status: string;
  created_by: number;
  created_at: string;
}

export default function CandidatosRevision() {
  const [candidates, setCandidates] = useState<CandidateReview[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<CandidateReview[]>("/candidates/review")
      .then(setCandidates)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-3xl font-bold">
          Candidatos en revisión
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Casos con observaciones de afiliación pendientes de revisión
          administrativa.
        </p>
      </div>
      {loading ? (
        <p className="text-sm text-muted-foreground">
          Cargando observaciones...
        </p>
      ) : candidates.length === 0 ? (
        <p className="rounded-md border bg-card p-5 text-sm text-muted-foreground">
          No hay candidatos pendientes de revisión.
        </p>
      ) : (
        <div className="space-y-3">
          {candidates.map((candidate) => (
            <div key={candidate.id} className="rounded-lg border bg-card p-5">
              <p className="font-medium">Candidato #{candidate.id}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Persona #{candidate.person_id} · Estado:{" "}
                {candidate.candidate_status}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
