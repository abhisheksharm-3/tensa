FROM python:3.13-slim

# apt with CDN-cache bypass + retry: Debian mirrors occasionally serve a .deb
# whose hash doesn't match the fresh index ("Hash Sum mismatch"), which fails
# the build nondeterministically. No-Cache forces revalidation past stale CDN
# edges; the retry loop rides out transient mirror inconsistencies.
RUN set -eux; \
    for i in 1 2 3; do \
      rm -rf /var/lib/apt/lists/*; \
      apt-get update -o Acquire::http::No-Cache=true -o Acquire::Retries=3 \
      && apt-get install -y --no-install-recommends \
         -o Acquire::http::No-Cache=true -o Acquire::Retries=3 \
         ffmpeg aria2 curl \
      && break; \
      echo "apt attempt $i failed; retrying..."; sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp \
    && chmod +x /usr/local/bin/yt-dlp

WORKDIR /app

RUN pip install poetry==1.8.3
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry lock --no-interaction \
    && poetry install --no-interaction --no-ansi

# bgutil PO-token provider — supplies YouTube PO tokens automatically so most
# downloads need no manual YOUTUBE_PO_TOKEN. Installed as the yt-dlp plugin that
# talks to the bgutil-ytdlp-pot-provider HTTP server (run that server as a
# sidecar; see docker-compose / README). Network at build time is required for
# this pip install; if the build runs fully offline, drop this line and set
# YOUTUBE_PO_TOKEN manually instead.
RUN pip install --no-cache-dir bgutil-ytdlp-pot-provider || \
    echo "WARN: bgutil PO-token provider not installed (offline build?); set YOUTUBE_PO_TOKEN manually"

COPY . .
