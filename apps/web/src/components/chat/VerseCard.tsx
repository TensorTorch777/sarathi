"use client";

import { Star } from "lucide-react";
import { useState } from "react";

import { EmotionBadge } from "@/components/chat/EmotionBadge";
import { addFavorite } from "@/lib/api/memory";
import type { RetrievedVerse } from "@/lib/types/api";

export function VerseCard({ verse }: { verse: RetrievedVerse }) {
  const [favorited, setFavorited] = useState(false);
  const [busy, setBusy] = useState(false);

  return (
    <article className="glass animate-fade-up overflow-hidden rounded-2xl border border-[rgba(212,175,55,0.22)]">
      <header className="flex flex-wrap items-center justify-between gap-2 border-b border-[rgba(212,175,55,0.12)] px-4 py-3">
        <div>
          <p className="brand-mark text-lg text-[var(--gold-soft)]">{verse.citation}</p>
          <p className="text-xs text-[var(--ink-faint)]">
            Chapter {verse.chapter} · Verse {verse.verse_number}
            {verse.verified ? " · verified" : ""}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          {verse.emotions.slice(0, 3).map((emotion) => (
            <EmotionBadge key={`${verse.verse_id}-${emotion}`} emotion={emotion} />
          ))}
          <button
            type="button"
            disabled={busy || favorited}
            className="rounded-lg border border-[rgba(212,175,55,0.28)] p-1.5 text-[var(--gold)] transition hover:bg-[rgba(212,175,55,0.12)] disabled:opacity-50"
            aria-label="Save favorite verse to memory"
            onClick={() => {
              setBusy(true);
              void addFavorite({ verse_id: verse.verse_id })
                .then(() => setFavorited(true))
                .catch(() => undefined)
                .finally(() => setBusy(false));
            }}
          >
            <Star className={`h-4 w-4 ${favorited ? "fill-current" : ""}`} />
          </button>
        </div>
      </header>

      <div className="space-y-3 px-4 py-4">
        <p className="font-[family-name:var(--font-display)] text-xl leading-relaxed text-[#f7f0d8]">
          {verse.sanskrit}
        </p>
        {verse.transliteration ? (
          <p className="text-sm italic text-[var(--ink-muted)]">{verse.transliteration}</p>
        ) : null}
        <p className="text-sm leading-relaxed text-[var(--ink)]">{verse.translation}</p>
        {verse.topics.length > 0 ? (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {verse.topics.map((topic) => (
              <span
                key={`${verse.verse_id}-${topic}`}
                className="rounded-md border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] px-2 py-0.5 text-[11px] uppercase tracking-wider text-[var(--ink-muted)]"
              >
                {topic}
              </span>
            ))}
          </div>
        ) : null}
      </div>
    </article>
  );
}
