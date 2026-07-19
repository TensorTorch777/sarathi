/** Shared API types mirroring the FastAPI schemas. */

export type UserRole = "user" | "admin";

export interface User {
  id: string;
  email: string;
  display_name: string | null;
  role: UserRole;
  locale: string | null;
  is_active: boolean;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: "bearer" | string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: TokenPair;
}

export interface AnswerCitation {
  citation: string;
  chapter: number;
  verse_number: number;
  verse_id: string;
  translation: string;
}

export interface RetrievedVerse {
  verse_id: string;
  citation: string;
  chapter: number;
  verse_number: number;
  sanskrit: string;
  translation: string;
  transliteration: string | null;
  topics: string[];
  emotions: string[];
  bm25_score: number;
  dense_score: number;
  rrf_score: number;
  rerank_score: number;
  compressed_context: string;
  verified: boolean;
}

export interface ChatAskResponse {
  answer: string;
  emotions: string[];
  topics: string[];
  rewritten_query: string;
  citations: AnswerCitation[];
  verses: RetrievedVerse[];
  stages: Record<string, unknown>;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details?: unknown;

  constructor(status: number, code: string, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}
