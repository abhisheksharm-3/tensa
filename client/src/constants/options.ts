import type {
  AudioBitrate,
  AudioFormat,
  DownloadQuality,
  OptionValues,
  TranscriptFormat,
  VideoFormat,
  WhisperModel,
} from "@/types/job";

export const QUALITIES: { value: DownloadQuality; label: string }[] = [
  { value: "best", label: "Best" },
  { value: "1080p", label: "1080p" },
  { value: "720p", label: "720p" },
  { value: "audio", label: "Audio only" },
];

export const AUDIO_FORMATS: AudioFormat[] = [
  "mp3",
  "wav",
  "flac",
  "aac",
  "ogg",
];
export const AUDIO_BITRATES: AudioBitrate[] = ["128k", "192k", "256k", "320k"];
export const VIDEO_FORMATS: VideoFormat[] = [
  "mp4",
  "webm",
  "mkv",
  "mov",
  "gif",
];
export const WHISPER_MODELS: WhisperModel[] = [
  "tiny",
  "base",
  "small",
  "medium",
  "large",
];
export const TRANSCRIPT_FORMATS: TranscriptFormat[] = ["srt", "vtt", "txt"];

export const DEFAULT_OPTIONS: OptionValues = {
  audioFormat: "mp3",
  audioBitrate: "192k",
  videoFormat: "mp4",
  whisperModel: "base",
  transcriptFormat: "srt",
  language: "",
};
