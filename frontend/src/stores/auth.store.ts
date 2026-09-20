import { create } from "zustand";
import { apiFetch } from "../services/api";
import {
  loginRequest,
  type AuthUser,
  type UserRole,
} from "../services/auth.service";

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

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: localStorage.getItem("access_token"),
  isAuthenticated: false,
  isLoading: true,

  login: async (email, password) => {
    const result = await loginRequest(email, password);
    localStorage.setItem("access_token", result.access_token);
    localStorage.setItem("refresh_token", result.refresh_token);
    set({ user: result.user, accessToken: result.access_token, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, accessToken: null, isAuthenticated: false });
  },

  restoreSession: async () => {
    if (!localStorage.getItem("access_token")) {
      set({ isLoading: false });
      return;
    }

    try {
      const user = await apiFetch<AuthUser>("/auth/me");
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      get().logout();
      set({ isLoading: false });
    }
  },

  hasRole: (roles) => {
    const role = get().user?.role;
    return role !== undefined && roles.includes(role);
  },
}));