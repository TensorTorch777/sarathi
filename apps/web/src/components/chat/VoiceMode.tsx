"use client";

import { Mic, MicOff, Radio } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { useVoiceMode } from "@/lib/voice/useVoiceMode";
import type { VoiceDonePayload } from "@/lib/voice/session";
import { cn } from "@/lib/utils/cn";

const STATE_LABEL: Record<string, string> = {
  idle: "Voice off",
  connecting: "Connecting…",
  listening: "Listening — speak when ready",
  processing: "Transcribing & reflecting…",
  speaking: "Sarathi is speaking — talk to interrupt",
  error: "Voice error",
};

export function VoiceMode({
  conversationId,
  onTranscript,
  onDone,
}: {
  conversationId?: string | null;
  onTranscript?: (text: string) => void;
  onDone?: (payload: VoiceDonePayload) => void;
}) {
  const { active, state, error, metrics, partialAnswer, start, stop, interrupt } =
    useVoiceMode({
      conversationId,
      onTranscript,
      onDone,
    });

  return (
    <div className="glass mx-auto mt-3 w-full max-w-3xl rounded-2xl px-4 py-3">
      <div className="flex flex-wrap items-center gap-3">
        <div
          className={cn(
            "flex h-11 w-11 items-center justify-center rounded-full border",
            active
              ? "border-[rgba(212,175,55,0.55)] bg-[rgba(212,175,55,0.16)] text-[var(--gold)]"
              : "border-[rgba(255,255,255,0.1)] text-[var(--ink-muted)]",
            state === "listening" && "animate-pulse",
            state === "speaking" && "shadow-[0_0_24px_rgba(212,175,55,0.35)]",
          )}
        >
          {active ? <Radio className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
        </div>

        <div className="min-w-0 flex-1">
          <p className="text-sm text-[var(--ink)]">{STATE_LABEL[state] ?? state}</p>
          <p className="text-xs text-[var(--ink-faint)]">
            Whisper STT · Piper calm narration · VAD barge-in
            {metrics?.stt_ms != null ? ` · STT ${Math.round(metrics.stt_ms)}ms` : ""}
            {metrics?.first_audio_ms != null
              ? ` · first audio ${Math.round(metrics.first_audio_ms)}ms`
              : ""}
          </p>
        </div>

        {!active ? (
          <Button type="button" onClick={() => void start()}>
            <Mic className="h-4 w-4" />
            Start voice
          </Button>
        ) : (
          <div className="flex gap-2">
            {state === "speaking" ? (
              <Button type="button" variant="ghost" onClick={() => interrupt()}>
                Interrupt
              </Button>
            ) : null}
            <Button type="button" variant="danger" onClick={() => void stop()}>
              <MicOff className="h-4 w-4" />
              Stop
            </Button>
          </div>
        )}
      </div>

      {error ? (
        <p className="mt-2 text-sm text-[var(--danger)]">{error}</p>
      ) : null}

      {partialAnswer && (state === "processing" || state === "speaking") ? (
        <p className="mt-3 line-clamp-3 text-sm text-[var(--ink-muted)]">{partialAnswer}</p>
      ) : null}
    </div>
  );
}
