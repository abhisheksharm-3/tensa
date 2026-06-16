"use server";

import { ApiRequestError, apiRequest } from "@/lib/api-client";
import type { JobStatusResponse, JobSubmitPayload } from "@/types/job";

/**
 * Server Actions for job lifecycle. These are the only code paths that reach the
 * FastAPI backend for job operations; client hooks (React Query) call these, and
 * components call the hooks. Live progress is the sole exception — it streams
 * directly over SSE (see `hooks/useSSE.ts`), since a stream cannot be proxied
 * through a Server Action.
 */

function rethrow(error: unknown): never {
  // Surface a clean, serializable message across the RSC boundary.
  if (error instanceof ApiRequestError) throw new Error(error.detail);
  throw error instanceof Error ? error : new Error("Request failed");
}

export async function submitJobAction(
  payload: JobSubmitPayload,
): Promise<{ jobId: string }> {
  try {
    const { job_id } = await apiRequest<{ job_id: string }>("/api/jobs", {
      method: "POST",
      body: payload,
    });
    return { jobId: job_id };
  } catch (error) {
    rethrow(error);
  }
}

export async function cancelJobAction(jobId: string): Promise<void> {
  try {
    await apiRequest<void>(`/api/jobs/${jobId}`, { method: "DELETE" });
  } catch (error) {
    rethrow(error);
  }
}

export async function getJobStatusAction(
  jobId: string,
): Promise<JobStatusResponse | null> {
  try {
    return await apiRequest<JobStatusResponse>(`/api/jobs/${jobId}`);
  } catch (error) {
    // A 404 means the job/status has expired out of the store — treat as gone
    // rather than an error so stale persisted jobs reconcile cleanly.
    if (error instanceof ApiRequestError && error.status === 404) return null;
    rethrow(error);
  }
}
