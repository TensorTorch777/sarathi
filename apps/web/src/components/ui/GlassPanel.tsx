import { cn } from "@/lib/utils/cn";

export function GlassPanel({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return <div className={cn("glass rounded-[var(--radius-lg)]", className)}>{children}</div>;
}
