import { apiFetch, loginSession } from "./api";

export type UserRole = "admin" | "apoderado";

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  terms_accepted_at: string | null;
  terms_version: string | null;
  email_verified_at?: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export async function loginRequest(
  email: string,
  password: string,
): Promise<LoginResponse> {
  return loginSession(email, password);
}

export async function requestUnlock(email: string): Promise<{ message: string }> {
  return apiFetch(
    "/auth/unlock-request",
    {
      method: "POST",
      body: JSON.stringify({ email }),
    },
    false,
  );
}
