"use client";

import { useMutation } from "@tanstack/react-query";
import { cancelJobAction, submitJobAction } from "@/lib/actions/jobs";
import { fetchMetadataAction } from "@/lib/actions/metadata";
import { fetchPlaylistInfoAction } from "@/lib/actions/playlist";
import { uploadFileAction } from "@/lib/actions/upload";
import type { JobSubmitPayload } from "@/types/job";

/**
 * React Query hooks over the job Server Actions. This is the only layer
 * components use to mutate backend state — components never call the actions
 * (or fetch) directly. Live progress is the lone exception and goes over SSE.
 */

export function useSubmitJob() {
  return useMutation({
    mutationFn: (payload: JobSubmitPayload) => submitJobAction(payload),
  });
}

export function useCancelJob() {
  return useMutation({
    mutationFn: (jobId: string) => cancelJobAction(jobId),
  });
}

export function usePlaylistInfo() {
  return useMutation({
    mutationFn: (url: string) => fetchPlaylistInfoAction(url),
  });
}

export function useMetadata() {
  return useMutation({
    mutationFn: (url: string) => fetchMetadataAction(url),
  });
}

export function useUploadFile() {
  return useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return uploadFileAction(form);
    },
  });
}
