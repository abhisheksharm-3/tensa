"use client";

import { Loader2 } from "lucide-react";
import { useMemo, useState } from "react";
import { QualitySelector } from "@/components/QualitySelector";
import type { PlaylistModalProps } from "@/components/types";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { formatDuration } from "@/lib/utils";
import type { DownloadQuality } from "@/types/job";

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

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleAll = () => {
    setSelected(
      allSelected ? new Set() : new Set(items.map((item) => item.id)),
    );
  };

  const selectedItems = useMemo(
    () => items.filter((item) => selected.has(item.id)),
    [items, selected],
  );

  return (
    <Sheet open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <SheetContent side="bottom" className="flex h-[85vh] flex-col gap-0 p-0">
        <SheetHeader className="border-b border-border px-4 pt-4 pb-3">
          <SheetTitle className="text-base">{title || "Playlist"}</SheetTitle>
          <p className="text-xs text-muted-foreground">{items.length} videos</p>
        </SheetHeader>

        {loading && (
          <div className="flex flex-1 items-center justify-center">
            <Loader2 className="size-6 animate-spin text-muted-foreground" />
            <span className="ml-2 text-sm text-muted-foreground">
              Loading playlist…
            </span>
          </div>
        )}

        {error && (
          <div className="flex flex-1 items-center justify-center px-4">
            <p className="text-center text-sm text-destructive">{error}</p>
          </div>
        )}

        {!loading && !error && items.length > 0 && (
          <>
            <div className="flex items-center gap-3 border-b border-border px-4 py-2">
              <Checkbox
                id="select-all"
                checked={allSelected}
                onCheckedChange={toggleAll}
              />
              <label
                htmlFor="select-all"
                className="cursor-pointer text-xs text-muted-foreground"
              >
                {allSelected ? "Deselect all" : "Select all"}
              </label>
            </div>

            <ScrollArea className="flex-1">
              <div className="divide-y divide-border/60">
                {items.map((item, idx) => (
                  <label
                    key={item.id}
                    htmlFor={`playlist-item-${item.id}`}
                    className="flex cursor-pointer items-center gap-3 px-4 py-3 transition-colors hover:bg-muted/40"
                  >
                    <Checkbox
                      id={`playlist-item-${item.id}`}
                      checked={selected.has(item.id)}
                      onCheckedChange={() => toggle(item.id)}
                      className="shrink-0"
                    />
                    {item.thumbnail && (
                      // biome-ignore lint/performance/noImgElement: remote yt-dlp thumbnails, not local assets
                      <img
                        src={item.thumbnail}
                        alt=""
                        className="size-auto h-9 w-14 shrink-0 rounded bg-muted object-cover"
                      />
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm text-foreground">
                        {idx + 1}. {item.title}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDuration(item.duration)}
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </ScrollArea>
          </>
        )}

        <div className="flex flex-col gap-3 border-t border-border px-4 pt-3 pb-4">
          <QualitySelector value={quality} onChange={setQuality} />
          <Button
            className="w-full"
            disabled={selected.size === 0}
            onClick={() => onDownload(selectedItems, quality)}
          >
            Download {selected.size > 0 ? `${selected.size} selected` : ""}
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
