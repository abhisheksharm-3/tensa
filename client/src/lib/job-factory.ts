import type { Job, JobType } from "@/types/job";

const MAX_TITLE_LENGTH = 60;

/** Build a fresh pending Job for the live job list from a submitted source. */
export function createPendingJob(
  jobId: string,
  type: JobType,
  title: string,
  thumbnail: string | null = null,
): Job {
  return {
    id: jobId,
    type,
    title,
    thumbnail,
    status: "pending",
    percent: 0,
    speed: "—",
    eta: "—",
    downloadUrl: null,
    fileSize: null,
    error: null,
    addedAt: Date.now(),
    completedAt: null,
  };
}

/** Derive a display title from a filename or URL, truncating long URLs. */
export function deriveJobTitle(file: File | null, url: string): string {
  if (file) return file.name;
  return url.length > MAX_TITLE_LENGTH
    ? `${url.slice(0, MAX_TITLE_LENGTH - 3)}…`
    : url;
}
