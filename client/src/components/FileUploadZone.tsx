"use client";

import { FileAudio, FileVideo, Upload, X } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import type { FileUploadZoneProps } from "@/components/types";
import { ACCEPTED_FILE_TYPES } from "@/constants/modes";
import { cn, formatBytes } from "@/lib/utils";

export function FileUploadZone({ mode, file, onFile }: FileUploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) onFile(dropped);
    },
    [onFile],
  );

  if (file) {
    return (
      <div className="mx-1 flex items-center gap-3 rounded-xl border border-border bg-background/40 p-3">
        {file.type.startsWith("audio") ? (
          <FileAudio className="size-5 shrink-0 text-primary" />
        ) : (
          <FileVideo className="size-5 shrink-0 text-primary" />
        )}
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm text-foreground">{file.name}</p>
          <p className="font-mono text-xs text-muted-foreground">
            {formatBytes(file.size)}
          </p>
        </div>
        <button
          type="button"
          aria-label="Remove file"
          onClick={() => onFile(null)}
          className="text-muted-foreground transition-colors hover:text-foreground"
        >
          <X className="size-4" />
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      className={cn(
        "mx-1 block w-[calc(100%-0.5rem)] rounded-xl border border-dashed p-6 text-center transition-colors",
        isDragging
          ? "border-primary/60 bg-primary/5"
          : "border-border hover:border-muted-foreground/60 hover:bg-background/40",
      )}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <Upload className="mx-auto mb-2 size-5 text-muted-foreground" />
      <p className="text-sm text-foreground">Drop a file, or click to browse</p>
      <p className="mt-0.5 font-mono text-xs text-muted-foreground/70">
        {mode === "convert" ? "video files" : "audio or video"}
      </p>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_FILE_TYPES[mode]}
        className="hidden"
        onChange={(e) => {
          const selected = e.target.files?.[0];
          if (selected) onFile(selected);
        }}
      />
    </button>
  );
}
