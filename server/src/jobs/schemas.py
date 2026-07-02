from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class JobType(StrEnum):
    DOWNLOAD = "download"
    PLAYLIST_ITEM = "playlist_item"
    AUDIO_EXTRACT = "audio_extract"
    CONVERT = "convert"
    TRANSCRIBE = "transcribe"


class DownloadQuality(StrEnum):
    BEST = "best"
    P1080 = "1080p"
    P720 = "720p"
    AUDIO = "audio"


class AudioFormat(StrEnum):
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"


class AudioBitrate(StrEnum):
    K128 = "128k"
    K192 = "192k"
    K256 = "256k"
    K320 = "320k"


class VideoFormat(StrEnum):
    MP4 = "mp4"
    WEBM = "webm"
    MKV = "mkv"
    MOV = "mov"
    GIF = "gif"


class WhisperModel(StrEnum):
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class TranscriptFormat(StrEnum):
    TXT = "txt"
    SRT = "srt"
    VTT = "vtt"


class JobRequest(BaseModel):
    type: JobType
    url: str | None = None
    quality: DownloadQuality = DownloadQuality.BEST
    audio_format: AudioFormat = AudioFormat.MP3
    audio_bitrate: AudioBitrate = AudioBitrate.K192
    video_format: VideoFormat = VideoFormat.MP4
    whisper_model: WhisperModel = WhisperModel.BASE
    transcript_format: TranscriptFormat = TranscriptFormat.SRT
    language: str | None = None
    trim_start: float | None = None
    trim_end: float | None = None
    scale_width: int | None = None
    input_path: str | None = None
    # Additive: embed subtitles into video downloads, and remove sponsor segments
    # via SponsorBlock. Both apply only to download / playlist_item jobs.
    embed_subs: bool = False
    sponsorblock: bool = False


class JobResponse(BaseModel):
    job_id: str


class UploadResponse(BaseModel):
    upload_path: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    message: str | None = None
    download_url: str | None = None
    file_size: int | None = None
    # Additive fields — the four required keys above are unchanged.
    error: str | None = None
    type: str | None = None
