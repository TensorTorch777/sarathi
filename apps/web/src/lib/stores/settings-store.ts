"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

export type StreamSpeed = "calm" | "balanced" | "swift";

interface SettingsState {
  streamSpeed: StreamSpeed;
  showVerseCards: boolean;
  showReferences: boolean;
  showPipelineMeta: boolean;
  setStreamSpeed: (speed: StreamSpeed) => void;
  setShowVerseCards: (value: boolean) => void;
  setShowReferences: (value: boolean) => void;
  setShowPipelineMeta: (value: boolean) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      streamSpeed: "balanced",
      showVerseCards: true,
      showReferences: true,
      showPipelineMeta: false,
      setStreamSpeed: (streamSpeed) => set({ streamSpeed }),
      setShowVerseCards: (showVerseCards) => set({ showVerseCards }),
      setShowReferences: (showReferences) => set({ showReferences }),
      setShowPipelineMeta: (showPipelineMeta) => set({ showPipelineMeta }),
    }),
    { name: "sarathi-settings" },
  ),
);

/** Characters revealed per tick for progressive answer streaming. */
export function charsPerTick(speed: StreamSpeed): number {
  switch (speed) {
    case "calm":
      return 2;
    case "swift":
      return 12;
    default:
      return 5;
  }
}

export function tickMs(speed: StreamSpeed): number {
  switch (speed) {
    case "calm":
      return 28;
    case "swift":
      return 12;
    default:
      return 18;
  }
}
