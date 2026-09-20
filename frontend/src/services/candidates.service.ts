import { apiFetch } from "./api";

export interface CandidatePersonPayload {
  dni: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  gender: string;
  address?: string;
  municipality_id?: number;
}

export interface CandidateCreatePayload {
  person: CandidatePersonPayload;
  office_id: number;
  election_id: number;
}

export interface CandidateResponse {
  id: number;
  person_id: number;
  office_id: number;
  election_id: number;
  candidate_status: string;
  created_by: number;
  created_at: string;
}

export interface AffiliationValidationResponse {
  status: "verified" | "warning";
  code?: string;
  message: string;
  requires_admin_review: boolean;
  details: Record<string, unknown>;
}

export interface CandidateCreateResponse {
  candidate: CandidateResponse;
  affiliation: AffiliationValidationResponse;
}

export function createCandidate(
  payload: CandidateCreatePayload
): Promise<CandidateCreateResponse> {
  return apiFetch<CandidateCreateResponse>("/candidates", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}