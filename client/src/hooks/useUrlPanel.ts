"use client";

import { useCallback, useState, useTransition } from "react";
import type { UseUrlPanelReturn } from "@/components/types";
import { FILE_MODES, URL_MODES } from "@/constants/modes";
import { DEFAULT_OPTIONS } from "@/constants/options";
import {
  useMetadata,
  usePlaylistInfo,
  useSubmitJob,
  useUploadFile,
} from "@/hooks/useJobActions";
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
  if (mode === "download") {
    payload.quality = quality;
    payload.embed_subs = options.embedSubs;
    payload.sponsorblock = options.sponsorblock;
  }
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

/**
 * Orchestrates the submit panel. All backend access goes through the React Query
 * hooks (useSubmitJob / useUploadFile / usePlaylistInfo) which wrap Server
 * Actions — this hook never touches the API directly. `useTransition` keeps the
 * UI responsive while a submission is in flight.
 */
export function useUrlPanel(onJobAdded: (job: Job) => void): UseUrlPanelReturn {
  const [url, setUrl] = useState("");
  const [mode, setMode] = useState<Mode>("download");
  const [quality, setQuality] = useState<DownloadQuality>("best");
  const [options, setOptions] = useState<OptionValues>(DEFAULT_OPTIONS);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const submitJob = useSubmitJob();
  const uploadFile = useUploadFile();
  const playlistInfo = usePlaylistInfo();
  const metadata = useMetadata();

  const [playlistOpen, setPlaylistOpen] = useState(false);
  const [playlistTitle, setPlaylistTitle] = useState("");
  const [playlistItems, setPlaylistItems] = useState<PlaylistItem[]>([]);

  const patchOptions = useCallback((patch: Partial<OptionValues>) => {
    setOptions((prev) => ({ ...prev, ...patch }));
  }, []);

  const onModeChange = useCallback((next: Mode) => {
    setMode(next);
    setError(null);
    setFile(null);
  }, []);

  const openPlaylist = useCallback(
    async (playlistUrl: string) => {
      setPlaylistItems([]);
      setPlaylistTitle(playlistUrl);
      setPlaylistOpen(true);
      try {
        const info = await playlistInfo.mutateAsync(playlistUrl);
        setPlaylistItems(info.items);
        if (info.title) setPlaylistTitle(info.title);
      } catch {
        // surfaced via playlistInfo.error in the modal
      }
    },
    [playlistInfo],
  );

  const onSubmit = useCallback(
    (e: React.FormEvent) => {
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
        startTransition(() => {
          void openPlaylist(trimmedUrl);
        });
        return;
      }

      startTransition(async () => {
        try {
          let inputPath: string | undefined;
          if (file && FILE_MODES.has(mode)) {
            inputPath = (await uploadFile.mutateAsync(file)).uploadPath;
          }
          const payload = buildPayload(
            mode,
            trimmedUrl,
            inputPath,
            quality,
            options,
          );
          // Enqueue and resolve metadata concurrently so the job card can show a
          // real title + cover instead of the raw URL (best-effort; URL falls back).
          const metaPromise = trimmedUrl
            ? metadata.mutateAsync(trimmedUrl).catch(() => null)
            : Promise.resolve(null);
          const [{ jobId }, meta] = await Promise.all([
            submitJob.mutateAsync(payload),
            metaPromise,
          ]);
          onJobAdded(
            createPendingJob(
              jobId,
              mode,
              meta?.title ?? deriveJobTitle(file, trimmedUrl),
              meta?.thumbnail ?? null,
            ),
          );
          setUrl("");
          setFile(null);
        } catch (err) {
          setError(err instanceof Error ? err.message : "Something went wrong");
        }
      });
    },
    [
      url,
      mode,
      file,
      quality,
      options,
      onJobAdded,
      openPlaylist,
      submitJob,
      uploadFile,
      metadata,
    ],
  );

  const onPlaylistDownload = useCallback(
    async (selected: PlaylistItem[], selectedQuality: DownloadQuality) => {
      setPlaylistOpen(false);
      for (const item of selected) {
        try {
          const videoUrl = `https://www.youtube.com/watch?v=${item.id}`;
          const { jobId } = await submitJob.mutateAsync({
            type: "playlist_item",
            url: videoUrl,
            quality: selectedQuality,
          });
          onJobAdded(
            createPendingJob(
              jobId,
              "playlist_item",
              item.title,
              item.thumbnail,
            ),
          );
        } catch {
          // a failed enqueue can be retried by the user
        }
      }
      setUrl("");
    },
    [onJobAdded, submitJob],
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
    loading: isPending || submitJob.isPending || uploadFile.isPending,
    error,
    onSubmit,
    playlist: {
      open: playlistOpen,
      title: playlistTitle,
      items: playlistItems,
      loading: playlistInfo.isPending,
      error: playlistInfo.error ? playlistInfo.error.message : null,
      close: () => setPlaylistOpen(false),
      onDownload: onPlaylistDownload,
    },
    showUrlInput: URL_MODES.has(mode) || FILE_MODES.has(mode),
    showFileUpload: FILE_MODES.has(mode),
    showQuality: mode === "download",
  };
}
