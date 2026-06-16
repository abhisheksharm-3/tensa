# Tensa Server

FastAPI backend for video processing.

## Setup

```bash
poetry install
```

## Run

```bash
poetry run uvicorn src.main:app --reload
```

Server runs at http://localhost:8000

## API Endpoints

### Download
- `GET /api/download/info?url=` — Get video info
- `GET /api/download/playlist/info?url=` — Get playlist info
- `POST /api/download/video` — Download video
- `POST /api/download/playlist` — Download playlist

### Audio
- `POST /api/audio/extract` — Extract from URL
- `POST /api/audio/extract/upload` — Extract from file

### Transcribe
- `POST /api/transcribe/url` — Transcribe from URL
- `POST /api/transcribe/upload` — Transcribe from file

### Convert
- `POST /api/convert/format` — Convert format
- `POST /api/convert/format/upload` — Convert uploaded file
- `POST /api/convert/trim` — Trim video
- `POST /api/convert/thumbnails` — Extract thumbnails

## Dependencies

- FastAPI + Uvicorn
- yt-dlp (video downloading)
- ffmpeg-python (audio/video processing)
- OpenAI Whisper (transcription)

## System Requirements

FFmpeg must be installed and available in PATH.
