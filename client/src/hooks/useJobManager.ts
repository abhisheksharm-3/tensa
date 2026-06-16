"use client";

import { useCallback, useReducer } from "react";
import type { Job, JobAction, SSEEvent } from "@/types/job";

function reducer(state: Job[], action: JobAction): Job[] {
  switch (action.type) {
    case "ADD":
      return [action.job, ...state];
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

/** Manage the live list of jobs and translate SSE events into job state patches. */
export function useJobManager() {
  const [jobs, dispatch] = useReducer(reducer, []);

  const addJob = useCallback((job: Job) => dispatch({ type: "ADD", job }), []);
  const removeJob = useCallback(
    (id: string) => dispatch({ type: "REMOVE", id }),
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

  return { jobs, addJob, removeJob, applySSEEvent };
}
