"use client";

import { Loader2, Send } from "lucide-react";
import { FileUploadZone } from "@/components/FileUploadZone";
import { ModeSelector } from "@/components/ModeSelector";
import { OptionsPanel } from "@/components/OptionsPanel";
import { PlaylistModal } from "@/components/PlaylistModal";
import { QualitySelector } from "@/components/QualitySelector";
import type { UrlPanelProps } from "@/components/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { URL_MODES } from "@/constants/modes";
import { useUrlPanel } from "@/hooks/useUrlPanel";

export function UrlPanel({ onJobAdded }: UrlPanelProps) {
  const panel = useUrlPanel(onJobAdded);

  return (
    <>
      <form onSubmit={panel.onSubmit} className="space-y-3">
        <ModeSelector value={panel.mode} onChange={panel.onModeChange} />

        {panel.showUrlInput && (
          <div className="flex gap-2">
            <Input
              type="url"
              value={panel.url}
              onChange={(e) => panel.setUrl(e.target.value)}
              placeholder={
                URL_MODES.has(panel.mode)
                  ? "Paste URL here…"
                  : "Paste URL, or upload a file below"
              }
              className="flex-1"
            />
            <Button type="submit" disabled={panel.loading} className="px-4">
              {panel.loading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Send className="size-4" />
              )}
            </Button>
          </div>
        )}

        {panel.showQuality && (
          <QualitySelector value={panel.quality} onChange={panel.setQuality} />
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
          <p className="text-xs text-destructive">{panel.error}</p>
        )}
      </form>

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
