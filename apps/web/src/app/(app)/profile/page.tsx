"use client";

import { useEffect, useState } from "react";

import { AppPageShell } from "@/components/layout/AppPageShell";
import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { ApiError } from "@/lib/types/api";
import { useAuthStore } from "@/lib/stores/auth-store";

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  const loadProfile = useAuthStore((s) => s.loadProfile);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        await loadProfile();
        if (!cancelled) setError(null);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? err.message
              : "Could not refresh profile from the API.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [loadProfile]);

  return (
    <AppPageShell title="Profile" subtitle="Your Sarathi account">
      <GlassPanel className="animate-fade-up space-y-5 p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[rgba(212,175,55,0.15)] brand-mark text-3xl text-[var(--gold)]">
            {(user?.display_name || user?.email || "?").slice(0, 1).toUpperCase()}
          </div>
          <div>
            <p className="text-xl text-[var(--ink)]">
              {user?.display_name || "Seeker"}
            </p>
            <p className="text-sm text-[var(--ink-muted)]">{user?.email}</p>
          </div>
        </div>

        <dl className="grid gap-3 sm:grid-cols-2">
          <Field label="User ID" value={user?.id ?? "—"} mono />
          <Field label="Role" value={user?.role ?? "—"} />
          <Field label="Locale" value={user?.locale || "Not set"} />
          <Field label="Status" value={user?.is_active ? "Active" : "Inactive"} />
        </dl>

        {error ? (
          <p className="text-sm text-[var(--danger)]">{error}</p>
        ) : null}

        <Button
          variant="ghost"
          loading={loading}
          onClick={async () => {
            setLoading(true);
            setError(null);
            try {
              await loadProfile();
            } catch (err) {
              setError(err instanceof ApiError ? err.message : "Refresh failed");
            } finally {
              setLoading(false);
            }
          }}
        >
          Refresh from server
        </Button>
      </GlassPanel>
    </AppPageShell>
  );
}

function Field({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="rounded-xl border border-[rgba(255,255,255,0.06)] bg-[rgba(0,0,0,0.2)] px-3 py-2.5">
      <dt className="text-[11px] uppercase tracking-[0.16em] text-[var(--ink-faint)]">
        {label}
      </dt>
      <dd
        className={`mt-1 break-all text-sm text-[var(--ink)] ${mono ? "font-mono text-xs" : ""}`}
      >
        {value}
      </dd>
    </div>
  );
}
