"use client";

import { AppPageShell } from "@/components/layout/AppPageShell";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { getApiBaseUrl } from "@/lib/api/client";
import { useSettingsStore } from "@/lib/stores/settings-store";
import { cn } from "@/lib/utils/cn";

export default function SettingsPage() {
  const streamSpeed = useSettingsStore((s) => s.streamSpeed);
  const showVerseCards = useSettingsStore((s) => s.showVerseCards);
  const showReferences = useSettingsStore((s) => s.showReferences);
  const showPipelineMeta = useSettingsStore((s) => s.showPipelineMeta);
  const setStreamSpeed = useSettingsStore((s) => s.setStreamSpeed);
  const setShowVerseCards = useSettingsStore((s) => s.setShowVerseCards);
  const setShowReferences = useSettingsStore((s) => s.setShowReferences);
  const setShowPipelineMeta = useSettingsStore((s) => s.setShowPipelineMeta);

  return (
    <AppPageShell title="Settings" subtitle="Shape how Sarathi presents answers">
      <div className="space-y-4">
        <GlassPanel className="animate-fade-up space-y-4 p-6">
          <div>
            <h2 className="text-sm font-medium text-[var(--gold-soft)]">Answer streaming</h2>
            <p className="mt-1 text-sm text-[var(--ink-muted)]">
              Answers arrive from the local model as a whole, then reveal with a typing
              animation.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {(
              [
                ["calm", "Calm"],
                ["balanced", "Balanced"],
                ["swift", "Swift"],
              ] as const
            ).map(([value, label]) => (
              <button
                key={value}
                type="button"
                onClick={() => setStreamSpeed(value)}
                className={cn(
                  "rounded-xl border px-3 py-2.5 text-sm transition",
                  streamSpeed === value
                    ? "border-[rgba(212,175,55,0.45)] bg-[rgba(212,175,55,0.14)] text-[var(--gold-soft)]"
                    : "border-[rgba(255,255,255,0.08)] text-[var(--ink-muted)] hover:bg-[rgba(255,255,255,0.04)]",
                )}
              >
                {label}
              </button>
            ))}
          </div>
        </GlassPanel>

        <GlassPanel className="animate-fade-up space-y-3 p-6">
          <h2 className="text-sm font-medium text-[var(--gold-soft)]">Display</h2>
          <ToggleRow
            label="Verse cards"
            description="Show full Sanskrit + translation cards under replies"
            checked={showVerseCards}
            onChange={setShowVerseCards}
          />
          <ToggleRow
            label="Reference cards"
            description="Show citation chips with translations"
            checked={showReferences}
            onChange={setShowReferences}
          />
          <ToggleRow
            label="Pipeline metadata"
            description="Show rewritten query under assistant messages"
            checked={showPipelineMeta}
            onChange={setShowPipelineMeta}
          />
        </GlassPanel>

        <GlassPanel className="animate-fade-up space-y-2 p-6">
          <h2 className="text-sm font-medium text-[var(--gold-soft)]">Voice mode</h2>
          <p className="text-sm text-[var(--ink-muted)]">
            Start voice from the chat composer. Uses local Whisper for speech-to-text, Silero
            VAD for end-of-speech + barge-in, and Piper for calm narration. Streaming audio
            begins with a verse bridge while the answer generates.
          </p>
        </GlassPanel>

        <GlassPanel className="animate-fade-up space-y-2 p-6">
          <h2 className="text-sm font-medium text-[var(--gold-soft)]">API</h2>
          <p className="text-sm text-[var(--ink-muted)]">
            Connected to{" "}
            <code className="rounded bg-[rgba(255,255,255,0.06)] px-1.5 py-0.5 text-[var(--ink)]">
              {getApiBaseUrl()}
            </code>
          </p>
          <p className="text-xs text-[var(--ink-faint)]">
            Change via <code>NEXT_PUBLIC_API_BASE_URL</code> in <code>.env.local</code>.
          </p>
        </GlassPanel>
      </div>
    </AppPageShell>
  );
}

function ToggleRow({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="flex cursor-pointer items-start justify-between gap-4 rounded-xl border border-[rgba(255,255,255,0.06)] bg-[rgba(0,0,0,0.18)] px-3 py-3">
      <span>
        <span className="block text-sm text-[var(--ink)]">{label}</span>
        <span className="mt-0.5 block text-xs text-[var(--ink-faint)]">{description}</span>
      </span>
      <input
        type="checkbox"
        className="mt-1 h-4 w-4 accent-[var(--gold)]"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
      />
    </label>
  );
}
