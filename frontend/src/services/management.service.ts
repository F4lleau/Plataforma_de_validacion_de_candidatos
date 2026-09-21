import { apiFetch } from "./api";
export interface Election {
  id: number;
  name: string;
  election_type: string;
  election_date: string;
  active: boolean;
  loading_opens: string | null;
  loading_closes: string | null;
}
export interface Office {
  id: number;
  code: string;
  name: string;
  scope_type: string;
  municipality_based: boolean;
  required_positions: number;
  requires_parity: boolean;
  requires_alternation: boolean;
  active: boolean;
}
export interface Municipality {
  id: number;
  name: string;
  active: boolean;
}
export interface Module {
  election_id: number;
  office_id: number;
  municipality_id: number | null;
  enabled: boolean;
}
export interface Apoderado {
  email_verified_at: string | null;
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  modules: Module[];
}
export interface Position {
  position: number;
  name: string;
  group: string;
}
export interface Rules {
  minimum_age: number;
  age_reference: "election_date" | "loading_closes" | "unconfirmed";
  required_positions: number;
  requires_parity: boolean;
  requires_alternation: boolean;
  requires_affiliation: boolean;
  requires_renaper: boolean;
  other_requirements_confirmed: boolean;
  template_is_test: boolean;
  positions: Position[];
}
export interface RuleVersion {
  id: number;
  office_id: number;
  version: number;
  enabled: boolean;
  rules: Rules;
}
export interface ListRow {
  id: number;
  election_id: number;
  office_id: number;
  municipality_id: number | null;
  list_name: string;
  list_number: string | null;
  status: string;
  candidate_count: number;
  assigned_user_ids: number[];
  rule_version_id: number | null;
}
export interface CandidateData {
  id: number;
  revision: number;
  candidate_status: string;
  position: number;
  person: {
    dni: string;
    first_name: string;
    last_name: string;
    birth_date: string;
    gender: "F" | "M" | "X";
    address: string | null;
    municipality_id: number | null;
  };
  history?: {
    id: number;
    type: string;
    status: string;
    message: string;
    revision: number | null;
    validated_at: string;
    current_revision: boolean;
  }[];
  validations: {
    type: string;
    status: string;
    message: string;
    validated_at: string;
    origin: string;
  }[];
}
export interface ListDetail extends ListRow {
  composition: import("./reporting.service").Composition;
  submitted_at: string | null;
  evaluations: {
    id: number;
    validated_at: string;
    status: string;
    message: string;
  }[];
  rule: RuleVersion | null;
  candidates: CandidateData[];
}
export function save<T>(path: string, body: unknown, method = "POST") {
  return apiFetch<T>(path, { method, body: JSON.stringify(body) });
}
export async function catalogs(signal?: AbortSignal) {
  const [elections, offices, municipalities] = await Promise.all([
    apiFetch<Election[]>("/elections/", { signal }),
    apiFetch<Office[]>("/offices/", { signal }),
    apiFetch<Municipality[]>("/municipalities/", { signal }),
  ]);
  return { elections, offices, municipalities };
}
