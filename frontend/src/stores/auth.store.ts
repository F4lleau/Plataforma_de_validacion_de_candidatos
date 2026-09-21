import { acceptTerms, type LegalDocument } from "../services/legal.service";
import { create } from "zustand";
import {
  apiFetch,
  setTermsRequiredHandler,
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
  acceptTerms: (document: LegalDocument) => Promise<void>;
  syncProfile: () => Promise<void>;
  hasRole: (roles: UserRole[]) => boolean;
}

// Acceptance is immutable for a given account. A concurrent /me or refresh
// started before acceptance must not overwrite the successful server response.
function mergeProfile(previous: AuthUser | null, incoming: AuthUser): AuthUser {
  return previous?.id === incoming.id &&
    previous.terms_accepted_at &&
    !incoming.terms_accepted_at
    ? {
        ...incoming,
        terms_accepted_at: previous.terms_accepted_at,
        terms_version: previous.terms_version,
      }
    : incoming;
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
  acceptTerms: async (document) => {
    const user = await acceptTerms(document);
    set({ user });
  },
  syncProfile: async () => {
    if (!get().isAuthenticated) return;
    const user = await apiFetch<AuthUser>("/auth/me");
    set((state) => ({ user: mergeProfile(state.user, user) }));
  },
  hasRole: (roles) => {
    const role = get().user?.role;
    return role !== undefined && roles.includes(role);
  },
}));
setUnauthorizedHandler(() => useAuthStore.setState(signedOut));
setSessionHandler((result) =>
  useAuthStore.setState((state) => ({
    user: mergeProfile(state.user, result.user),
    accessToken: result.access_token,
    isAuthenticated: true,
    isLoading: false,
  })),
);

setTermsRequiredHandler(() =>
  useAuthStore.setState((state) => ({
    user: state.user
      ? { ...state.user, terms_accepted_at: null, terms_version: null }
      : null,
  })),
);
