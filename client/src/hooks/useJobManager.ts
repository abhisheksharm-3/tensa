"use client";

import { useCallback, useEffect, useReducer, useRef } from "react";
import { JOBS_STORAGE_KEY, MAX_PERSISTED_JOBS } from "@/constants/sse";
import type { Job, JobAction, SSEEvent } from "@/types/job";

function reducer(state: Job[], action: JobAction): Job[] {
  switch (action.type) {
    case "HYDRATE":
      return action.jobs;
    case "ADD":
      return [action.job, ...state.filter((job) => job.id !== action.job.id)];
    case "PATCH":
      return state.map((job) =>
        job.id === action.id ? { ...job, ...action.patch } : job,
      );
    case "REMOVE":
      return state.filter((job) => job.id !== action.id);
    default:
      return state;
  }
}

function loadPersisted(): Job[] {
  try {
    const raw = localStorage.getItem(JOBS_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as Job[];
    return Array.isArray(parsed) ? parsed.slice(0, MAX_PERSISTED_JOBS) : [];
  } catch {
    return [];
  }
}

/**
 * Manage the live list of jobs, translate SSE events into job-state patches, and
 * persist the list to localStorage so a page refresh doesn't lose in-flight or
 * recently-finished jobs. Hydration runs after mount to avoid SSR mismatch;
 * status reconciliation for jobs that finished while away is handled separately
 * by `useJobReconcile`.
 */
export function useJobManager() {
  const [jobs, dispatch] = useReducer(reducer, []);
  const hydrated = useRef(false);

  // Hydrate from localStorage once, on the client, after first paint.
  useEffect(() => {
    dispatch({ type: "HYDRATE", jobs: loadPersisted() });
    hydrated.current = true;
  }, []);

  // Persist on change, but only after hydration so we never clobber stored jobs
  // with the empty initial state during the first render.
  useEffect(() => {
    if (!hydrated.current) return;
    try {
      localStorage.setItem(
        JOBS_STORAGE_KEY,
        JSON.stringify(jobs.slice(0, MAX_PERSISTED_JOBS)),
      );
    } catch {
      // storage full or unavailable — non-fatal, the list still works in-memory
    }
  }, [jobs]);

  const addJob = useCallback((job: Job) => dispatch({ type: "ADD", job }), []);
  const removeJob = useCallback(
    (id: string) => dispatch({ type: "REMOVE", id }),
    [],
  );
  const patchJob = useCallback(
    (id: string, patch: Partial<Job>) => dispatch({ type: "PATCH", id, patch }),
    [],
  );

  const applySSEEvent = useCallback((id: string, event: SSEEvent) => {
    switch (event.type) {
      case "progress":
        dispatch({
          type: "PATCH",
          id,
          patch: {
            status: "running",
            percent: event.percent,
            speed: event.speed,
            eta: event.eta,
          },
        });
        break;
      case "done":
        dispatch({
          type: "PATCH",
          id,
          patch: {
            status: "done",
            percent: 100,
            downloadUrl: event.download_url,
            fileSize: event.size,
            completedAt: Date.now(),
          },
        });
        break;
      case "error":
        dispatch({
          type: "PATCH",
          id,
          patch: { status: "error", error: event.message },
        });
        break;
      case "cancelled":
        dispatch({ type: "PATCH", id, patch: { status: "cancelled" } });
        break;
    }
  }, []);

  return { jobs, addJob, removeJob, patchJob, applySSEEvent };
}
