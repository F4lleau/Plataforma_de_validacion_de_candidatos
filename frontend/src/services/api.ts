import type { LoginResponse } from "./auth.service";
export const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  `http://${typeof window !== "undefined" ? window.location.hostname : "localhost"}:8000/api/v1`;

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

let onTermsRequired: (() => void) | undefined;
export function setTermsRequiredHandler(handler: () => void) {
  onTermsRequired = handler;
}

let onUnauthorized: (() => void) | undefined;
let onSession: ((session: LoginResponse) => void) | undefined;
let accessToken: string | null = null;
let generation = 0;
let renewal: Promise<LoginResponse> | null = null;
const channel =
  typeof window !== "undefined" && typeof BroadcastChannel !== "undefined"
    ? new BroadcastChannel("je-session")
    : null;

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}
export function setSessionHandler(handler: (session: LoginResponse) => void) {
  onSession = handler;
}
export function getAccessToken() {
  return accessToken;
}
export function setAccessToken(token: string | null) {
  accessToken = token;
  generation++;
}
export function clearSession(broadcast = true) {
  setAccessToken(null);
  onUnauthorized?.();
  if (broadcast) channel?.postMessage({ type: "logout" });
}
channel?.addEventListener("message", (event) => {
  if (event.data?.type === "logout") clearSession(false);
  // A different tab logged in: discard the previous identity, restore on reload.
  if (event.data?.type === "login") clearSession(false);
});

export async function sessionLock<T>(work: () => Promise<T>): Promise<T> {
  if (typeof navigator !== "undefined" && navigator.locks)
    return navigator.locks.request("je-auth-cookie", work);
  return work();
}

async function csrfToken(): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/auth/csrf`, {
    credentials: "include",
  });
  if (!response.ok)
    throw new ApiError(
      "No se pudo iniciar la operación segura.",
      response.status,
    );
  return (await response.json()).csrf_token;
}

export function refreshSession(): Promise<LoginResponse> {
  if (renewal) return renewal;
  const version = generation;
  renewal = sessionLock(async () => {
    if (version !== generation) throw new ApiError("La sesión cambió.", 401);
    const result = await request<LoginResponse>(
      "/auth/refresh",
      { method: "POST" },
      false,
    );
    if (version !== generation) throw new ApiError("La sesión cambió.", 401);
    accessToken = result.access_token;
    onSession?.(result);
    return result;
  }).finally(() => {
    renewal = null;
  });
  return renewal;
}

export async function loginSession(
  email: string,
  password: string,
): Promise<LoginResponse> {
  const version = ++generation;
  return sessionLock(async () => {
    const result = await request<LoginResponse>(
      "/auth/login",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      },
      false,
    );
    if (version !== generation) throw new ApiError("La sesión cambió.", 401);
    accessToken = result.access_token;
    channel?.postMessage({ type: "login" });
    return result;
  });
}

export async function logoutSession(): Promise<void> {
  clearSession();
  await sessionLock(() => request("/auth/logout", { method: "POST" }, false));
}

async function request<T>(
  endpoint: string,
  options: RequestInit,
  authenticated: boolean,
  binary = false,
  retried = false,
): Promise<T> {
  const token = authenticated ? accessToken : null;
  const version = generation;
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const unsafe = !["GET", "HEAD"].includes(options.method ?? "GET");
  let response: Response;
  try {
    if (unsafe) headers.set("X-CSRF-Token", await csrfToken());
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      credentials: "include",
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

  // Authentication fails before domain handlers run: retry only a 401, once.
  if (response.status === 401 && authenticated && version === generation) {
    if (!retried) {
      try {
        if (token === accessToken) await refreshSession();
        if (version !== generation)
          throw new ApiError("La sesión cambió.", 401);
        return await request<T>(endpoint, options, authenticated, binary, true);
      } catch (error) {
        if (
          error instanceof ApiError &&
          error.status === 401 &&
          version === generation
        )
          clearSession();
        throw error;
      }
    }
    clearSession();
  }
  if (authenticated && version !== generation)
    throw new ApiError("La sesión cambió.", 401);
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const detail =
      typeof body === "object" && body !== null && "detail" in body
        ? body.detail
        : null;
    if (authenticated && version !== generation)
      throw new ApiError("La sesión cambió.", 401);
    const structured =
      typeof detail === "object" &&
      detail !== null &&
      "code" in detail &&
      "message" in detail
        ? detail
        : null;
    const code = structured ? String(structured.code) : undefined;
    if (
      authenticated &&
      response.status === 403 &&
      code === "TERMS_ACCEPTANCE_REQUIRED"
    )
      onTermsRequired?.();
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
          : structured
            ? String(structured.message)
            : validationMessage || "Revisá los datos e intentá nuevamente.";
    throw new ApiError(message, response.status, code);
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
  const result = (await response.json()) as T;
  if (authenticated && version !== generation)
    throw new ApiError("La sesión cambió.", 401);
  return result;
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
