"use client";

import { Menu } from "lucide-react";
import { useState } from "react";

import { ChatSidebar } from "@/components/chat/ChatSidebar";

export function AppPageShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

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
          <div>
            <h1 className="brand-mark text-2xl text-[var(--gold-soft)]">{title}</h1>
            {subtitle ? <p className="text-xs text-[var(--ink-faint)]">{subtitle}</p> : null}
          </div>
        </header>
        <main className="flex-1 overflow-y-auto px-4 py-6 scrollbar-thin md:px-8">
          <div className="mx-auto w-full max-w-2xl">{children}</div>
        </main>
      </div>
    </div>
  );
}
