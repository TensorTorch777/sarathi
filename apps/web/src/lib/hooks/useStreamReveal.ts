"use client";

import { useEffect, useState } from "react";

import {
  charsPerTick,
  tickMs,
  type StreamSpeed,
} from "@/lib/stores/settings-store";

/**
 * Progressively reveal `fullText` for a ChatGPT-like streaming feel.
 * The backend returns a complete answer; this hook animates it into view.
 */
export function useStreamReveal(
  fullText: string,
  enabled: boolean,
  speed: StreamSpeed,
): { displayed: string; done: boolean } {
  const [displayed, setDisplayed] = useState(enabled ? "" : fullText);
  const [done, setDone] = useState(!enabled);

  useEffect(() => {
    if (!enabled) {
      setDisplayed(fullText);
      setDone(true);
      return;
    }

    setDisplayed("");
    setDone(false);
    let index = 0;
    const step = charsPerTick(speed);
    const delay = tickMs(speed);

    const timer = window.setInterval(() => {
      index = Math.min(fullText.length, index + step);
      setDisplayed(fullText.slice(0, index));
      if (index >= fullText.length) {
        window.clearInterval(timer);
        setDone(true);
      }
    }, delay);

    return () => window.clearInterval(timer);
  }, [fullText, enabled, speed]);

  return { displayed, done };
}
