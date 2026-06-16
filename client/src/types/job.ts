export type Mode = "download" | "audio" | "playlist" | "convert" | "transcribe";

export type JobStatus = "pending" | "running" | "done" | "error" | "cancelled";

export type DownloadQuality = "best" | "1080p" | "720p" | "audio";
export type AudioFormat = "mp3" | "wav" | "flac" | "aac" | "ogg";
export type AudioBitrate = "128k" | "192k" | "256k" | "320k";
export type VideoFormat = "mp4" | "webm" | "mkv" | "mov" | "gif";
export type WhisperModel = "tiny" | "base" | "small" | "medium" | "large";
export type TranscriptFormat = "txt" | "srt" | "vtt";

export type Job = {
  id: string;
  type: string;
  title: string;
  thumbnail: string | null;
  status: JobStatus;
  percent: number;
  speed: string;
  eta: string;
  downloadUrl: string | null;
  fileSize: number | null;
  error: string | null;
  addedAt: number;
  completedAt: number | null;
};

/** Resolved metadata for any URL (single item or playlist). */
export type Metadata = {
  title: string;
  thumbnail: string | null;
  duration: number | null;
  uploader: string | null;
  is_playlist: boolean;
  entry_count: number | null;
};

export type SSEProgressEvent = {
  type: "progress";
  percent: number;
  speed: string;
  eta: string;
};

export type SSEDoneEvent = {
  type: "done";
  download_url: string;
  size: number;
};

export type SSEErrorEvent = {
  type: "error";
  message: string;
};

export type SSECancelledEvent = {
  type: "cancelled";
};

export type SSEEvent =
  | SSEProgressEvent
  | SSEDoneEvent
  | SSEErrorEvent
  | SSECancelledEvent;

export type PlaylistItem = {
  id: string;
  title: string;
  duration: number | null;
  thumbnail: string | null;
};

export type OptionValues = {
  audioFormat: AudioFormat;
  audioBitrate: AudioBitrate;
  videoFormat: VideoFormat;
  whisperModel: WhisperModel;
  transcriptFormat: TranscriptFormat;
  language: string;
  embedSubs: boolean;
  sponsorblock: boolean;
};

/** Shape returned by GET /api/jobs/{id} (status reconciliation, SSE fallback). */
export type JobStatusResponse = {
  job_id: string;
  status: string;
  message: string | null;
  download_url: string | null;
  file_size: number | null;
};

export type JobAction =
  | { type: "HYDRATE"; jobs: Job[] }
  | { type: "ADD"; job: Job }
  | { type: "PATCH"; id: string; patch: Partial<Job> }
  | { type: "REMOVE"; id: string };

export type SSEHandler = (event: SSEEvent) => void;

export type JobSubmitPayload = {
  type: string;
  url?: string;
  input_path?: string;
  quality?: DownloadQuality;
  audio_format?: AudioFormat;
  audio_bitrate?: AudioBitrate;
  video_format?: VideoFormat;
  whisper_model?: WhisperModel;
  transcript_format?: TranscriptFormat;
  language?: string;
  embed_subs?: boolean;
  sponsorblock?: boolean;
};
