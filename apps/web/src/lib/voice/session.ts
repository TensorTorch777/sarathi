"use client";

import { useAuthStore } from "@/lib/stores/auth-store";
import {
  arrayBufferToBase64,
  base64ToArrayBuffer,
  PcmPlaybackQueue,
} from "@/lib/voice/audio";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000/api/v1";

export type VoiceUiState =
  | "idle"
  | "connecting"
  | "listening"
  | "processing"
  | "speaking"
  | "error";

export interface VoiceDonePayload {
  answer: string;
  transcript: string;
  emotions: string[];
  topics: string[];
  citations: Array<{
    citation: string;
    chapter: number;
    verse_number: number;
    verse_id: string;
    translation: string;
  }>;
  verses: Array<{
    verse_id: string;
    citation: string;
    chapter: number;
    verse_number: number;
    sanskrit: string;
    translation: string;
    transliteration: string | null;
    topics: string[];
    emotions: string[];
    verified: boolean;
  }>;
  metrics?: {
    stt_ms?: number;
    total_ms?: number;
    first_audio_ms?: number | null;
    first_audio_under_2s?: boolean;
  };
}

export interface VoiceSessionHandlers {
  onState?: (state: VoiceUiState) => void;
  onTranscript?: (text: string) => void;
  onAnswerDelta?: (text: string) => void;
  onDone?: (payload: VoiceDonePayload) => void;
  onError?: (message: string) => void;
  onMetrics?: (metrics: VoiceDonePayload["metrics"]) => void;
}

function wsUrl(token: string): string {
  const http = API_BASE.replace(/\/$/, "");
  const ws = http.startsWith("https")
    ? http.replace(/^https/, "wss")
    : http.replace(/^http/, "ws");
  return `${ws}/voice/session?token=${encodeURIComponent(token)}`;
}

export class VoiceSession {
  private socket: WebSocket | null = null;
  private playback: PcmPlaybackQueue | null = null;
  private handlers: VoiceSessionHandlers;
  private conversationId: string | null;
  private answerBuffer = "";
  private closed = false;

  constructor(handlers: VoiceSessionHandlers = {}, conversationId?: string | null) {
    this.handlers = handlers;
    this.conversationId = conversationId ?? null;
  }

  async connect(): Promise<void> {
    const token = useAuthStore.getState().accessToken;
    if (!token) {
      throw new Error("Sign in to use voice mode");
    }
    this.handlers.onState?.("connecting");
    this.playback = new PcmPlaybackQueue(22050);
    await this.playback.resume();
    this.playback.setIdleHandler(() => {
      if (!this.closed) this.handlers.onState?.("listening");
    });

    await new Promise<void>((resolve, reject) => {
      const socket = new WebSocket(wsUrl(token));
      this.socket = socket;
      socket.onopen = () => resolve();
      socket.onerror = () => reject(new Error("Voice WebSocket failed to connect"));
      socket.onclose = () => {
        if (!this.closed) this.handlers.onState?.("idle");
      };
      socket.onmessage = (event) => {
        void this.handleMessage(String(event.data));
      };
    });
  }

  private async handleMessage(raw: string): Promise<void> {
    let data: Record<string, unknown>;
    try {
      data = JSON.parse(raw) as Record<string, unknown>;
    } catch {
      return;
    }
    const type = data.type;

    if (type === "ready") {
      this.handlers.onState?.("listening");
      return;
    }
    if (type === "final_transcript") {
      this.handlers.onTranscript?.(String(data.text ?? ""));
      this.handlers.onState?.("processing");
      return;
    }
    if (type === "answer_delta") {
      const text = String(data.text ?? "");
      this.answerBuffer += text;
      this.handlers.onAnswerDelta?.(text);
      return;
    }
    if (type === "audio") {
      this.handlers.onState?.("speaking");
      const b64 = String(data.audio_b64 ?? "");
      const sampleRate = Number(data.sample_rate ?? 22050);
      if (b64 && this.playback) {
        await this.playback.resume();
        this.playback.enqueuePcm16(base64ToArrayBuffer(b64), sampleRate);
      }
      return;
    }
    if (type === "done") {
      const payload = data as unknown as VoiceDonePayload;
      this.handlers.onMetrics?.(payload.metrics);
      this.handlers.onDone?.({
        ...payload,
        answer: payload.answer || this.answerBuffer,
      });
      this.answerBuffer = "";
      if (!this.playback?.isPlaying) {
        this.handlers.onState?.("listening");
      }
      return;
    }
    if (type === "interrupted") {
      this.playback?.interrupt();
      this.answerBuffer = "";
      this.handlers.onState?.("listening");
      return;
    }
    if (type === "error") {
      this.handlers.onError?.(String(data.message ?? "Voice error"));
      this.handlers.onState?.("error");
    }
  }

  /** Send a completed utterance (PCM16 LE mono) after VAD end-of-speech. */
  sendUtterance(pcm16: ArrayBuffer, sampleRate = 16000): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return;
    // Barge-in: stop local playback before sending the next turn.
    this.playback?.interrupt();
    this.answerBuffer = "";
    this.handlers.onState?.("processing");
    this.socket.send(
      JSON.stringify({
        type: "utterance",
        format: "pcm_s16le",
        sample_rate: sampleRate,
        audio_b64: arrayBufferToBase64(pcm16),
        conversation_id: this.conversationId,
      }),
    );
  }

  interrupt(): void {
    this.playback?.interrupt();
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type: "interrupt" }));
    }
    this.handlers.onState?.("listening");
  }

  setConversationId(id: string | null): void {
    this.conversationId = id;
  }

  async close(): Promise<void> {
    this.closed = true;
    this.interrupt();
    this.socket?.close();
    this.socket = null;
    await this.playback?.close();
    this.playback = null;
    this.handlers.onState?.("idle");
  }
}
