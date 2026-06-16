"use client";

import { ArrowRight, Loader2 } from "lucide-react";
import { FileUploadZone } from "@/components/FileUploadZone";
import { ModeSelector } from "@/components/ModeSelector";
import { OptionsPanel } from "@/components/OptionsPanel";
import { PlaylistModal } from "@/components/PlaylistModal";
import { QualitySelector } from "@/components/QualitySelector";
import type { UrlPanelProps } from "@/components/types";
import { URL_MODES } from "@/constants/modes";
import { useUrlPanel } from "@/hooks/useUrlPanel";
import { cn } from "@/lib/utils";

export function UrlPanel({ onJobAdded }: UrlPanelProps) {
  const panel = useUrlPanel(onJobAdded);

  return (
    <>
      <div className="rounded-2xl border border-border/70 bg-card/60 p-3 shadow-2xl shadow-black/40 backdrop-blur-xl">
        <form onSubmit={panel.onSubmit} className="space-y-3">
          <ModeSelector value={panel.mode} onChange={panel.onModeChange} />

          {panel.showUrlInput && (
            <div className="group flex items-center gap-2 rounded-xl border border-border bg-input/60 p-1.5 pl-4 transition-colors focus-within:border-primary/60 focus-within:glow-ember-soft">
              <input
                type="url"
                value={panel.url}
                onChange={(e) => panel.setUrl(e.target.value)}
                placeholder={
                  URL_MODES.has(panel.mode)
                    ? "https://…"
                    : "paste a URL, or upload below"
                }
                className="min-w-0 flex-1 bg-transparent font-mono text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none"
              />
              <button
                type="submit"
                disabled={panel.loading}
                aria-label="Start"
                className={cn(
                  "inline-flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-all",
                  "hover:glow-ember disabled:opacity-60",
                )}
              >
                {panel.loading ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  <ArrowRight className="size-4" />
                )}
              </button>
            </div>
          )}

          {panel.showQuality && (
            <QualitySelector
              value={panel.quality}
              onChange={panel.setQuality}
            />
          )}

          {panel.showFileUpload && (
            <FileUploadZone
              mode={panel.mode}
              file={panel.file}
              onFile={panel.setFile}
            />
          )}

          <OptionsPanel
            mode={panel.mode}
            values={panel.options}
            onChange={panel.patchOptions}
          />

          {panel.error && (
            <p className="px-1 font-mono text-xs text-destructive">
              {panel.error}
            </p>
          )}
        </form>
      </div>

      <PlaylistModal
        open={panel.playlist.open}
        onClose={panel.playlist.close}
        title={panel.playlist.title}
        items={panel.playlist.items}
        loading={panel.playlist.loading}
        error={panel.playlist.error}
        onDownload={panel.playlist.onDownload}
      />
    </>
  );
}
