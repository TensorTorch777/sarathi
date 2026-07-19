import { ApiError, type ApiErrorBody } from "@/lib/types/api";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000/api/v1";

type TokenGetter = () => string | null;
type TokenRefresher = () => Promise<string | null>;

let getAccessToken: TokenGetter = () => null;
let refreshAccessToken: TokenRefresher = async () => null;

/** Wire auth store callbacks into the HTTP client (called once from providers). */
export function configureApiAuth(options: {
  getAccessToken: TokenGetter;
  refreshAccessToken: TokenRefresher;
}): void {
  getAccessToken = options.getAccessToken;
  refreshAccessToken = options.refreshAccessToken;
}

export interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  auth?: boolean;
  signal?: AbortSignal;
  /** Skip the automatic refresh+retry cycle. */
  skipRefresh?: boolean;
}

async function parseError(response: Response): Promise<ApiError> {
  let code = "http_error";
  let message = response.statusText || "Request failed";
  let details: unknown;

  try {
    const data = (await response.json()) as ApiErrorBody;
    if (data?.error) {
      code = data.error.code ?? code;
      message = data.error.message ?? message;
      details = data.error.details;
    }
  } catch {
    // Non-JSON error body — keep defaults.
  }

  return new ApiError(response.status, code, message, details);
}

/** Typed fetch against the Sarathi API with optional bearer auth + refresh. */
export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body, auth = false, signal, skipRefresh = false } = options;
  const headers: Record<string, string> = {
    Accept: "application/json",
  };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (auth) {
    const token = getAccessToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    signal,
  });

  if (response.status === 401 && auth && !skipRefresh) {
    const next = await refreshAccessToken();
    if (next) {
      return apiRequest<T>(path, { ...options, skipRefresh: true });
    }
  }

  if (!response.ok) {
    throw await parseError(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function getApiBaseUrl(): string {
  return API_BASE;
}
