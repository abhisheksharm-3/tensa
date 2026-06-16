import "server-only";

/**
 * Server-only HTTP client for the FastAPI backend.
 *
 * This module is the single egress point from the Next.js server to the API.
 * It is imported exclusively by Server Actions (`lib/actions/*`); components and
 * client hooks never import it. The only client→backend path that bypasses this
 * is the SSE progress stream (see `hooks/useSSE.ts`), which a Server Action
 * cannot proxy.
 *
 * `INTERNAL_API_URL` lets the Next server reach the API over the private Docker
 * network (e.g. http://api:8000) while the browser uses NEXT_PUBLIC_API_URL.
 */
const INTERNAL_API_URL =
  process.env.INTERNAL_API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export interface ApiError {
  status: number;
  detail: string;
}

export class ApiRequestError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor({ status, detail }: ApiError) {
    super(detail);
    this.name = "ApiRequestError";
    this.status = status;
    this.detail = detail;
  }
}

async function toError(res: Response): Promise<ApiRequestError> {
  const fallback = res.statusText || "Request failed";
  const detail = await res
    .json()
    .then((body) => (typeof body?.detail === "string" ? body.detail : fallback))
    .catch(() => fallback);
  return new ApiRequestError({ status: res.status, detail });
}

interface RequestOptions {
  method?: "GET" | "POST" | "DELETE";
  body?: unknown;
  signal?: AbortSignal;
}

export async function apiRequest<T>(
  path: string,
  { method = "GET", body, signal }: RequestOptions = {},
): Promise<T> {
  const res = await fetch(`${INTERNAL_API_URL}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    signal,
    cache: "no-store",
  });

  if (!res.ok) throw await toError(res);
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

/** Forward a multipart upload (FormData) to the API, preserving the stream. */
export async function apiUpload<T>(path: string, form: FormData): Promise<T> {
  const res = await fetch(`${INTERNAL_API_URL}${path}`, {
    method: "POST",
    body: form,
    cache: "no-store",
  });
  if (!res.ok) throw await toError(res);
  return res.json() as Promise<T>;
}
