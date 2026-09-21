import { apiFetch, apiDownload } from "./api";
import type { ListRow } from "./management.service";
export interface Filters {
  election_id: string;
  office_id: string;
  municipality_id: string;
  apoderado_id: string;
  status: string;
  search: string;
}
export const emptyFilters: Filters = {
  election_id: "",
  office_id: "",
  municipality_id: "",
  apoderado_id: "",
  status: "",
  search: "",
};
export function query(filters: Record<string, string | number | undefined>) {
  return new URLSearchParams(
    Object.entries(filters)
      .filter(([, v]) => v !== "" && v !== undefined)
      .map(([k, v]) => [k, String(v)]),
  ).toString();
}
export interface ReportList extends ListRow {
  election_name: string;
  office_name: string;
  municipality_name: string;
  created_at: string | null;
  submitted_at: string | null;
  apoderados: { id: number; name: string }[];
}
export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
export interface Summary {
  total_lists: number;
  total_candidates: number;
  approved_lists: number;
  sent_lists: number;
  incomplete_lists: number;
  rejected_lists: number;
  active_apoderados: number | null;
  approval_rate: number;
  approval_denominator: number;
  by_status: Record<string, number>;
  by_office: {
    office_id: number;
    office_name: string;
    lists: number;
    candidates: number;
  }[];
  recent_lists?: ReportList[];
  modules?: {
    id: number;
    election_name: string;
    office_name: string;
    municipality_name: string;
  }[];
}
export interface Composition {
  status: string;
  message: string;
  can_submit: boolean;
  issues: { code: string; message: string; positions: number[] }[];
  details: {
    required_positions: number | null;
    current_positions: number;
    female?: number;
    male?: number;
    other?: number;
    requires_alternation?: boolean;
    template_is_test?: boolean;
    groups_expected?: Record<string, number>;
    groups_actual?: Record<string, number>;
  };
}
export const stateLabels: Record<string, string> = {
  borrador: "Borrador",
  incompleta: "Incompleta",
  en_validacion: "En validación",
  rechazada_composicion: "Composición observada",
  enviada_admin: "Enviada al administrador",
  aprobada_sistema: "Aprobada por sistema",
};
export async function download(path: string) {
  const result = await apiDownload(path);
  const url = URL.createObjectURL(result.blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = result.filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function summary(filters: Filters) {
  return apiFetch<Summary>(
    `/admin/reports?${query(filters as unknown as Record<string, string>)}`,
  );
}
