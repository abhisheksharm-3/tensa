export const TERMINAL_EVENT_TYPES = new Set(["done", "error", "cancelled"]);
export const MAX_SSE_RETRIES = 3;
export const POLL_INTERVAL_MS = 3000;
export const FILE_EXPIRY_SECONDS = 300;

/** localStorage key + cap for the persisted job list (survives page refresh). */
export const JOBS_STORAGE_KEY = "tensa.jobs.v1";
export const MAX_PERSISTED_JOBS = 50;
