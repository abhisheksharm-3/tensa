import type { Job } from "@/types/job";

const MAX_TITLE_LENGTH = 60;

/** Build a fresh pending Job for the live job list from a submitted source. */
export function createPendingJob(
  jobId: string,
  type: string,
  title: string,
): Job {
  return {
    id: jobId,
    type,
    title,
    status: "pending",
    percent: 0,
    speed: "—",
    eta: "—",
    downloadUrl: null,
    fileSize: null,
    error: null,
    addedAt: Date.now(),
  };
}

/** Derive a display title from a filename or URL, truncating long URLs. */
export function deriveJobTitle(file: File | null, url: string): string {
  if (file) return file.name;
  return url.length > MAX_TITLE_LENGTH
    ? `${url.slice(0, MAX_TITLE_LENGTH - 3)}…`
    : url;
}
