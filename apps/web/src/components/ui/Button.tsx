"use client";

import { cn } from "@/lib/utils/cn";

type Variant = "primary" | "ghost" | "danger" | "subtle";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  loading?: boolean;
}

const variants: Record<Variant, string> = {
  primary:
    "bg-gradient-to-br from-[#e6c768] via-[#d4af37] to-[#9a7a1f] text-[#1a1406] font-semibold shadow-[0_8px_24px_rgba(212,175,55,0.25)] hover:brightness-110",
  ghost:
    "bg-transparent border border-[rgba(212,175,55,0.28)] text-[var(--ink)] hover:bg-[rgba(212,175,55,0.08)]",
  subtle:
    "bg-[rgba(255,255,255,0.04)] border border-[rgba(255,255,255,0.06)] text-[var(--ink)] hover:bg-[rgba(255,255,255,0.08)]",
  danger:
    "bg-[rgba(224,122,106,0.12)] border border-[rgba(224,122,106,0.35)] text-[#f0b4aa] hover:bg-[rgba(224,122,106,0.2)]",
};

export function Button({
  className,
  variant = "primary",
  loading,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--gold)] disabled:cursor-not-allowed disabled:opacity-50",
        variants[variant],
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent" />
      ) : null}
      {children}
    </button>
  );
}
