DEFAULT_BITRATE_FORMAT = "bestaudio"

BITRATE_FORMAT_MAP = {
    "128k": "bestaudio[abr<=128]",
    "192k": "bestaudio[abr<=192]",
    "256k": "bestaudio[abr<=256]",
    "320k": "bestaudio",
}

DEFAULT_CODEC = "libmp3lame"

FORMAT_CODEC_MAP = {
    "mp3": "libmp3lame",
    "aac": "aac",
    "wav": "pcm_s16le",
    "flac": "flac",
    "ogg": "libvorbis",
}
