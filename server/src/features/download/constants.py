DEFAULT_FORMAT = "bestvideo+bestaudio/best"
AUDIO_QUALITY = "audio"

QUALITY_FORMAT_MAP = {
    "best": DEFAULT_FORMAT,
    "1080p": "bestvideo[height<=1080]+bestaudio/best",
    "720p": "bestvideo[height<=720]+bestaudio/best",
    "audio": "bestaudio[ext=m4a]",
}
