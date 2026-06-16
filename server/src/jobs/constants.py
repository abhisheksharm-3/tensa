# ARQ registers each worker function under its bare __qualname__ (see
# WorkerSettings.functions), so jobs must be enqueued by that same short name —
# not the dotted module path, which ARQ never sees.
TASK_MAP = {
    "download": "run_download",
    "playlist_item": "run_playlist_item",
    "audio_extract": "run_audio_extract",
    "convert": "run_convert",
    "transcribe": "run_transcribe",
}
