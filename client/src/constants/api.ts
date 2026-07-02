declare global {
  interface Window {
    __TENSA_API_BASE__?: string;
  }
}

/**
 * Browser-facing absolute API base. Resolved at call time (never inlined at
 * build) so the same build works on any deploy: the server injects the runtime
 * value onto `window.__TENSA_API_BASE__` (see `app/layout.tsx`), and the server
 * itself reads `PUBLIC_API_URL` directly.
 */
export function getApiBase(): string {
  if (typeof window !== "undefined" && window.__TENSA_API_BASE__) {
    return window.__TENSA_API_BASE__;
  }
  return process.env.PUBLIC_API_URL ?? "http://localhost:8000";
}
