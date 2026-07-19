"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { useAuthStore } from "@/lib/stores/auth-store";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const hydrated = useAuthStore((s) => s.hydrated);
  const accessToken = useAuthStore((s) => s.accessToken);

  useEffect(() => {
    if (hydrated && !accessToken) {
      router.replace("/login");
    }
  }, [hydrated, accessToken, router]);

  if (!hydrated) {
    return (
      <div className="flex min-h-[100dvh] items-center justify-center">
        <p className="brand-mark text-3xl gold-text">Sarathi</p>
      </div>
    );
  }

  if (!accessToken) {
    return null;
  }

  return children;
}
