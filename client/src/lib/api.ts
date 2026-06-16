import { API_BASE } from "@/constants/api";
import type { JobSubmitPayload, PlaylistItem } from "@/types/job";

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

export async function submitJob(
  payload: JobSubmitPayload,
): Promise<{ job_id: string }> {
  return apiPost("/api/jobs", payload);
}

export async function cancelJob(jobId: string): Promise<void> {
  await fetch(`${API_BASE}/api/jobs/${jobId}`, { method: "DELETE" });
}

export async function fetchPlaylistInfo(
  url: string,
): Promise<{ items: PlaylistItem[]; total: number }> {
  return apiPost("/api/playlist/info", { url });
}

export async function uploadFile(file: File): Promise<{ upload_path: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export function jobStreamUrl(jobId: string): string {
  return `${API_BASE}/api/jobs/${jobId}/stream`;
}

export function jobStatusUrl(jobId: string): string {
  return `${API_BASE}/api/jobs/${jobId}`;
}
