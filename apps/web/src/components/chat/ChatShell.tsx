"use client";

import { Menu } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { Composer } from "@/components/chat/Composer";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { VoiceMode } from "@/components/chat/VoiceMode";
import { askSarathi } from "@/lib/api/chat";
import { saveConversationSummary } from "@/lib/api/memory";
import { ApiError } from "@/lib/types/api";
import {
  makeId,
  useConversationStore,
} from "@/lib/stores/conversation-store";
import type { VoiceDonePayload } from "@/lib/voice/session";

export function ChatShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const conversations = useConversationStore((s) => s.conversations);
  const activeId = useConversationStore((s) => s.activeId);
  const createConversation = useConversationStore((s) => s.createConversation);
  const appendMessage = useConversationStore((s) => s.appendMessage);
  const updateMessage = useConversationStore((s) => s.updateMessage);

  const active = useMemo(
    () => conversations.find((c) => c.id === activeId) ?? null,
    [conversations, activeId],
  );

  useEffect(() => {
    if (!activeId && conversations.length === 0) {
      createConversation();
    }
  }, [activeId, conversations.length, createConversation]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [active?.messages, pending]);

  const finishStream = useCallback(
    (messageId: string) => {
      if (!activeId) return;
      updateMessage(activeId, messageId, { streaming: false });
    },
    [activeId, updateMessage],
  );

  const handleSend = async (text: string) => {
    let conversationId = activeId;
    if (!conversationId) {
      conversationId = createConversation();
    }

    const userMessage = {
      id: makeId(),
      role: "user" as const,
      content: text,
      createdAt: new Date().toISOString(),
    };
    appendMessage(conversationId, userMessage);
    setPending(true);

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const assistantId = makeId();

    try {
      const response = await askSarathi({
        message: text,
        conversation_id: conversationId,
        signal: controller.signal,
      });

      appendMessage(conversationId, {
        id: assistantId,
        role: "assistant",
        content: response.answer,
        createdAt: new Date().toISOString(),
        emotions: response.emotions,
        topics: response.topics,
        citations: response.citations,
        verses: response.verses,
        rewrittenQuery: response.rewritten_query,
        streaming: true,
      });

      // Persist a short conversation summary into long-term vector memory.
      const conv = useConversationStore
        .getState()
        .conversations.find((c) => c.id === conversationId);
      void saveConversationSummary({
        conversation_id: conversationId,
        title: conv?.title || "Conversation",
        summary: `User asked about: ${text}\nSarathi taught from ${
          response.citations.map((c) => c.citation).join(", ") || "retrieved verses"
        }. Emotions: ${response.emotions.join(", ") || "n/a"}.`,
        messages_preview: [text, response.answer.slice(0, 280)],
      }).catch(() => {
        // Non-blocking — chat should still succeed if memory write fails.
      });
    } catch (error) {
      if (controller.signal.aborted) return;
      const message =
        error instanceof ApiError
          ? error.message
          : error instanceof Error
            ? error.message
            : "Something went wrong while asking Sarathi.";
      appendMessage(conversationId, {
        id: assistantId,
        role: "assistant",
        content: "",
        createdAt: new Date().toISOString(),
        error: message,
        streaming: false,
      });
    } finally {
      setPending(false);
    }
  };

  const handleVoiceTranscript = useCallback(
    (text: string) => {
      if (!text.trim()) return;
      let conversationId = activeId;
      if (!conversationId) {
        conversationId = createConversation();
      }
      appendMessage(conversationId, {
        id: makeId(),
        role: "user",
        content: text.trim(),
        createdAt: new Date().toISOString(),
      });
    },
    [activeId, appendMessage, createConversation],
  );

  const handleVoiceDone = useCallback(
    (payload: VoiceDonePayload) => {
      let conversationId = activeId;
      if (!conversationId) {
        conversationId = createConversation();
      }
      appendMessage(conversationId, {
        id: makeId(),
        role: "assistant",
        content: payload.answer,
        createdAt: new Date().toISOString(),
        emotions: payload.emotions,
        topics: payload.topics,
        citations: payload.citations,
        verses: payload.verses.map((v) => ({
          verse_id: v.verse_id,
          citation: v.citation,
          chapter: v.chapter,
          verse_number: v.verse_number,
          sanskrit: v.sanskrit,
          translation: v.translation,
          transliteration: v.transliteration,
          topics: v.topics,
          emotions: v.emotions,
          bm25_score: 0,
          dense_score: 0,
          rrf_score: 0,
          rerank_score: 0,
          compressed_context: v.translation,
          verified: v.verified,
        })),
        streaming: true,
      });
    },
    [activeId, appendMessage, createConversation],
  );

  return (
    <div className="flex h-[100dvh] overflow-hidden">
      <ChatSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-[rgba(212,175,55,0.12)] px-4 py-3 md:px-6">
          <button
            type="button"
            className="rounded-lg p-2 text-[var(--ink-muted)] hover:bg-[rgba(255,255,255,0.05)] md:hidden"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open sidebar"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="min-w-0">
            <p className="brand-mark truncate text-xl text-[var(--gold-soft)]">
              {active?.title || "New conversation"}
            </p>
            <p className="text-xs text-[var(--ink-faint)]">
              An AI guide grounded in the Bhagavad Gita — not Krishna
            </p>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-4 py-6 scrollbar-thin md:px-8">
          <div className="mx-auto flex w-full max-w-3xl flex-col gap-5">
            {!active?.messages.length && !pending ? (
              <EmptyState onPickPrompt={handleSend} disabled={pending} />
            ) : (
              active?.messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  onStreamComplete={finishStream}
                />
              ))
            )}
            {pending ? <TypingIndicator /> : null}
            <div ref={bottomRef} />
          </div>
        </main>

        <div className="border-t border-[rgba(212,175,55,0.1)] px-4 py-4 md:px-8">
          <Composer disabled={pending} onSend={handleSend} />
          <VoiceMode
            conversationId={activeId}
            onTranscript={handleVoiceTranscript}
            onDone={handleVoiceDone}
          />
        </div>
      </div>
    </div>
  );
}

function EmptyState({
  onPickPrompt,
  disabled,
}: {
  onPickPrompt: (prompt: string) => void;
  disabled?: boolean;
}) {
  return (
    <div className="animate-fade-up flex min-h-[50vh] flex-col items-center justify-center text-center">
      <p className="brand-mark text-5xl gold-text sm:text-6xl">Sarathi</p>
      <p className="mt-4 max-w-md text-base text-[var(--ink-muted)]">
        Ask about duty, fear, attachment, or purpose. Answers cite real chapter and verse —
        never invented.
      </p>
      <div className="mt-8 grid w-full max-w-lg gap-2 sm:grid-cols-2">
        {[
          "I feel anxious about my responsibilities.",
          "How does the Gita speak about attachment?",
          "What is nishkama karma in daily life?",
          "I am grieving a loss. What can I learn?",
        ].map((prompt) => (
          <button
            key={prompt}
            type="button"
            disabled={disabled}
            className="glass rounded-xl px-3 py-3 text-left text-sm text-[var(--ink-muted)] transition hover:border-[rgba(212,175,55,0.35)] hover:text-[var(--ink)] disabled:opacity-50"
            onClick={() => onPickPrompt(prompt)}
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}
