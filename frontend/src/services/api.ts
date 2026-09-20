export const API_BASE_URL = "http://localhost:8000/api/v1";

function clearStoredTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

async function parseApiError(response: Response): Promise<never> {
  const errorBody = await response.json().catch(() => null) as { detail?: string } | null;
  throw new Error(errorBody?.detail || "No se pudo completar la operación.");
}

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("access_token");
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (response.status === 401) clearStoredTokens();
  if (!response.ok) return parseApiError(response);
  return response.json() as Promise<T>;
}

export async function apiUpload<T>(endpoint: string, body: FormData): Promise<T> {
  const token = localStorage.getItem("access_token");
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body,
  });

  if (response.status === 401) clearStoredTokens();
  if (!response.ok) return parseApiError(response);
  return response.json() as Promise<T>;
}
