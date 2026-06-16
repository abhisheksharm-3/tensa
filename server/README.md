# Tensa Server

FastAPI backend for video processing. Async job pipeline: FastAPI enqueues work
onto an ARQ/Redis queue; workers run yt-dlp / ffmpeg / Whisper and stream progress
over Redis pub/sub (SSE). Job records are persisted durably in PostgreSQL.

## Setup

```bash
poetry install
```

## Run (local)

```bash
poetry run uvicorn src.main:app --reload      # API
poetry run arq src.worker.WorkerSettings      # worker
```

Server runs at http://localhost:8000. With no `DATABASE_URL` set, a local SQLite
file (`./tensa.db`) backs the job store, so the API/worker run without Postgres in
development.

## Run (Docker)

```bash
docker compose up --build
```

Brings up `redis`, `postgres`, `api`, `worker`, and `frontend`.

### Scaling workers

Workers are stateless and pull from the shared Redis queue — run as many as the
host allows:

```bash
docker compose up --scale worker=4
```

Per-worker concurrency is `WORKER_MAX_JOBS` (default 4); the per-job wall-clock
ceiling is `WORKER_JOB_TIMEOUT` (default 600s). No code assumes a single worker.

## API Endpoints

- `POST /api/jobs` — enqueue a job (see `JobRequest`)
- `GET /api/jobs/{id}` — job status (read from Postgres)
- `GET /api/jobs/{id}/stream` — SSE progress stream
- `DELETE /api/jobs/{id}` — cancel a job (aborts the running worker + kills yt-dlp/ffmpeg)
- `GET /api/files/{job_id}/{filename}` — download a finished file
- `POST /api/upload` — upload a source file (streamed, size + content-type enforced)
- `POST /api/playlist/info` — list playlist entries
- `GET /api/health` — health check
- `GET /metrics` — Prometheus metrics

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379` | ARQ queue + pub/sub + rate-limit storage |
| `DATABASE_URL` | `sqlite+aiosqlite:///./tensa.db` | Async SQLAlchemy DSN; use `postgresql+asyncpg://...` in prod |
| `DOWNLOAD_DIR` | `./downloads` | Output + uploads root |
| `WHISPER_MODELS_DIR` | `./models` | Whisper model cache |
| `RATE_LIMIT_PER_HOUR` | `20` | slowapi limit on `/jobs`, `/upload`, `/playlist/info` |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `WORKER_MAX_JOBS` | `4` | ARQ concurrency per worker |
| `WORKER_JOB_TIMEOUT` | `600` | Per-job timeout (seconds) |
| `MAX_DOWNLOAD_FILESIZE` | `4G` | **Disk-safety** yt-dlp `--max-filesize` ceiling |
| `MAX_UPLOAD_SIZE` | `2147483648` | Max upload bytes (2 GiB) |
| `LOG_LEVEL` | `INFO` | Log level |
| `LOG_JSON` | `true` | JSON logs (set `false` for console dev output) |
| `METRICS_ENABLED` | `true` | Expose `/metrics` + request middleware |
| `YOUTUBE_COOKIES_FILE` | _(unset)_ | Netscape cookies.txt — auth, higher limits, age/region unlock |
| `YOUTUBE_PLAYER_CLIENTS` | _(unset)_ | Comma-separated yt-dlp player clients |
| `YOUTUBE_PO_TOKEN` | _(unset)_ | Explicit PO token escape hatch |

## Production yt-dlp behavior

Every download is built with production defaults (see `engines/ytdlp.py`):

- **aria2c external downloader** (`-x16 -s16 -k1M`) when `aria2c` is on PATH;
  falls back to the native downloader if absent.
- **Concurrent fragments** (`-N 4`) and aggressive **retries**
  (`--retries 10 --fragment-retries 10 --file-access-retries 3 --retry-sleep --socket-timeout`).
- **Disk safety:** hard `--max-filesize` ceiling (`MAX_DOWNLOAD_FILESIZE`, default 4G).
  A prior multi-GB "Best" pull filled the disk and crashed Docker.
- **`--no-playlist`** for single-download jobs.
- **Format sorting** (`-S`) for predictable quality.
- Video downloads **embed** `--embed-metadata --embed-thumbnail --embed-chapters`
  by default; `--embed-subs` only when `embed_subs: true`.
- **SponsorBlock** (`--sponsorblock-remove default`) when `sponsorblock: true`.

### YouTube PO tokens (bgutil)

The worker image installs the **bgutil PO-token provider** plugin
(`bgutil-ytdlp-pot-provider`), which supplies YouTube PO tokens automatically so
most downloads need no manual `YOUTUBE_PO_TOKEN`. The plugin talks to a
`bgutil-ytdlp-pot-provider` HTTP server — run that as a sidecar in production. If
the image is built fully offline (the plugin's `pip install` is skipped), set
`YOUTUBE_PO_TOKEN` manually instead.

## Observability

- **Structured JSON logging** (structlog) across API and worker, with `job_id`
  bound into every log line for a running job.
- **Prometheus `/metrics`**: HTTP request count + latency histograms, and a
  `tensa_jobs_total{type,status}` counter for the job lifecycle.

## Security hardening

- **SSRF guard** (`core/url_safety.py`): job/playlist URLs must be http(s) and
  must not resolve to private/loopback/link-local/metadata/reserved addresses.
- **Path safety**: `input_path` is constrained under `DOWNLOAD_DIR`; served file
  paths require a UUID `job_id` and must resolve under `DOWNLOAD_DIR`.
- **Uploads** are streamed with aiofiles under a size ceiling and content-type
  allowlist.

## Dependencies

- FastAPI + Uvicorn, ARQ + Redis
- SQLAlchemy 2 (async) + asyncpg (Postgres) / aiosqlite (dev)
- yt-dlp + aria2 (video downloading), ffmpeg-python (A/V), OpenAI Whisper
- structlog, prometheus-client, slowapi

## System Requirements

FFmpeg and yt-dlp must be on PATH (installed in the Docker image). `aria2` is
optional but recommended for fast downloads.
