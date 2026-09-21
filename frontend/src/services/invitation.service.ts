import { apiFetch } from "./api";
import type { Module } from "./management.service";
export interface Invitation {
  id: number;
  email: string;
  role: "apoderado";
  modules: Module[];
  state: "pending" | "expired" | "cancelled" | "accepted";
  expires_at: string;
  generation: number;
  mail_state: "pending" | "processing" | "sent" | "failed" | "cancelled" | null;
}
export const invitationState = {
  pending: "Pendiente de aceptación",
  expired: "Vencida",
  cancelled: "Cancelada",
  accepted: "Aceptada",
};
export const mailState = {
  pending: "Correo en cola",
  processing: "Enviando correo",
  sent: "Aceptado por SMTP; entrega no confirmada",
  failed: "Falló el envío",
  cancelled: "Envío cancelado",
};
export function invitationPost<T>(
  path: string,
  body: unknown,
  authenticated = true,
) {
  return apiFetch<T>(
    path,
    { method: "POST", body: JSON.stringify(body) },
    authenticated,
  );
}
