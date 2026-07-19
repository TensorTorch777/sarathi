"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { AnswerCitation, RetrievedVerse } from "@/lib/types/api";

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  emotions?: string[];
  topics?: string[];
  citations?: AnswerCitation[];
  verses?: RetrievedVerse[];
  rewrittenQuery?: string;
  /** True while the assistant answer is being progressively revealed. */
  streaming?: boolean;
  error?: string;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messages: ChatMessage[];
}

interface ConversationState {
  conversations: Conversation[];
  activeId: string | null;
  createConversation: () => string;
  setActive: (id: string | null) => void;
  deleteConversation: (id: string) => void;
  renameConversation: (id: string, title: string) => void;
  appendMessage: (conversationId: string, message: ChatMessage) => void;
  updateMessage: (
    conversationId: string,
    messageId: string,
    patch: Partial<ChatMessage>,
  ) => void;
  getActive: () => Conversation | null;
}

function nowIso(): string {
  return new Date().toISOString();
}

function makeId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function titleFromMessage(text: string): string {
  const cleaned = text.replace(/\s+/g, " ").trim();
  if (!cleaned) return "New conversation";
  return cleaned.length > 48 ? `${cleaned.slice(0, 48)}…` : cleaned;
}

export const useConversationStore = create<ConversationState>()(
  persist(
    (set, get) => ({
      conversations: [],
      activeId: null,

      createConversation: () => {
        const id = makeId();
        const stamp = nowIso();
        const conversation: Conversation = {
          id,
          title: "New conversation",
          createdAt: stamp,
          updatedAt: stamp,
          messages: [],
        };
        set((state) => ({
          conversations: [conversation, ...state.conversations],
          activeId: id,
        }));
        return id;
      },

      setActive: (id) => set({ activeId: id }),

      deleteConversation: (id) =>
        set((state) => {
          const next = state.conversations.filter((c) => c.id !== id);
          const activeId =
            state.activeId === id ? (next[0]?.id ?? null) : state.activeId;
          return { conversations: next, activeId };
        }),

      renameConversation: (id, title) =>
        set((state) => ({
          conversations: state.conversations.map((c) =>
            c.id === id ? { ...c, title, updatedAt: nowIso() } : c,
          ),
        })),

      appendMessage: (conversationId, message) =>
        set((state) => ({
          conversations: state.conversations.map((c) => {
            if (c.id !== conversationId) return c;
            const isFirstUser =
              message.role === "user" &&
              c.messages.every((m) => m.role !== "user");
            return {
              ...c,
              title: isFirstUser ? titleFromMessage(message.content) : c.title,
              updatedAt: nowIso(),
              messages: [...c.messages, message],
            };
          }),
        })),

      updateMessage: (conversationId, messageId, patch) =>
        set((state) => ({
          conversations: state.conversations.map((c) => {
            if (c.id !== conversationId) return c;
            return {
              ...c,
              updatedAt: nowIso(),
              messages: c.messages.map((m) =>
                m.id === messageId ? { ...m, ...patch } : m,
              ),
            };
          }),
        })),

      getActive: () => {
        const { conversations, activeId } = get();
        return conversations.find((c) => c.id === activeId) ?? null;
      },
    }),
    {
      name: "sarathi-conversations",
      partialize: (state) => ({
        conversations: state.conversations,
        activeId: state.activeId,
      }),
    },
  ),
);

export { makeId };
