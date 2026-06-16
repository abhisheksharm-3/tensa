# Tensa

Self-hosted, ad-free media toolkit. Paste a URL from YouTube, Instagram, TikTok,
Facebook, or X (or upload a file) and download it as video/audio, extract audio,
convert formats, or transcribe it — with live progress and no ad-plagued sites.

## Features

- **Download** — video or audio, highest quality, from 1800+ sites via yt-dlp
- **Playlist** — fetch a YouTube playlist and download all or selected items
- **Audio extract** — MP3 / WAV / FLAC / AAC / OGG at a chosen bitrate (URL or upload)
- **Convert** — MP4 / WebM / MKV / MOV / GIF, codec, CRF, trim, scale (upload)
- **Transcribe** — Whisper → TXT / SRT / VTT (URL or upload)

## Architecture

Jobs are async. FastAPI enqueues work onto an ARQ queue; workers run
yt-dlp/ffmpeg/Whisper as **subprocesses** (crash-isolated, independently
updatable) and publish progress to Redis Pub/Sub. The API streams that to the
browser over SSE.

```
browser ──HTTP──> FastAPI (api) ──enqueue──> Redis ──> ARQ worker
   ▲                  │                        │          │ yt-dlp / ffmpeg / whisper
   └──────SSE─────────┘   <──── pub/sub job:{id} ─────────┘
```

### Backend layout — one responsibility per file

```
server/src/
├── engines/        external-tool I/O only
│   ├── ytdlp.py        argv builder + progress parser + runner + playlist dump
│   ├── ffmpeg.py       generic ffmpeg runner
│   └── whisper.py      whisper CLI runner
├── features/{download,playlist,audio,convert,transcribe}/
│   ├── constants.py    format/codec/quality maps
│   ├── service.py      business logic (produce the output file)
│   └── task.py         thin ARQ adapter -> core.job_execution.execute_job
├── core/
│   ├── job_execution.py  shared lifecycle: running -> produce -> done/cleanup
│   ├── redis.py          client + pub/sub + status helpers
│   ├── sse.py            SSE StreamingResponse
│   ├── files.py          job dirs, serving, delayed delete + sweeper
│   └── rate_limit.py     Redis-backed slowapi limiter (fail-open)
├── jobs/             routing + schemas + enqueue/cancel service
├── main.py           app factory
└── worker.py         ARQ WorkerSettings + 30-min sweeper cron
```

Constants, types (Pydantic schemas), business logic, external-tool/repo I/O, and
routing are each isolated. The same separation holds on the client (`types/`,
`constants/`, `hooks/`, `lib/`, `components/` with prop types in `components/types.ts`).

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build -d
```

- Frontend: http://localhost:3000
- API: http://localhost:8000  ·  health: `/api/health`

## Local dev

```bash
# backend (needs Redis, ffmpeg, yt-dlp on PATH)
cd server && poetry install && poetry run uvicorn src.main:app --reload
cd server && poetry run arq src.worker.WorkerSettings        # worker

# frontend
cd client && bun install && bun run dev
```

## API

```
POST   /api/jobs                 enqueue a job -> { job_id }
GET    /api/jobs/{id}/stream     SSE progress (progress | done | error | cancelled)
GET    /api/jobs/{id}            status (SSE fallback / polling)
DELETE /api/jobs/{id}            cancel
GET    /api/files/{id}/{name}    download the output (path-traversal guarded)
POST   /api/upload               store an uploaded file -> { upload_path }
POST   /api/playlist/info        playlist metadata (no download)
GET    /api/health
```

## YouTube reliability (other platforms need none of this)

yt-dlp gets **full CDN speed** because it solves YouTube's `n` throttle signature.
YouTube's newer anti-bot (PO tokens / SABR) can still interfere, so Tensa exposes
opt-in levers (set in `.env`):

| Var | Purpose |
|---|---|
| `YOUTUBE_COOKIES_FILE` | Netscape `cookies.txt` from a logged-in browser. Authenticates, lifts rate limits, unlocks age/region-locked videos. Most impactful. |
| `YOUTUBE_PLAYER_CLIENTS` | Comma list, e.g. `tv,web_safari`. Empty = yt-dlp's current default. |
| `YOUTUBE_PO_TOKEN` | Explicit `<client>+<token>` escape hatch. |

For automatic PO tokens, install the **bgutil PO-token provider** plugin in the
worker image. In Docker the `./server` dir is mounted at `/app`, so dropping
`server/cookies.txt` and setting `YOUTUBE_COOKIES_FILE=/app/cookies.txt` is enough.

> Services like vidssave look "effortless" only because they run server-side
> extraction behind **rotating residential proxies + PO-token solvers** and proxy
> the bytes through their own API. They extract the same CDN URLs yt-dlp does.
> For self-hosted personal use, cookies + yt-dlp is the right, simple approach.

## Tests

```bash
cd server && poetry run pytest      # 20 passing
cd client && bun run lint           # biome
```

## Tech stack

**Backend** Python 3.13 · FastAPI · ARQ · Redis · yt-dlp · ffmpeg · Whisper · slowapi · Poetry
**Frontend** Next.js 16 · React 19 · Tailwind v4 · shadcn/ui · TanStack Query · Biome · Bun
