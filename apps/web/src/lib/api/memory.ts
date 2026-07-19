import { apiRequest } from "@/lib/api/client";

export type MemoryKind =
  | "career_goal"
  | "conversation"
  | "conversation_summary"
  | "favorite_verse"
  | "journal"
  | "reflection"
  | "note";

export interface MemoryItem {
  id: string;
  kind: MemoryKind;
  title: string | null;
  content: string;
  source_id: string | null;
  metadata: Record<string, unknown>;
  created_at: string | null;
  updated_at: string | null;
}

export interface CareerGoal {
  id: string;
  title: string;
  description: string;
  status: string;
  memory_item_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface FavoriteVerse {
  id: string;
  verse_id: string;
  note: string | null;
  memory_item_id: string | null;
  citation: string | null;
  translation: string | null;
  created_at: string;
}

export interface JournalEntry {
  id: string;
  title: string | null;
  content: string;
  mood_note: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReflectionEntry {
  id: string;
  journal_id: string;
  verse_id: string | null;
  content: string;
  created_at: string;
}

export async function listMemoryItems(kind?: MemoryKind): Promise<MemoryItem[]> {
  const qs = kind ? `?kind=${kind}` : "";
  return apiRequest<MemoryItem[]>(`/memory/items${qs}`, { auth: true });
}

export async function createMemoryItem(input: {
  kind?: MemoryKind;
  title?: string;
  content: string;
}): Promise<MemoryItem> {
  return apiRequest<MemoryItem>("/memory/items", {
    method: "POST",
    auth: true,
    body: input,
  });
}

export async function deleteMemoryItem(id: string): Promise<void> {
  await apiRequest<void>(`/memory/items/${id}`, { method: "DELETE", auth: true });
}

export async function recallMemories(query: string, topK = 6) {
  return apiRequest<
    Array<{
      memory_id: string;
      kind: MemoryKind;
      title: string | null;
      content: string;
      score: number;
    }>
  >("/memory/recall", {
    method: "POST",
    auth: true,
    body: { query, top_k: topK },
  });
}

export async function listGoals(): Promise<CareerGoal[]> {
  return apiRequest<CareerGoal[]>("/memory/goals", { auth: true });
}

export async function createGoal(input: {
  title: string;
  description: string;
  status?: string;
}): Promise<CareerGoal> {
  return apiRequest<CareerGoal>("/memory/goals", {
    method: "POST",
    auth: true,
    body: { status: "active", ...input },
  });
}

export async function listFavorites(): Promise<FavoriteVerse[]> {
  return apiRequest<FavoriteVerse[]>("/memory/favorites", { auth: true });
}

export async function addFavorite(input: {
  verse_id: string;
  note?: string;
}): Promise<FavoriteVerse> {
  return apiRequest<FavoriteVerse>("/memory/favorites", {
    method: "POST",
    auth: true,
    body: input,
  });
}

export async function listJournals(): Promise<JournalEntry[]> {
  return apiRequest<JournalEntry[]>("/memory/journals", { auth: true });
}

export async function createJournal(input: {
  title?: string;
  content: string;
  mood_note?: string;
}): Promise<JournalEntry> {
  return apiRequest<JournalEntry>("/memory/journals", {
    method: "POST",
    auth: true,
    body: input,
  });
}

export async function listReflections(): Promise<ReflectionEntry[]> {
  return apiRequest<ReflectionEntry[]>("/memory/reflections", { auth: true });
}

export async function createReflection(input: {
  journal_id: string;
  content: string;
  verse_id?: string;
}): Promise<ReflectionEntry> {
  return apiRequest<ReflectionEntry>("/memory/reflections", {
    method: "POST",
    auth: true,
    body: input,
  });
}

export async function saveConversationSummary(input: {
  conversation_id?: string;
  title?: string;
  summary: string;
  messages_preview?: string[];
}): Promise<MemoryItem> {
  return apiRequest<MemoryItem>("/memory/conversations/summary", {
    method: "POST",
    auth: true,
    body: input,
  });
}
