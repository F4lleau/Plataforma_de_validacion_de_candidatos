import { create } from "zustand";
import {
  clearSession,
  getAccessToken,
  logoutSession,
  refreshSession,
  setUnauthorizedHandler,
  setSessionHandler,
} from "../services/api";
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
  logout: () => Promise<void>;
  restoreSession: () => Promise<void>;
  hasRole: (roles: UserRole[]) => boolean;
}

const signedOut = {
  user: null,
  accessToken: null,
  isAuthenticated: false,
  isLoading: false,
};
// Cutover: legacy bearer credentials are deliberately rejected by the API.
localStorage.removeItem("access_token");
localStorage.removeItem("refresh_token");

export const useAuthStore = create<AuthState>((set, get) => ({
  ...signedOut,
  isLoading: true,
  login: async (email, password) => {
    const result = await loginRequest(email, password);
    set({
      user: result.user,
      accessToken: result.access_token,
      isAuthenticated: true,
      isLoading: false,
    });
  },
  logout: async () => {
    await logoutSession();
  },
  restoreSession: async () => {
    try {
      await refreshSession();
    } catch {
      if (!getAccessToken()) clearSession(false);
    }
  },
  hasRole: (roles) => {
    const role = get().user?.role;
    return role !== undefined && roles.includes(role);
  },
}));
setUnauthorizedHandler(() => useAuthStore.setState(signedOut));
setSessionHandler((result) =>
  useAuthStore.setState({
    user: result.user,
    accessToken: result.access_token,
    isAuthenticated: true,
    isLoading: false,
  }),
);
