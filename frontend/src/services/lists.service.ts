import { apiFetch } from "./api";

export async function getListTemplate(officeType: string) {
  return apiFetch(`/list-templates/${officeType}`);
}

export async function validateList(listId: number, officeType: string) {
  return apiFetch(`/validations/list/${listId}?office_type=${officeType}`);
}