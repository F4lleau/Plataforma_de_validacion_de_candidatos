import { loginSession } from "./api";

export type UserRole = "admin" | "apoderado";

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
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
