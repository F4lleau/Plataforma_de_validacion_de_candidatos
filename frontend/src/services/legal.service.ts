import { apiFetch } from "./api";
import type { AuthUser } from "./auth.service";

export interface LegalDocument {
  id: "terms" | "privacy";
  title: string;
  version: string;
  published_on: string;
  notice: string;
  paragraphs: string[];
  sha256: string;
}
export interface LegalDocuments {
  terms: LegalDocument;
  privacy: LegalDocument;
}
export const getLegalDocuments = () =>
  apiFetch<LegalDocuments>("/legal/documents", {}, false);
export const acceptTerms = (document: LegalDocument) =>
  apiFetch<AuthUser>("/auth/terms/accept", {
    method: "POST",
    body: JSON.stringify({
      accepted: true,
      version: document.version,
      sha256: document.sha256,
    }),
  });

export function safeLoginDestination(from: unknown): string {
  return typeof from === "string" &&
    from.startsWith("/") &&
    !from.startsWith("//") &&
    !/[\\\s]/.test(from) &&
    ![
      "/login",
      "/invitacion",
      "/recuperar-clave",
      "/restablecer-clave",
    ].includes(from.split(/[?#]/)[0])
    ? from
    : "/dashboard";
}
