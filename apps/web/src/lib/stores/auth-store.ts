"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import {
  fetchCurrentUser,
  loginUser,
  logoutUser,
  refreshTokens,
  registerUser,
} from "@/lib/api/auth";
import type { TokenPair, User } from "@/lib/types/api";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  hydrated: boolean;
  setHydrated: (value: boolean) => void;
  setSession: (user: User, tokens: TokenPair) => void;
  clearSession: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<string | null>;
  loadProfile: () => Promise<User>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      hydrated: false,

      setHydrated: (value) => set({ hydrated: value }),

      setSession: (user, tokens) =>
        set({
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
        }),

      clearSession: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
        }),

      login: async (email, password) => {
        const response = await loginUser({ email, password });
        get().setSession(response.user, response.tokens);
      },

      register: async (email, password, displayName) => {
        const response = await registerUser({
          email,
          password,
          display_name: displayName || undefined,
        });
        get().setSession(response.user, response.tokens);
      },

      logout: async () => {
        const refresh = get().refreshToken;
        try {
          await logoutUser(refresh);
        } catch {
          // Local session still cleared even if the server call fails.
        }
        get().clearSession();
      },

      refresh: async () => {
        const current = get().refreshToken;
        if (!current) {
          get().clearSession();
          return null;
        }
        try {
          const tokens = await refreshTokens(current);
          set({
            accessToken: tokens.access_token,
            refreshToken: tokens.refresh_token,
          });
          return tokens.access_token;
        } catch {
          get().clearSession();
          return null;
        }
      },

      loadProfile: async () => {
        const user = await fetchCurrentUser();
        set({ user });
        return user;
      },
    }),
    {
      name: "sarathi-auth",
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated(true);
      },
    },
  ),
);
