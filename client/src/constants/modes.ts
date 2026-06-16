import { Download, FileText, ListVideo, Music, RefreshCcw } from "lucide-react";
import type { Mode } from "@/types/job";

export type ModeOption = {
  value: Mode;
  label: string;
  icon: React.ElementType;
};

export const MODES: ModeOption[] = [
  { value: "download", label: "Video", icon: Download },
  { value: "audio", label: "Audio", icon: Music },
  { value: "playlist", label: "Playlist", icon: ListVideo },
  { value: "convert", label: "Convert", icon: RefreshCcw },
  { value: "transcribe", label: "Transcribe", icon: FileText },
];

export const URL_MODES = new Set<Mode>(["download", "playlist"]);
export const FILE_MODES = new Set<Mode>(["audio", "convert", "transcribe"]);

export const ACCEPTED_FILE_TYPES: Record<Mode, string> = {
  audio: "audio/*,video/*",
  convert: "video/*",
  transcribe: "audio/*,video/*",
  download: "",
  playlist: "",
};
