"use client";

import { cn } from "@/lib/utils/cn";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ className, label, error, id, ...props }: InputProps) {
  const inputId = id ?? props.name;
  return (
    <label className="flex w-full flex-col gap-1.5 text-sm">
      {label ? (
        <span className="text-[var(--ink-muted)]">{label}</span>
      ) : null}
      <input
        id={inputId}
        className={cn(
          "w-full rounded-xl border border-[rgba(212,175,55,0.22)] bg-[rgba(0,0,0,0.28)] px-3.5 py-2.5 text-[var(--ink)] outline-none transition placeholder:text-[var(--ink-faint)] focus:border-[var(--gold)] focus:shadow-[0_0_0_3px_rgba(212,175,55,0.15)]",
          error && "border-[rgba(224,122,106,0.55)]",
          className,
        )}
        {...props}
      />
      {error ? <span className="text-xs text-[var(--danger)]">{error}</span> : null}
    </label>
  );
}
