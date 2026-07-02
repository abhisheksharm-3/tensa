"use client";

import { Check, Loader2 } from "lucide-react";
import { useMemo, useState } from "react";
import { QualitySelector } from "@/components/QualitySelector";
import type { PlaylistModalProps } from "@/components/types";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { cn, formatDuration } from "@/lib/utils";
import type { DownloadQuality } from "@/types/job";

function CheckBox({ checked }: { checked: boolean }) {
  return (
    <span
      className={cn(
        "flex size-5 shrink-0 items-center justify-center rounded-md border transition-colors",
        checked
          ? "border-primary bg-primary text-primary-foreground"
          : "border-border bg-input/40",
      )}
    >
      {checked && <Check className="size-3.5" strokeWidth={3} />}
    </span>
  );
}

export function PlaylistModal({
  open,
  onClose,
  title,
  items,
  loading,
  error,
  onDownload,
}: PlaylistModalProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [quality, setQuality] = useState<DownloadQuality>("best");

  const allSelected = items.length > 0 && selected.size === items.length;

  const toggle = (id: string) =>
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const toggleAll = () =>
    setSelected(allSelected ? new Set() : new Set(items.map((i) => i.id)));

  const selectedItems = useMemo(
    () => items.filter((i) => selected.has(i.id)),
    [items, selected],
  );

  return (
    <Sheet open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <SheetContent
        side="bottom"
        className="h-[85vh] gap-0 rounded-t-2xl border-border/70 bg-card/95 p-0 backdrop-blur-xl"
      >
        <div className="mx-auto flex h-full w-full max-w-2xl flex-col">
          <header className="shrink-0 border-b border-border/60 px-5 pt-5 pb-4 pr-12">
            <h2 className="truncate font-display text-lg font-semibold text-foreground">
              {title || "Playlist"}
            </h2>
            <p className="font-mono text-xs text-muted-foreground">
              {items.length} videos
            </p>
          </header>

          {loading && (
            <div className="flex flex-1 items-center justify-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="size-5 animate-spin" />
              loading playlist…
            </div>
          )}

          {error && (
            <div className="flex flex-1 items-center justify-center px-6 text-center font-mono text-sm text-destructive">
              {error}
            </div>
          )}

          {!loading && !error && items.length > 0 && (
            <>
              {/* biome-ignore lint/a11y/useSemanticElements: composite toggle row, not a native checkbox */}
              <button
                type="button"
                onClick={toggleAll}
                role="checkbox"
                aria-checked={allSelected}
                className="flex shrink-0 items-center gap-3 border-b border-border/60 px-5 py-3 text-left text-xs text-muted-foreground transition-colors hover:text-foreground"
              >
                <CheckBox checked={allSelected} />
                {allSelected ? "Deselect all" : "Select all"}
                <span className="ml-auto font-mono">
                  {selected.size} selected
                </span>
              </button>

              <div className="min-h-0 flex-1 overflow-y-auto">
                {items.map((item, idx) => {
                  const isSel = selected.has(item.id);
                  return (
                    // biome-ignore lint/a11y/useSemanticElements: composite media row, not a native checkbox
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => toggle(item.id)}
                      role="checkbox"
                      aria-checked={isSel}
                      className={cn(
                        "flex w-full items-center gap-3 px-5 py-2.5 text-left transition-colors",
                        isSel ? "bg-primary/5" : "hover:bg-muted/40",
                      )}
                    >
                      <CheckBox checked={isSel} />
                      <span className="w-5 shrink-0 text-right font-mono text-[11px] text-muted-foreground">
                        {idx + 1}
                      </span>
                      {item.thumbnail ? (
                        // biome-ignore lint/performance/noImgElement: remote yt-dlp thumbnails
                        <img
                          src={item.thumbnail}
                          alt=""
                          className="h-9 w-16 shrink-0 rounded bg-muted object-cover"
                        />
                      ) : null}
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm text-foreground">
                          {item.title}
                        </p>
                        <p className="font-mono text-[11px] text-muted-foreground">
                          {formatDuration(item.duration)}
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </>
          )}

          <footer className="shrink-0 space-y-3 border-t border-border/60 px-5 pt-3 pb-5">
            <QualitySelector value={quality} onChange={setQuality} />
            <button
              type="button"
              disabled={selected.size === 0}
              onClick={() => onDownload(selectedItems, quality)}
              className="inline-flex h-10 w-full items-center justify-center rounded-lg bg-primary text-sm font-medium text-primary-foreground transition-all hover:glow-ember disabled:opacity-50"
            >
              Download{selected.size > 0 ? ` ${selected.size} selected` : ""}
            </button>
          </footer>
        </div>
      </SheetContent>
    </Sheet>
  );
}
