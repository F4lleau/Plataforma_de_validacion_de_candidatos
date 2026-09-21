import { apiFetch } from "./api";

export interface ListTemplate {
  id: number;
  name: string;
  group_name: string;
  position_order: number;
}

export interface ElectoralList {
  id: number;
  list_name: string;
  status: string;
  election_id: number;
  office_id: number;
  municipality_id: number | null;
}

export function getLists() {
  return apiFetch<ElectoralList[]>("/lists/");
}

export async function getListTemplate(officeType: string) {
  return apiFetch<ListTemplate[]>(`/list-templates/${officeType}`);
}

export async function validateList(listId: number, officeType: string) {
  return apiFetch(`/validations/list/${listId}?office_type=${officeType}`);
}
