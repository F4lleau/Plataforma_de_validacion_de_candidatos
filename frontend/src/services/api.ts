export const API_BASE_URL = "http://localhost:8000/api/v1";

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

let onUnauthorized: (() => void) | undefined;

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

async function request<T>(
  endpoint: string,
  options: RequestInit,
  authenticated: boolean,
  binary = false,
): Promise<T> {
  const token = authenticated ? localStorage.getItem("access_token") : null;
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError")
      throw error;
    throw new ApiError(
      "No pudimos conectar con el servidor. Intentá nuevamente.",
      0,
    );
  }

  // Una respuesta antigua no debe cerrar una sesión iniciada después.
  if (
    response.status === 401 &&
    authenticated &&
    token === localStorage.getItem("access_token")
  ) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    onUnauthorized?.();
  }
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const detail =
      typeof body === "object" && body !== null && "detail" in body
        ? body.detail
        : null;
    const validationMessage = Array.isArray(detail)
      ? detail
          .map((item: unknown) => {
            if (typeof item !== "object" || item === null || !("msg" in item))
              return "";
            const field =
              "loc" in item && Array.isArray(item.loc)
                ? item.loc.filter((v) => v !== "body").join(".")
                : "";
            return `${field ? field + ": " : ""}${String(item.msg)}`;
          })
          .filter(Boolean)
          .join(" · ")
      : "";
    const message =
      response.status >= 500
        ? "El servidor no pudo completar la operación. Intentá nuevamente."
        : typeof detail === "string"
          ? detail
          : validationMessage || "Revisá los datos e intentá nuevamente.";
    throw new ApiError(message, response.status);
  }
  if (binary) {
    const type = response.headers.get("Content-Type") ?? "";
    if (
      !/^(application\/(pdf|vnd\.openxmlformats-officedocument\.spreadsheetml\.sheet)|text\/csv)/.test(
        type,
      )
    )
      throw new ApiError("La descarga no devolvió un archivo válido.", 502);
    const disposition = response.headers.get("Content-Disposition") ?? "";
    const filename =
      disposition.match(/filename="([A-Za-z0-9_.-]+)"/)?.[1] ?? "exportacion";
    return { blob: await response.blob(), filename } as T;
  }
  return response.json() as Promise<T>;
}

export function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
  authenticated = true,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type"))
    headers.set("Content-Type", "application/json");
  return request<T>(endpoint, { ...options, headers }, authenticated);
}

export function apiUpload<T>(endpoint: string, body: FormData): Promise<T> {
  return request<T>(endpoint, { method: "POST", body }, true);
}

export function apiDownload(
  endpoint: string,
): Promise<{ blob: Blob; filename: string }> {
  return request(endpoint, {}, true, true);
}
