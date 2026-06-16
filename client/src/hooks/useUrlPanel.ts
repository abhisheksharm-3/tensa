"use client";

import { useCallback, useState } from "react";
import type { UseUrlPanelReturn } from "@/components/types";
import { FILE_MODES, URL_MODES } from "@/constants/modes";
import { DEFAULT_OPTIONS } from "@/constants/options";
import { fetchPlaylistInfo, submitJob, uploadFile } from "@/lib/api";
import { createPendingJob, deriveJobTitle } from "@/lib/job-factory";
import type {
  DownloadQuality,
  Job,
  JobSubmitPayload,
  Mode,
  OptionValues,
  PlaylistItem,
} from "@/types/job";

function buildPayload(
  mode: Mode,
  url: string,
  inputPath: string | undefined,
  quality: DownloadQuality,
  options: OptionValues,
): JobSubmitPayload {
  const payload: JobSubmitPayload = { type: mode };
  if (url) payload.url = url;
  if (inputPath) payload.input_path = inputPath;
  if (mode === "download") payload.quality = quality;
  if (mode === "audio") {
    payload.audio_format = options.audioFormat;
    payload.audio_bitrate = options.audioBitrate;
  }
  if (mode === "convert") payload.video_format = options.videoFormat;
  if (mode === "transcribe") {
    payload.whisper_model = options.whisperModel;
    payload.transcript_format = options.transcriptFormat;
    if (options.language) payload.language = options.language;
  }
  return payload;
}

export function useUrlPanel(onJobAdded: (job: Job) => void): UseUrlPanelReturn {
  const [url, setUrl] = useState("");
  const [mode, setMode] = useState<Mode>("download");
  const [quality, setQuality] = useState<DownloadQuality>("best");
  const [options, setOptions] = useState<OptionValues>(DEFAULT_OPTIONS);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [playlistOpen, setPlaylistOpen] = useState(false);
  const [playlistTitle, setPlaylistTitle] = useState("");
  const [playlistItems, setPlaylistItems] = useState<PlaylistItem[]>([]);
  const [playlistLoading, setPlaylistLoading] = useState(false);
  const [playlistError, setPlaylistError] = useState<string | null>(null);

  const patchOptions = useCallback((patch: Partial<OptionValues>) => {
    setOptions((prev) => ({ ...prev, ...patch }));
  }, []);

  const onModeChange = useCallback((next: Mode) => {
    setMode(next);
    setError(null);
    setFile(null);
  }, []);

  const openPlaylist = useCallback(async (playlistUrl: string) => {
    setPlaylistLoading(true);
    setPlaylistError(null);
    setPlaylistItems([]);
    setPlaylistTitle(playlistUrl);
    setPlaylistOpen(true);
    try {
      const info = await fetchPlaylistInfo(playlistUrl);
      setPlaylistItems(info.items);
    } catch (err) {
      setPlaylistError(
        err instanceof Error ? err.message : "Failed to load playlist",
      );
    } finally {
      setPlaylistLoading(false);
    }
  }, []);

  const onSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);
      const trimmedUrl = url.trim();

      if (URL_MODES.has(mode) && !trimmedUrl) {
        setError("Please enter a URL.");
        return;
      }
      if (FILE_MODES.has(mode) && !trimmedUrl && !file) {
        setError("Please enter a URL or upload a file.");
        return;
      }

      if (mode === "playlist") {
        await openPlaylist(trimmedUrl);
        return;
      }

      setLoading(true);
      try {
        let inputPath: string | undefined;
        if (file && FILE_MODES.has(mode)) {
          inputPath = (await uploadFile(file)).upload_path;
        }
        const payload = buildPayload(
          mode,
          trimmedUrl,
          inputPath,
          quality,
          options,
        );
        const { job_id } = await submitJob(payload);
        onJobAdded(
          createPendingJob(job_id, mode, deriveJobTitle(file, trimmedUrl)),
        );
        setUrl("");
        setFile(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Something went wrong");
      } finally {
        setLoading(false);
      }
    },
    [url, mode, file, quality, options, onJobAdded, openPlaylist],
  );

  const onPlaylistDownload = useCallback(
    async (selected: PlaylistItem[], selectedQuality: DownloadQuality) => {
      setPlaylistOpen(false);
      for (const item of selected) {
        try {
          const videoUrl = `https://www.youtube.com/watch?v=${item.id}`;
          const { job_id } = await submitJob({
            type: "playlist_item",
            url: videoUrl,
            quality: selectedQuality,
          });
          onJobAdded(createPendingJob(job_id, "playlist_item", item.title));
        } catch {
          // a failed enqueue surfaces as the item's own error state on retry
        }
      }
      setUrl("");
    },
    [onJobAdded],
  );

  return {
    url,
    setUrl,
    mode,
    onModeChange,
    quality,
    setQuality,
    options,
    patchOptions,
    file,
    setFile,
    loading,
    error,
    onSubmit,
    playlist: {
      open: playlistOpen,
      title: playlistTitle,
      items: playlistItems,
      loading: playlistLoading,
      error: playlistError,
      close: () => setPlaylistOpen(false),
      onDownload: onPlaylistDownload,
    },
    showUrlInput: URL_MODES.has(mode) || FILE_MODES.has(mode),
    showFileUpload: FILE_MODES.has(mode),
    showQuality: mode === "download",
  };
}
