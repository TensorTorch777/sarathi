"use client";

import { ArrowUp } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils/cn";

export function Composer({
  disabled,
  onSend,
}: {
  disabled?: boolean;
  onSend: (message: string) => void;
}) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }, [value]);

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  return (
    <form
      className="glass mx-auto w-full max-w-3xl rounded-2xl p-2 shadow-[0_16px_48px_rgba(0,0,0,0.35)]"
      onSubmit={(event) => {
        event.preventDefault();
        submit();
      }}
    >
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          disabled={disabled}
          placeholder="Ask Sarathi about duty, fear, grief, purpose…"
          className={cn(
            "max-h-[180px] min-h-[48px] flex-1 resize-none bg-transparent px-3 py-3 text-[15px] text-[var(--ink)] outline-none placeholder:text-[var(--ink-faint)] disabled:opacity-60",
          )}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              submit();
            }
          }}
        />
        <Button
          type="submit"
          disabled={disabled || !value.trim()}
          className="mb-1 mr-1 h-11 w-11 shrink-0 rounded-xl px-0"
          aria-label="Send message"
        >
          <ArrowUp className="h-5 w-5" />
        </Button>
      </div>
      <p className="px-3 pb-1.5 text-[11px] text-[var(--ink-faint)]">
        Grounded in the Bhagavad Gita · Enter to send · Shift+Enter for a new line
      </p>
    </form>
  );
}
