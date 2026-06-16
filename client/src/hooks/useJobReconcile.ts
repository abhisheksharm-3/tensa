"use client";

import { useQueries } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { getJobStatusAction } from "@/lib/actions/jobs";
import type { Job } from "@/types/job";

const NON_TERMINAL = new Set(["pending", "running"]);

/**
 * Reconcile persisted jobs that may have changed while the page was closed.
 *
 * Live jobs in the current session update via SSE, but a job that finished while
 * the tab was gone has no event to replay (pub/sub is live-only). On mount we
 * fetch the authoritative status for each non-terminal job through React Query →
 * the Server Action, and patch the list. A job whose status has expired out of
 * the store (null) is marked expired so the UI doesn't wait on it forever.
 */
export function useJobReconcile(
  jobs: Job[],
  patchJob: (id: string, patch: Partial<Job>) => void,
): void {
  const targets = jobs.filter((job) => NON_TERMINAL.has(job.status));
  const processed = useRef<Set<string>>(new Set());

  const results = useQueries({
    queries: targets.map((job) => ({
      queryKey: ["job-status", job.id],
      queryFn: () => getJobStatusAction(job.id),
      staleTime: Number.POSITIVE_INFINITY,
      gcTime: 60_000,
      retry: false,
      refetchOnWindowFocus: false,
    })),
  });

  useEffect(() => {
    results.forEach((result, index) => {
      const job = targets[index];
      if (!job || result.isPending || processed.current.has(job.id)) return;

      processed.current.add(job.id);
      const status = result.data;

      if (status === null) {
        patchJob(job.id, { status: "error", error: "File expired" });
        return;
      }
      if (!status) return; // query errored; leave the job for SSE to resolve

      if (status.status === "done") {
        patchJob(job.id, {
          status: "done",
          percent: 100,
          downloadUrl: status.download_url,
          fileSize: status.file_size,
        });
      } else if (status.status === "failed") {
        patchJob(job.id, {
          status: "error",
          error: status.message ?? "Job failed",
        });
      } else if (status.status === "cancelled") {
        patchJob(job.id, { status: "cancelled" });
      }
      // pending / running: SSE drives the live updates
    });
  }, [results, targets, patchJob]);
}
