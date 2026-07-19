import type { AnswerCitation } from "@/lib/types/api";

export function ReferenceCard({ citation }: { citation: AnswerCitation }) {
  return (
    <aside className="glass animate-fade-up flex gap-3 rounded-xl px-3.5 py-3">
      <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[rgba(212,175,55,0.12)] text-sm font-semibold text-[var(--gold)]">
        {citation.chapter}.{citation.verse_number}
      </div>
      <div className="min-w-0">
        <p className="text-sm font-medium text-[var(--gold-soft)]">{citation.citation}</p>
        <p className="mt-1 line-clamp-3 text-xs leading-relaxed text-[var(--ink-muted)]">
          {citation.translation}
        </p>
      </div>
    </aside>
  );
}
