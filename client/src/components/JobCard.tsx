"use client";

import { AlertCircle, CheckCircle2, Download, Loader2, X } from "lucide-react";
import { useEffect, useState } from "react";
import type { JobCardProps } from "@/components/types";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { API_BASE } from "@/constants/api";
import { FILE_EXPIRY_SECONDS } from "@/constants/sse";
import { useSSE } from "@/hooks/useSSE";
import { cancelJob } from "@/lib/api";
import { cn, formatBytes, triggerDownload } from "@/lib/utils";
import type { JobStatus } from "@/types/job";

function StatusIcon({ status }: { status: JobStatus }) {
  switch (status) {
    case "pending":
      return (
        <Loader2 className="mt-0.5 size-4 shrink-0 animate-spin text-muted-foreground" />
      );
    case "running":
      return (
        <span className="mt-1 size-2 shrink-0 rounded-full bg-amber-400 shadow-[0_0_6px_1px] shadow-amber-400/60" />
      );
    case "done":
      return <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-primary" />;
    case "error":
      return (
        <AlertCircle className="mt-0.5 size-4 shrink-0 text-destructive" />
      );
    case "cancelled":
      return <X className="mt-0.5 size-4 shrink-0 text-muted-foreground" />;
  }
}

export function JobCard({ job, onEvent, onRemove }: JobCardProps) {
  const [expiresIn, setExpiresIn] = useState<number | null>(null);
  const isActive = job.status === "pending" || job.status === "running";

  useSSE(isActive ? job.id : null, (event) => onEvent(job.id, event));

  useEffect(() => {
    if (job.status !== "done") return;
    setExpiresIn(FILE_EXPIRY_SECONDS);
    const interval = setInterval(() => {
      setExpiresIn((prev) => {
        if (prev === null || prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [job.status]);

  const handleDownload = () => {
    if (job.downloadUrl)
      triggerDownload(`${API_BASE}${job.downloadUrl}`, job.title);
  };

  return (
    <div
      className={cn(
        "rounded-lg border p-4 transition-colors",
        job.status === "done" && "border-primary/40 bg-primary/5",
        job.status === "error" && "border-destructive/40 bg-destructive/5",
        !["done", "error"].includes(job.status) && "border-border bg-card",
      )}
    >
      <div className="mb-3 flex items-start gap-3">
        <StatusIcon status={job.status} />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-foreground">
            {job.title}
          </p>
          <p className="text-xs capitalize text-muted-foreground">
            {job.type.replace("_", " ")}
          </p>
        </div>
        {isActive ? (
          <Button
            variant="ghost"
            size="icon"
            className="size-7 text-muted-foreground"
            onClick={() => cancelJob(job.id)}
          >
            <X className="size-4" />
          </Button>
        ) : (
          <Button
            variant="ghost"
            size="icon"
            className="size-7 text-muted-foreground"
            onClick={() => onRemove(job.id)}
          >
            <X className="size-4" />
          </Button>
        )}
      </div>

      {job.status === "running" && (
        <div className="space-y-1.5">
          <Progress value={job.percent} className="h-1.5" />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>
              {job.percent.toFixed(1)}% · {job.speed}
            </span>
            <span>{job.eta} remaining</span>
          </div>
        </div>
      )}

      {job.status === "pending" && (
        <p className="text-xs text-muted-foreground">Queued…</p>
      )}

      {job.status === "done" && (
        <div className="space-y-2">
          <Button className="h-8 w-full text-sm" onClick={handleDownload}>
            <Download className="mr-1.5 size-3.5" />
            Download {job.fileSize ? `(${formatBytes(job.fileSize)})` : ""}
          </Button>
          {expiresIn !== null && expiresIn > 0 && (
            <p className="text-center text-xs text-muted-foreground">
              Expires in {Math.floor(expiresIn / 60)}m {expiresIn % 60}s
            </p>
          )}
          {expiresIn === 0 && (
            <p className="text-center text-xs text-muted-foreground">
              File expired
            </p>
          )}
        </div>
      )}

      {job.status === "error" && (
        <p className="mt-1 line-clamp-2 text-xs text-destructive">
          {job.error}
        </p>
      )}
    </div>
  );
}
