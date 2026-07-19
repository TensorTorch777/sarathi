"use client";

import {
  Brain,
  MessageSquarePlus,
  Settings,
  Trash2,
  UserRound,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { Button } from "@/components/ui/Button";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { cn } from "@/lib/utils/cn";

export function ChatSidebar({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const conversations = useConversationStore((s) => s.conversations);
  const activeId = useConversationStore((s) => s.activeId);
  const createConversation = useConversationStore((s) => s.createConversation);
  const setActive = useConversationStore((s) => s.setActive);
  const deleteConversation = useConversationStore((s) => s.deleteConversation);

  return (
    <>
      <div
        className={cn(
          "fixed inset-0 z-40 bg-black/50 transition md:hidden",
          open ? "opacity-100" : "pointer-events-none opacity-0",
        )}
        onClick={onClose}
      />

      <aside
        className={cn(
          "glass fixed inset-y-0 left-0 z-50 flex w-[288px] flex-col border-r border-[rgba(212,175,55,0.14)] transition-transform md:static md:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex items-center justify-between px-4 py-4">
          <Link href="/chat" className="brand-mark text-2xl gold-text" onClick={onClose}>
            Sarathi
          </Link>
          <button
            type="button"
            className="rounded-lg p-1.5 text-[var(--ink-muted)] hover:bg-[rgba(255,255,255,0.05)] md:hidden"
            onClick={onClose}
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="px-3">
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={() => {
              createConversation();
              onClose();
            }}
          >
            <MessageSquarePlus className="h-4 w-4" />
            New chat
          </Button>
        </div>

        <div className="mt-4 flex-1 overflow-y-auto px-2 scrollbar-thin">
          <p className="px-2 pb-2 text-[11px] uppercase tracking-[0.18em] text-[var(--ink-faint)]">
            History
          </p>
          <ul className="space-y-1 pb-4">
            {conversations.length === 0 ? (
              <li className="px-2 py-3 text-sm text-[var(--ink-faint)]">
                Your conversations will appear here.
              </li>
            ) : (
              conversations.map((conversation) => (
                <li key={conversation.id}>
                  <div
                    className={cn(
                      "group flex items-center gap-1 rounded-xl px-2 py-2 transition",
                      activeId === conversation.id
                        ? "bg-[rgba(212,175,55,0.12)]"
                        : "hover:bg-[rgba(255,255,255,0.04)]",
                    )}
                  >
                    <button
                      type="button"
                      className="min-w-0 flex-1 truncate text-left text-sm text-[var(--ink)]"
                      onClick={() => {
                        setActive(conversation.id);
                        onClose();
                      }}
                    >
                      {conversation.title}
                    </button>
                    <button
                      type="button"
                      className="rounded-md p-1 text-[var(--ink-faint)] opacity-0 transition hover:text-[var(--danger)] group-hover:opacity-100"
                      aria-label="Delete conversation"
                      onClick={() => deleteConversation(conversation.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>

        <div className="space-y-1 border-t border-[rgba(212,175,55,0.12)] p-3">
          <NavLink href="/memory" active={pathname.startsWith("/memory")} onNavigate={onClose}>
            <Brain className="h-4 w-4" />
            Memory
          </NavLink>
          <NavLink href="/profile" active={pathname.startsWith("/profile")} onNavigate={onClose}>
            <UserRound className="h-4 w-4" />
            Profile
          </NavLink>
          <NavLink href="/settings" active={pathname.startsWith("/settings")} onNavigate={onClose}>
            <Settings className="h-4 w-4" />
            Settings
          </NavLink>
          <div className="rounded-xl bg-[rgba(0,0,0,0.2)] px-3 py-2">
            <p className="truncate text-sm text-[var(--ink)]">
              {user?.display_name || user?.email || "Guest"}
            </p>
            <p className="truncate text-xs text-[var(--ink-faint)]">{user?.email}</p>
          </div>
          <Button
            variant="subtle"
            className="w-full"
            onClick={async () => {
              await logout();
              onClose();
              window.location.href = "/login";
            }}
          >
            Sign out
          </Button>
        </div>
      </aside>
    </>
  );
}

function NavLink({
  href,
  active,
  children,
  onNavigate,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
  onNavigate: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onNavigate}
      className={cn(
        "flex items-center gap-2 rounded-xl px-3 py-2 text-sm transition",
        active
          ? "bg-[rgba(212,175,55,0.12)] text-[var(--gold-soft)]"
          : "text-[var(--ink-muted)] hover:bg-[rgba(255,255,255,0.04)] hover:text-[var(--ink)]",
      )}
    >
      {children}
    </Link>
  );
}
