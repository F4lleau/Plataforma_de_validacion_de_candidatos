import { apiUpload } from "./api";
export interface PadronImportResult { file_name: string; total_rows: number; valid_rows: number; invalid_rows: number; status: string; batch_id: number; }

export function importPadron(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return apiUpload<PadronImportResult>("/padron/import", formData);
}