import type {
  DownloadQuality,
  Job,
  Mode,
  OptionValues,
  PlaylistItem,
  SSEEvent,
} from "@/types/job";

export type UseUrlPanelReturn = {
  url: string;
  setUrl: (url: string) => void;
  mode: Mode;
  onModeChange: (mode: Mode) => void;
  quality: DownloadQuality;
  setQuality: (quality: DownloadQuality) => void;
  options: OptionValues;
  patchOptions: (patch: Partial<OptionValues>) => void;
  file: File | null;
  setFile: (file: File | null) => void;
  loading: boolean;
  error: string | null;
  onSubmit: (e: React.FormEvent) => void;
  playlist: {
    open: boolean;
    title: string;
    items: PlaylistItem[];
    loading: boolean;
    error: string | null;
    close: () => void;
    onDownload: (selected: PlaylistItem[], quality: DownloadQuality) => void;
  };
  showUrlInput: boolean;
  showFileUpload: boolean;
  showQuality: boolean;
};

export type ModeSelectorProps = {
  value: Mode;
  onChange: (mode: Mode) => void;
};

export type QualitySelectorProps = {
  value: DownloadQuality;
  onChange: (quality: DownloadQuality) => void;
};

export type OptionsPanelProps = {
  mode: Mode;
  values: OptionValues;
  onChange: (patch: Partial<OptionValues>) => void;
};

export type FileUploadZoneProps = {
  mode: Mode;
  file: File | null;
  onFile: (file: File | null) => void;
};

export type JobCardProps = {
  job: Job;
  onEvent: (id: string, event: SSEEvent) => void;
  onRemove: (id: string) => void;
};

export type JobListProps = {
  jobs: Job[];
  onEvent: (id: string, event: SSEEvent) => void;
  onRemove: (id: string) => void;
};

export type UrlPanelProps = {
  onJobAdded: (job: Job) => void;
};

export type PlaylistModalProps = {
  open: boolean;
  onClose: () => void;
  title: string;
  items: PlaylistItem[];
  loading: boolean;
  error: string | null;
  onDownload: (selected: PlaylistItem[], quality: DownloadQuality) => void;
};

export type ProvidersProps = {
  children: React.ReactNode;
};

export type FieldProps = {
  label: string;
  children: React.ReactNode;
};
