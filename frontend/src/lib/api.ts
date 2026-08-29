/**
 * Single place where every HTTP call to the PAMS API goes through.
 *
 * Why centralise this rather than calling fetch() in each component:
 *  - the JWT has to be attached to every request, doing it in one place means
 *    no endpoint can accidentally be called without it
 *  - a 401 means the token expired, which should log the user out everywhere,
 *    not just fail one screen quietly
 *  - FastAPI returns errors as {"detail": "..."}, so unwrapping that once here
 *    means components can just catch an Error with a readable message
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const TOKEN_KEY = "pams_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/** Thrown for any non-2xx response, carrying the HTTP status so callers can
 *  tell "not found" apart from "not allowed" without parsing strings. */
export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** Called when a 401 comes back, wired up by AuthProvider at startup. */
let onUnauthorized: (() => void) | null = null;

export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler;
}

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
};

export async function request<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body } = options;

  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) {
    // The backend uses HTTPBearer, so the scheme word matters here.
    headers.Authorization = `Bearer ${token}`;
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    // fetch() only rejects on network-level failure, not on 4xx/5xx.
    throw new ApiError(0, "Can't reach the server. Check it's running.");
  }

  if (response.status === 401) {
    onUnauthorized?.();
    throw new ApiError(401, "Invalid Username or Password.");
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      // FastAPI's HTTPException puts the message in `detail`. Pydantic
      // validation errors (422) put an array there instead.
      if (typeof data.detail === "string") {
        detail = data.detail;
      } else if (Array.isArray(data.detail)) {
        detail = data.detail
          .map((d: { loc?: string[]; msg?: string }) =>
            d.loc ? `${d.loc.slice(1).join(".")}: ${d.msg}` : d.msg,
          )
          .join(", ");
      }
    } catch {
      // Response wasn't JSON, keep the generic message.
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT", body }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
