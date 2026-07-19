"use client";

import { useEffect, type ReactNode } from "react";

import { configureApiAuth } from "@/lib/api/client";
import { useAuthStore } from "@/lib/stores/auth-store";

export function AppProviders({ children }: { children: ReactNode }) {
  const getAccessToken = useAuthStore((s) => s.accessToken);
  const refresh = useAuthStore((s) => s.refresh);
  const setHydrated = useAuthStore((s) => s.setHydrated);
  const hydrated = useAuthStore((s) => s.hydrated);

  useEffect(() => {
    configureApiAuth({
      getAccessToken: () => useAuthStore.getState().accessToken,
      refreshAccessToken: () => useAuthStore.getState().refresh(),
    });
  }, [getAccessToken, refresh]);

  useEffect(() => {
    // Persist middleware may already flip hydrated; ensure a fallback for SSR.
    if (!hydrated) {
      const unsub = useAuthStore.persist.onFinishHydration(() => {
        setHydrated(true);
      });
      if (useAuthStore.persist.hasHydrated()) {
        setHydrated(true);
      }
      return unsub;
    }
    return undefined;
  }, [hydrated, setHydrated]);

  return children;
}
