import { apiUpload } from "./api";
import type { PadronImportResult } from "../pages/Padron";

export function importPadron(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return apiUpload<PadronImportResult>("/padron/import", formData);
}