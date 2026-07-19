import { apiRequest } from "@/lib/api/client";
import type { ChatAskResponse } from "@/lib/types/api";

export async function askSarathi(input: {
  message: string;
  conversation_id?: string | null;
  top_k?: number;
  signal?: AbortSignal;
}): Promise<ChatAskResponse> {
  return apiRequest<ChatAskResponse>("/chat/ask", {
    method: "POST",
    auth: true,
    signal: input.signal,
    body: {
      message: input.message,
      conversation_id: input.conversation_id ?? null,
      top_k: input.top_k ?? 5,
    },
  });
}
