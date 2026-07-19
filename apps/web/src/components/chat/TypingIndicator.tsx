export function TypingIndicator() {
  return (
    <div
      className="glass inline-flex items-center gap-2 rounded-2xl px-4 py-3"
      aria-live="polite"
      aria-label="Sarathi is composing a reply"
    >
      <span className="text-xs tracking-wide text-[var(--ink-muted)]">Sarathi is reflecting</span>
      <span className="flex items-center gap-1.5 pl-1">
        <span className="typing-dot h-1.5 w-1.5 rounded-full bg-[var(--gold)]" />
        <span className="typing-dot h-1.5 w-1.5 rounded-full bg-[var(--gold)]" />
        <span className="typing-dot h-1.5 w-1.5 rounded-full bg-[var(--gold)]" />
      </span>
    </div>
  );
}
