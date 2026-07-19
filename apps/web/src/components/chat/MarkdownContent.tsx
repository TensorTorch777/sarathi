"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { cn } from "@/lib/utils/cn";

export function MarkdownContent({
  content,
  streaming = false,
  className,
}: {
  content: string;
  streaming?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("prose-sarathi", streaming && "stream-caret", className)}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}
