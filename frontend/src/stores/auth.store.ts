import { create } from "zustand";
import { apiFetch, setUnauthorizedHandler } from "../services/api";
import { loginRequest, type AuthUser, type UserRole } from "../services/auth.service";

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  restoreSession: () => Promise<void>;
  hasRole: (roles: UserRole[]) => boolean;
}

// Invalida respuestas de login o /me pendientes cuando cambia la sesión.
let sessionVersion = 0;

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email, password) => {
    const version = ++sessionVersion;
    const result = await loginRequest(email, password);
    if (version !== sessionVersion) return;
    localStorage.setItem("access_token", result.access_token);
    // No hay renovación implementada; no persistimos el refresh emitido por la API.
    localStorage.removeItem("refresh_token");
    set({ user: result.user, accessToken: result.access_token, isAuthenticated: true, isLoading: false });
  },

  logout: () => {
    ++sessionVersion;
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, accessToken: null, isAuthenticated: false, isLoading: false });
  },

  restoreSession: async () => {
    const version = ++sessionVersion;
    const token = localStorage.getItem("access_token");
    if (!token) {
      get().logout();
      return;
    }
    set({ user: null, accessToken: null, isAuthenticated: false, isLoading: true });
    try {
      const user = await apiFetch<AuthUser>("/auth/me");
      if (version !== sessionVersion || token !== localStorage.getItem("access_token")) return;
      set({ user, accessToken: token, isAuthenticated: true, isLoading: false });
    } catch {
      if (version === sessionVersion) get().logout();
    }
  },

  hasRole: (roles) => {
    const role = get().user?.role;
    return role !== undefined && roles.includes(role);
  },
}));

setUnauthorizedHandler(() => useAuthStore.getState().logout());
