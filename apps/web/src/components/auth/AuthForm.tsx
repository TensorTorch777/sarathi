"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { Input } from "@/components/ui/Input";
import { ApiError } from "@/lib/types/api";
import { useAuthStore } from "@/lib/stores/auth-store";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const register = useAuthStore((s) => s.register);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === "login") {
        await login(email.trim(), password);
      } else {
        await register(email.trim(), password, displayName.trim() || undefined);
      }
      router.replace("/chat");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Authentication failed",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-[100dvh] items-center justify-center px-4 py-10">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-24 top-10 h-72 w-72 rounded-full bg-[rgba(212,175,55,0.12)] blur-3xl" />
        <div className="absolute bottom-0 right-0 h-80 w-80 rounded-full bg-[rgba(120,90,30,0.18)] blur-3xl" />
      </div>

      <GlassPanel className="relative z-10 w-full max-w-md p-8">
        <div className="mb-8 text-center">
          <p className="brand-mark text-5xl gold-text">Sarathi</p>
          <p className="mt-2 text-sm text-[var(--ink-muted)]">
            {mode === "login"
              ? "Welcome back. Continue your reflection."
              : "Create an account to begin with the Gita."}
          </p>
        </div>

        <form className="space-y-4" onSubmit={onSubmit}>
          {mode === "register" ? (
            <Input
              label="Display name"
              name="display_name"
              autoComplete="name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Optional"
            />
          ) : null}
          <Input
            label="Email"
            name="email"
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
          />
          <Input
            label="Password"
            name="password"
            type="password"
            required
            minLength={8}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
          />

          {error ? (
            <p className="rounded-lg border border-[rgba(224,122,106,0.35)] bg-[rgba(224,122,106,0.1)] px-3 py-2 text-sm text-[#f0b4aa]">
              {error}
            </p>
          ) : null}

          <Button type="submit" className="w-full" loading={loading}>
            {mode === "login" ? "Sign in" : "Create account"}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-[var(--ink-muted)]">
          {mode === "login" ? (
            <>
              New here?{" "}
              <Link href="/register" className="text-[var(--gold-soft)] underline-offset-4 hover:underline">
                Create an account
              </Link>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <Link href="/login" className="text-[var(--gold-soft)] underline-offset-4 hover:underline">
                Sign in
              </Link>
            </>
          )}
        </p>
      </GlassPanel>
    </div>
  );
}
