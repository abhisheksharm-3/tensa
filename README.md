# Tensa

A comprehensive video toolkit for downloading, extracting audio, transcribing, and converting videos.

## Features

- **Download** — YouTube, Instagram, TikTok, Twitter, and more
- **Playlist** — Download entire playlists as video or audio
- **Audio Extract** — MP3, WAV, FLAC, AAC, OGG
- **Transcribe** — Speech-to-text with SRT, VTT, TXT output (Whisper)
- **Convert** — Format conversion, trimming, thumbnail extraction

## Quick Start

```bash
# Install dependencies
npm run install:all

# Start both server and client
npm run dev
```

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Prerequisites

- Node.js 18+
- Python 3.11+
- Poetry
- FFmpeg (system dependency)
- Bun (optional, for faster frontend)

## Project Structure

```
Tensa/
├── server/          # FastAPI backend
│   └── src/
│       ├── features/
│       │   ├── download/
│       │   ├── audio/
│       │   ├── transcribe/
│       │   └── convert/
│       └── core/
└── client/          # Next.js frontend
    ├── src/app/     # Pages
    └── src/features/
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start both server and client |
| `npm run dev:server` | Start backend only |
| `npm run dev:client` | Start frontend only |
| `npm run install:all` | Install all dependencies |

## Tech Stack

**Backend**: FastAPI, Poetry, yt-dlp, ffmpeg-python, OpenAI Whisper  
**Frontend**: Next.js 16, React Query, shadcn/ui, Tailwind CSS
