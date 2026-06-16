import { API_BASE } from "@/constants/api";

/**
 * Browser-side URLs that point straight at the FastAPI backend. These are the
 * sanctioned exceptions to the "UI → React Query → Server Action → backend" rule:
 *
 *  - the SSE progress stream: an `EventSource` connection can't be proxied
 *    through a Server Action;
 *  - file serving/download: streaming a (potentially multi-GB) FileResponse back
 *    through the Next server would be wasteful, so the browser links directly.
 *
 * Everything else (submit, cancel, status reconciliation, playlist, upload) goes
 * through Server Actions.
 */

export function jobStreamUrl(jobId: string): string {
  return `${API_BASE}/api/jobs/${jobId}/stream`;
}

export function fileDownloadUrl(downloadPath: string): string {
  return `${API_BASE}${downloadPath}`;
}
