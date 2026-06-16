"use client";

import { useCallback, useEffect, useRef } from "react";
import {
  MAX_SSE_RETRIES,
  POLL_INTERVAL_MS,
  TERMINAL_EVENT_TYPES,
} from "@/constants/sse";
import { getJobStatusAction } from "@/lib/actions/jobs";
import { jobStreamUrl } from "@/lib/stream";
import type { SSEEvent, SSEHandler } from "@/types/job";

/**
 * Subscribe to a job's SSE progress stream with exponential-backoff reconnect.
 * The stream itself is a direct browser→API `EventSource` (the sanctioned
 * streaming exception). After MAX_SSE_RETRIES failed connections it falls back
 * to polling status through the `getJobStatusAction` Server Action. Pass a null
 * jobId to stay disconnected.
 */
export function useSSE(jobId: string | null, onEvent: SSEHandler): void {
  const esRef = useRef<EventSource | null>(null);
  const retriesRef = useRef(0);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const startPolling = useCallback(
    (id: string) => {
      if (pollRef.current) return;
      pollRef.current = setInterval(async () => {
        try {
          const data = await getJobStatusAction(id);
          if (!data) {
            onEventRef.current({ type: "error", message: "File expired" });
            stopPolling();
            return;
          }
          if (data.status === "done") {
            onEventRef.current({
              type: "done",
              download_url: data.download_url ?? "",
              size: data.file_size ?? 0,
            });
            stopPolling();
          } else if (data.status === "failed") {
            onEventRef.current({
              type: "error",
              message: data.message ?? "Unknown error",
            });
            stopPolling();
          }
        } catch {
          // transient error — keep polling on the next tick
        }
      }, POLL_INTERVAL_MS);
    },
    [stopPolling],
  );

  useEffect(() => {
    if (!jobId) return;
    retriesRef.current = 0;

    const connect = (): void => {
      const es = new EventSource(jobStreamUrl(jobId));
      esRef.current = es;

      es.onmessage = (event: MessageEvent) => {
        try {
          const parsed = JSON.parse(event.data as string) as SSEEvent;
          onEventRef.current(parsed);
          if (TERMINAL_EVENT_TYPES.has(parsed.type)) {
            es.close();
            stopPolling();
          }
        } catch {
          // malformed payload — ignore this message
        }
      };

      es.onerror = () => {
        es.close();
        retriesRef.current += 1;
        if (retriesRef.current >= MAX_SSE_RETRIES) {
          startPolling(jobId);
        } else {
          setTimeout(connect, 1000 * 2 ** retriesRef.current);
        }
      };
    };

    connect();
    return () => {
      esRef.current?.close();
      stopPolling();
    };
  }, [jobId, startPolling, stopPolling]);
}
