"use client";

import { useEffect } from "react";

import { EmotionBadge } from "@/components/chat/EmotionBadge";
import { MarkdownContent } from "@/components/chat/MarkdownContent";
import { ReferenceCard } from "@/components/chat/ReferenceCard";
import { VerseCard } from "@/components/chat/VerseCard";
import { useStreamReveal } from "@/lib/hooks/useStreamReveal";
import type { ChatMessage } from "@/lib/stores/conversation-store";
import { useSettingsStore } from "@/lib/stores/settings-store";
import { cn } from "@/lib/utils/cn";

export function MessageBubble({
  message,
  onStreamComplete,
}: {
  message: ChatMessage;
  onStreamComplete?: (messageId: string) => void;
}) {
  const isUser = message.role === "user";
  const streamSpeed = useSettingsStore((s) => s.streamSpeed);
  const showVerseCards = useSettingsStore((s) => s.showVerseCards);
  const showReferences = useSettingsStore((s) => s.showReferences);
  const showPipelineMeta = useSettingsStore((s) => s.showPipelineMeta);

  const shouldStream = !isUser && Boolean(message.streaming);
  const { displayed, done } = useStreamReveal(message.content, shouldStream, streamSpeed);

  useEffect(() => {
    if (shouldStream && done) {
      onStreamComplete?.(message.id);
    }
  }, [shouldStream, done, message.id, onStreamComplete]);

  if (isUser) {
    return (
      <div className="animate-fade-up flex justify-end">
        <div className="max-w-[min(720px,92%)] rounded-2xl rounded-br-md bg-gradient-to-br from-[rgba(212,175,55,0.22)] to-[rgba(212,175,55,0.08)] px-4 py-3 text-[var(--ink)] shadow-[0_8px_24px_rgba(0,0,0,0.25)] ring-1 ring-[rgba(212,175,55,0.25)]">
          <p className="whitespace-pre-wrap text-[15px] leading-relaxed">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-up flex justify-start">
      <div className="flex w-full max-w-[min(820px,100%)] flex-col gap-3">
        <div className="glass rounded-2xl rounded-bl-md px-4 py-4 sm:px-5">
          {message.emotions && message.emotions.length > 0 ? (
            <div className="mb-3 flex flex-wrap gap-1.5">
              {message.emotions.map((emotion) => (
                <EmotionBadge key={`${message.id}-${emotion}`} emotion={emotion} />
              ))}
            </div>
          ) : null}

          {message.error ? (
            <p className="text-sm text-[var(--danger)]">{message.error}</p>
          ) : (
            <MarkdownContent content={displayed} streaming={shouldStream && !done} />
          )}

          {showPipelineMeta && message.rewrittenQuery ? (
            <p className="mt-4 border-t border-[rgba(255,255,255,0.06)] pt-3 text-xs text-[var(--ink-faint)]">
              Rewritten query: {message.rewrittenQuery}
            </p>
          ) : null}

          {message.topics && message.topics.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {message.topics.map((topic) => (
                <span
                  key={`${message.id}-topic-${topic}`}
                  className="rounded-md border border-[rgba(212,175,55,0.2)] px-2 py-0.5 text-[11px] uppercase tracking-wider text-[var(--gold-dim)]"
                >
                  {topic}
                </span>
              ))}
            </div>
          ) : null}
        </div>

        {showReferences && message.citations && message.citations.length > 0 ? (
          <section className="space-y-2">
            <h3 className="px-1 text-xs uppercase tracking-[0.18em] text-[var(--ink-faint)]">
              References
            </h3>
            <div className="grid gap-2 sm:grid-cols-2">
              {message.citations.map((citation) => (
                <ReferenceCard key={citation.verse_id} citation={citation} />
              ))}
            </div>
          </section>
        ) : null}

        {showVerseCards && message.verses && message.verses.length > 0 ? (
          <section className={cn("space-y-3", shouldStream && !done && "opacity-70")}>
            <h3 className="px-1 text-xs uppercase tracking-[0.18em] text-[var(--ink-faint)]">
              Verse cards
            </h3>
            <div className="grid gap-3">
              {message.verses.map((verse) => (
                <VerseCard key={verse.verse_id} verse={verse} />
              ))}
            </div>
          </section>
        ) : null}
      </div>
    </div>
  );
}
