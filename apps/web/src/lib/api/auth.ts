import { apiRequest } from "@/lib/api/client";
import type { AuthResponse, TokenPair, User } from "@/lib/types/api";

export async function registerUser(input: {
  email: string;
  password: string;
  display_name?: string;
}): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/auth/register", {
    method: "POST",
    body: input,
  });
}

export async function loginUser(input: {
  email: string;
  password: string;
}): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/auth/login", {
    method: "POST",
    body: input,
  });
}

export async function refreshTokens(refreshToken: string): Promise<TokenPair> {
  return apiRequest<TokenPair>("/auth/refresh", {
    method: "POST",
    body: { refresh_token: refreshToken },
    skipRefresh: true,
  });
}

export async function logoutUser(refreshToken?: string | null): Promise<void> {
  await apiRequest<{ message: string }>("/auth/logout", {
    method: "POST",
    auth: true,
    body: refreshToken ? { refresh_token: refreshToken } : {},
    skipRefresh: true,
  });
}

export async function fetchCurrentUser(): Promise<User> {
  return apiRequest<User>("/users/me", { auth: true });
}
