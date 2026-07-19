"use client";

import { useCallback, useEffect, useState } from "react";

import { AppPageShell } from "@/components/layout/AppPageShell";
import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { Input } from "@/components/ui/Input";
import {
  createGoal,
  createJournal,
  createMemoryItem,
  createReflection,
  listFavorites,
  listGoals,
  listJournals,
  listMemoryItems,
  listReflections,
  recallMemories,
  type CareerGoal,
  type FavoriteVerse,
  type JournalEntry,
  type MemoryItem,
  type ReflectionEntry,
} from "@/lib/api/memory";
import { ApiError } from "@/lib/types/api";

type Tab = "overview" | "goals" | "journals" | "favorites" | "recall";

export default function MemoryPage() {
  const [tab, setTab] = useState<Tab>("overview");
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<MemoryItem[]>([]);
  const [goals, setGoals] = useState<CareerGoal[]>([]);
  const [journals, setJournals] = useState<JournalEntry[]>([]);
  const [reflections, setReflections] = useState<ReflectionEntry[]>([]);
  const [favorites, setFavorites] = useState<FavoriteVerse[]>([]);
  const [recallQuery, setRecallQuery] = useState("");
  const [recallHits, setRecallHits] = useState<
    Array<{ kind: string; title: string | null; content: string; score: number }>
  >([]);

  const [goalTitle, setGoalTitle] = useState("");
  const [goalDesc, setGoalDesc] = useState("");
  const [journalTitle, setJournalTitle] = useState("");
  const [journalContent, setJournalContent] = useState("");
  const [journalMood, setJournalMood] = useState("");
  const [reflectionJournalId, setReflectionJournalId] = useState("");
  const [reflectionContent, setReflectionContent] = useState("");
  const [noteContent, setNoteContent] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const [m, g, j, r, f] = await Promise.all([
        listMemoryItems(),
        listGoals(),
        listJournals(),
        listReflections(),
        listFavorites(),
      ]);
      setItems(m);
      setGoals(g);
      setJournals(j);
      setReflections(r);
      setFavorites(f);
      if (!reflectionJournalId && j[0]) setReflectionJournalId(j[0].id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load memory");
    }
  }, [reflectionJournalId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const run = async (fn: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await fn();
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <AppPageShell
      title="Memory"
      subtitle="Long-term vector memory — goals, journals, favorites, reflections"
    >
      <div className="mb-4 flex flex-wrap gap-2">
        {(
          [
            ["overview", "Overview"],
            ["goals", "Career goals"],
            ["journals", "Journal"],
            ["favorites", "Favorite verses"],
            ["recall", "Recall"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={`rounded-xl border px-3 py-1.5 text-sm transition ${
              tab === id
                ? "border-[rgba(212,175,55,0.45)] bg-[rgba(212,175,55,0.14)] text-[var(--gold-soft)]"
                : "border-[rgba(255,255,255,0.08)] text-[var(--ink-muted)]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {error ? <p className="mb-3 text-sm text-[var(--danger)]">{error}</p> : null}

      {tab === "overview" ? (
        <div className="space-y-4">
          <GlassPanel className="space-y-3 p-5">
            <h2 className="text-sm text-[var(--gold-soft)]">Add a memory note</h2>
            <textarea
              className="min-h-[90px] w-full rounded-xl border border-[rgba(212,175,55,0.22)] bg-[rgba(0,0,0,0.28)] px-3 py-2 text-sm outline-none focus:border-[var(--gold)]"
              placeholder="Something Sarathi should remember about you…"
              value={noteContent}
              onChange={(e) => setNoteContent(e.target.value)}
            />
            <Button
              loading={busy}
              onClick={() =>
                void run(async () => {
                  await createMemoryItem({ content: noteContent, kind: "note" });
                  setNoteContent("");
                })
              }
              disabled={!noteContent.trim()}
            >
              Save to vector memory
            </Button>
          </GlassPanel>

          <GlassPanel className="space-y-3 p-5">
            <h2 className="text-sm text-[var(--gold-soft)]">
              Indexed memories ({items.length})
            </h2>
            <ul className="space-y-2">
              {items.length === 0 ? (
                <li className="text-sm text-[var(--ink-faint)]">No memories yet.</li>
              ) : (
                items.map((item) => (
                  <li
                    key={item.id}
                    className="rounded-xl border border-[rgba(255,255,255,0.06)] bg-[rgba(0,0,0,0.2)] px-3 py-2"
                  >
                    <p className="text-xs uppercase tracking-wider text-[var(--gold-dim)]">
                      {item.kind}
                    </p>
                    <p className="text-sm text-[var(--ink)]">{item.title || "Untitled"}</p>
                    <p className="mt-1 line-clamp-3 text-xs text-[var(--ink-muted)]">
                      {item.content}
                    </p>
                  </li>
                ))
              )}
            </ul>
          </GlassPanel>
        </div>
      ) : null}

      {tab === "goals" ? (
        <div className="space-y-4">
          <GlassPanel className="space-y-3 p-5">
            <h2 className="text-sm text-[var(--gold-soft)]">Career goal</h2>
            <Input label="Title" value={goalTitle} onChange={(e) => setGoalTitle(e.target.value)} />
            <textarea
              className="min-h-[90px] w-full rounded-xl border border-[rgba(212,175,55,0.22)] bg-[rgba(0,0,0,0.28)] px-3 py-2 text-sm outline-none"
              placeholder="Describe the path you are walking…"
              value={goalDesc}
              onChange={(e) => setGoalDesc(e.target.value)}
            />
            <Button
              loading={busy}
              disabled={!goalTitle.trim() || !goalDesc.trim()}
              onClick={() =>
                void run(async () => {
                  await createGoal({ title: goalTitle, description: goalDesc });
                  setGoalTitle("");
                  setGoalDesc("");
                })
              }
            >
              Remember goal
            </Button>
          </GlassPanel>
          <GlassPanel className="space-y-2 p-5">
            {goals.map((g) => (
              <div key={g.id} className="rounded-xl bg-[rgba(0,0,0,0.2)] px-3 py-2">
                <p className="text-sm text-[var(--ink)]">{g.title}</p>
                <p className="text-xs text-[var(--ink-muted)]">{g.description}</p>
                <p className="mt-1 text-[11px] uppercase text-[var(--gold-dim)]">{g.status}</p>
              </div>
            ))}
          </GlassPanel>
        </div>
      ) : null}

      {tab === "journals" ? (
        <div className="space-y-4">
          <GlassPanel className="space-y-3 p-5">
            <h2 className="text-sm text-[var(--gold-soft)]">Journal entry</h2>
            <Input
              label="Title"
              value={journalTitle}
              onChange={(e) => setJournalTitle(e.target.value)}
            />
            <Input
              label="Mood note"
              value={journalMood}
              onChange={(e) => setJournalMood(e.target.value)}
            />
            <textarea
              className="min-h-[110px] w-full rounded-xl border border-[rgba(212,175,55,0.22)] bg-[rgba(0,0,0,0.28)] px-3 py-2 text-sm outline-none"
              value={journalContent}
              onChange={(e) => setJournalContent(e.target.value)}
            />
            <Button
              loading={busy}
              disabled={!journalContent.trim()}
              onClick={() =>
                void run(async () => {
                  await createJournal({
                    title: journalTitle || undefined,
                    mood_note: journalMood || undefined,
                    content: journalContent,
                  });
                  setJournalTitle("");
                  setJournalMood("");
                  setJournalContent("");
                })
              }
            >
              Save journal
            </Button>
          </GlassPanel>

          <GlassPanel className="space-y-3 p-5">
            <h2 className="text-sm text-[var(--gold-soft)]">Reflection</h2>
            <label className="text-sm text-[var(--ink-muted)]">
              Journal
              <select
                className="mt-1 w-full rounded-xl border border-[rgba(212,175,55,0.22)] bg-[rgba(0,0,0,0.28)] px-3 py-2 text-sm"
                value={reflectionJournalId}
                onChange={(e) => setReflectionJournalId(e.target.value)}
              >
                {journals.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title || j.id.slice(0, 8)}
                  </option>
                ))}
              </select>
            </label>
            <textarea
              className="min-h-[90px] w-full rounded-xl border border-[rgba(212,175,55,0.22)] bg-[rgba(0,0,0,0.28)] px-3 py-2 text-sm outline-none"
              value={reflectionContent}
              onChange={(e) => setReflectionContent(e.target.value)}
            />
            <Button
              loading={busy}
              disabled={!reflectionJournalId || !reflectionContent.trim()}
              onClick={() =>
                void run(async () => {
                  await createReflection({
                    journal_id: reflectionJournalId,
                    content: reflectionContent,
                  });
                  setReflectionContent("");
                })
              }
            >
              Save reflection
            </Button>
          </GlassPanel>

          <GlassPanel className="space-y-2 p-5">
            <h2 className="text-sm text-[var(--gold-soft)]">Recent journals</h2>
            {journals.map((j) => (
              <div key={j.id} className="rounded-xl bg-[rgba(0,0,0,0.2)] px-3 py-2">
                <p className="text-sm">{j.title || "Untitled"}</p>
                <p className="line-clamp-2 text-xs text-[var(--ink-muted)]">{j.content}</p>
              </div>
            ))}
            <h2 className="pt-2 text-sm text-[var(--gold-soft)]">Reflections</h2>
            {reflections.map((r) => (
              <div key={r.id} className="rounded-xl bg-[rgba(0,0,0,0.2)] px-3 py-2 text-xs text-[var(--ink-muted)]">
                {r.content}
              </div>
            ))}
          </GlassPanel>
        </div>
      ) : null}

      {tab === "favorites" ? (
        <GlassPanel className="space-y-3 p-5">
          <p className="text-sm text-[var(--ink-muted)]">
            Favorite verses are saved from chat citations (coming soon from verse cards).
            Existing favorites:
          </p>
          {favorites.length === 0 ? (
            <p className="text-sm text-[var(--ink-faint)]">No favorites yet.</p>
          ) : (
            favorites.map((f) => (
              <div key={f.id} className="rounded-xl bg-[rgba(0,0,0,0.2)] px-3 py-2">
                <p className="text-sm text-[var(--gold-soft)]">{f.citation}</p>
                <p className="text-xs text-[var(--ink-muted)]">{f.translation}</p>
                {f.note ? <p className="mt-1 text-xs italic">{f.note}</p> : null}
              </div>
            ))
          )}
        </GlassPanel>
      ) : null}

      {tab === "recall" ? (
        <GlassPanel className="space-y-3 p-5">
          <h2 className="text-sm text-[var(--gold-soft)]">Semantic recall</h2>
          <Input
            label="Query"
            value={recallQuery}
            onChange={(e) => setRecallQuery(e.target.value)}
            placeholder="What am I struggling with at work?"
          />
          <Button
            loading={busy}
            disabled={!recallQuery.trim()}
            onClick={() =>
              void run(async () => {
                const hits = await recallMemories(recallQuery);
                setRecallHits(hits);
              })
            }
          >
            Search vector memory
          </Button>
          <ul className="space-y-2">
            {recallHits.map((h, i) => (
              <li key={`${h.kind}-${i}`} className="rounded-xl bg-[rgba(0,0,0,0.2)] px-3 py-2">
                <p className="text-xs uppercase text-[var(--gold-dim)]">
                  {h.kind} · score {h.score.toFixed(3)}
                </p>
                <p className="text-sm">{h.title}</p>
                <p className="text-xs text-[var(--ink-muted)]">{h.content}</p>
              </li>
            ))}
          </ul>
        </GlassPanel>
      ) : null}
    </AppPageShell>
  );
}
