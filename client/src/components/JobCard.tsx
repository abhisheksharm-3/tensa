"use client";

import { AlertCircle, ArrowDownToLine, Check, Loader2, X } from "lucide-react";
import { useEffect, useState } from "react";
import type { JobCardProps } from "@/components/types";
import { FILE_EXPIRY_SECONDS } from "@/constants/sse";
import { useCancelJob } from "@/hooks/useJobActions";
import { useSSE } from "@/hooks/useSSE";
import { fileDownloadUrl } from "@/lib/stream";
import { cn, formatBytes, triggerDownload } from "@/lib/utils";
import type { JobStatus } from "@/types/job";

function StatusDot({ status }: { status: JobStatus }) {
  switch (status) {
    case "pending":
      return (
        <Loader2 className="size-4 shrink-0 animate-spin text-muted-foreground" />
      );
    case "running":
      return (
        <span className="size-2.5 shrink-0 rounded-full bg-primary shadow-[0_0_8px_2px] shadow-primary/60" />
      );
    case "done":
      return <Check className="size-4 shrink-0 text-primary" />;
    case "error":
      return <AlertCircle className="size-4 shrink-0 text-destructive" />;
    case "cancelled":
      return <X className="size-4 shrink-0 text-muted-foreground" />;
  }
}

export function JobCard({ job, onEvent, onRemove }: JobCardProps) {
  const [expiresIn, setExpiresIn] = useState<number | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const isActive = job.status === "pending" || job.status === "running";
  const cancelJob = useCancelJob();

  useSSE(isActive ? job.id : null, (event) => onEvent(job.id, event));

  // Count down from the real completion time so a persisted/refreshed job shows
  // the true remaining lifetime (or "expired") instead of a fresh 5:00.
  useEffect(() => {
    if (job.status !== "done") return;
    const since = job.completedAt ?? job.addedAt;
    const tick = () => {
      const elapsed = Math.floor((Date.now() - since) / 1000);
      setExpiresIn(Math.max(0, FILE_EXPIRY_SECONDS - elapsed));
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [job.status, job.completedAt, job.addedAt]);

  const expired = job.status === "done" && expiresIn === 0;

  const handleDownload = async () => {
    if (!job.downloadUrl) return;
    setDownloadError(null);
    // Use the real output filename (with extension) from the URL, not the display
    // title — the metadata title has no extension and would save as a "Document".
    const filename = decodeURIComponent(
      job.downloadUrl.split("/").pop() ?? job.title,
    );
    try {
      await triggerDownload(fileDownloadUrl(job.downloadUrl), filename);
    } catch {
      setDownloadError("File expired — re-submit to download again.");
    }
  };

  return (
    <div
      className={cn(
        "animate-rise-in rounded-xl border bg-card/50 p-4 backdrop-blur-sm transition-colors",
        job.status === "done" && "border-primary/30",
        job.status === "error" && "border-destructive/30",
        !["done", "error"].includes(job.status) && "border-border/70",
      )}
    >
      <div className="flex items-start gap-3">
        {job.thumbnail ? (
          // biome-ignore lint/performance/noImgElement: remote yt-dlp thumbnails, not local assets
          <img
            src={job.thumbnail}
            alt=""
            className="h-12 w-20 shrink-0 rounded-md border border-border/60 bg-muted object-cover"
          />
        ) : (
          <span className="mt-0.5 flex size-4 items-center justify-center">
            <StatusDot status={job.status} />
          </span>
        )}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            {job.thumbnail && <StatusDot status={job.status} />}
            <p className="truncate text-sm font-medium text-foreground">
              {job.title}
            </p>
          </div>
          <p className="font-mono text-[11px] uppercase tracking-wide text-muted-foreground">
            {job.type.replace("_", " ")}
          </p>
        </div>
        <button
          type="button"
          aria-label={isActive ? "Cancel" : "Dismiss"}
          onClick={() =>
            isActive ? cancelJob.mutate(job.id) : onRemove(job.id)
          }
          className="text-muted-foreground transition-colors hover:text-foreground"
        >
          <X className="size-4" />
        </button>
      </div>

      {job.status === "running" && (
        <div className="mt-3 space-y-1.5">
          <div className="h-1 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary shadow-[0_0_8px_0] shadow-primary/60 transition-[width] duration-300 ease-out"
              style={{ width: `${job.percent}%` }}
            />
          </div>
          <div className="flex justify-between font-mono text-[11px] text-muted-foreground">
            <span>
              {job.percent.toFixed(1)}% · {job.speed}
            </span>
            <span>{job.eta} left</span>
          </div>
        </div>
      )}

      {job.status === "pending" && (
        <p className="mt-3 font-mono text-xs text-muted-foreground">queued…</p>
      )}

      {job.status === "done" && (
        <div className="mt-3 space-y-2">
          {expired ? (
            <p className="font-mono text-xs text-muted-foreground">
              file expired — re-submit to download again
            </p>
          ) : (
            <>
              <button
                type="button"
                onClick={handleDownload}
                className="inline-flex h-9 w-full items-center justify-center gap-2 rounded-lg bg-primary text-sm font-medium text-primary-foreground transition-all hover:glow-ember"
              >
                <ArrowDownToLine className="size-4" />
                Download{job.fileSize ? ` · ${formatBytes(job.fileSize)}` : ""}
              </button>
              {expiresIn !== null && (
                <p className="text-center font-mono text-[11px] text-muted-foreground">
                  expires in {Math.floor(expiresIn / 60)}m {expiresIn % 60}s
                </p>
              )}
            </>
          )}
          {downloadError && (
            <p className="text-center font-mono text-[11px] text-destructive">
              {downloadError}
            </p>
          )}
        </div>
      )}

      {job.status === "error" && (
        <p className="mt-2 line-clamp-2 font-mono text-xs text-destructive">
          {job.error}
        </p>
      )}
    </div>
  );
}
