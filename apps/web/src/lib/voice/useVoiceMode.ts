"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { floatTo16BitPCM } from "@/lib/voice/audio";
import {
  VoiceSession,
  type VoiceDonePayload,
  type VoiceUiState,
} from "@/lib/voice/session";

export interface UseVoiceModeOptions {
  conversationId?: string | null;
  onTranscript?: (text: string) => void;
  onAnswerDelta?: (text: string) => void;
  onDone?: (payload: VoiceDonePayload) => void;
}

/**
 * Mic capture + Silero VAD + Whisper/Piper voice session.
 * Speech start interrupts any ongoing TTS (barge-in).
 */
export function useVoiceMode(options: UseVoiceModeOptions = {}) {
  const [active, setActive] = useState(false);
  const [state, setState] = useState<VoiceUiState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<VoiceDonePayload["metrics"]>();
  const [partialAnswer, setPartialAnswer] = useState("");

  const sessionRef = useRef<VoiceSession | null>(null);
  const vadRef = useRef<{ pause: () => Promise<void>; destroy: () => Promise<void> } | null>(
    null,
  );
  const optionsRef = useRef(options);
  optionsRef.current = options;

  const stop = useCallback(async () => {
    try {
      await vadRef.current?.pause();
      await vadRef.current?.destroy();
    } catch {
      // ignore teardown races
    }
    vadRef.current = null;
    await sessionRef.current?.close();
    sessionRef.current = null;
    setActive(false);
    setState("idle");
    setPartialAnswer("");
  }, []);

  const start = useCallback(async () => {
    setError(null);
    setMetrics(undefined);
    setPartialAnswer("");

    const session = new VoiceSession(
      {
        onState: setState,
        onTranscript: (text) => optionsRef.current.onTranscript?.(text),
        onAnswerDelta: (text) => {
          setPartialAnswer((prev) => prev + text);
          optionsRef.current.onAnswerDelta?.(text);
        },
        onDone: (payload) => {
          setPartialAnswer(payload.answer);
          setMetrics(payload.metrics);
          optionsRef.current.onDone?.(payload);
        },
        onError: (message) => setError(message),
        onMetrics: setMetrics,
      },
      optionsRef.current.conversationId,
    );

    try {
      await session.connect();
      sessionRef.current = session;

      const { MicVAD } = await import("@ricky0123/vad-web");
      const vad = await MicVAD.new({
        startOnLoad: true,
        model: "v5",
        baseAssetPath: "/vad/",
        onnxWASMBasePath: "/vad/",
        positiveSpeechThreshold: 0.6,
        negativeSpeechThreshold: 0.35,
        redemptionMs: 400,
        minSpeechMs: 250,
        onSpeechStart: () => {
          session.interrupt();
          setState("listening");
        },
        onSpeechEnd: (audio) => {
          if (audio.length < 1600) return;
          session.sendUtterance(floatTo16BitPCM(audio), 16000);
        },
      });

      vadRef.current = vad;
      setActive(true);
      setState("listening");
    } catch (err) {
      await session.close();
      setError(err instanceof Error ? err.message : "Could not start voice mode");
      setState("error");
      setActive(false);
    }
  }, []);

  useEffect(() => {
    sessionRef.current?.setConversationId(options.conversationId ?? null);
  }, [options.conversationId]);

  useEffect(() => {
    return () => {
      void stop();
    };
  }, [stop]);

  return {
    active,
    state,
    error,
    metrics,
    partialAnswer,
    start,
    stop,
    interrupt: () => sessionRef.current?.interrupt(),
  };
}
