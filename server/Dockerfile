# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.13

# ── builder ──────────────────────────────────────────────────────────────────
# Resolve + install main deps (and the bgutil PO-token plugin) into the system
# site-packages. Build tooling (poetry, compilers) stays in this stage only.
FROM python:${PYTHON_VERSION}-slim AS builder
ENV PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false
RUN pip install poetry==2.4.1
WORKDIR /build
COPY pyproject.toml poetry.lock ./
# --only main: no pytest/httpx in the shipped deps. Lockfile => reproducible.
RUN poetry install --only main --no-root
RUN pip install bgutil-ytdlp-pot-provider \
    || echo "WARN: bgutil PO-token provider not installed (offline build?); set YOUTUBE_PO_TOKEN manually"

# ── test ─────────────────────────────────────────────────────────────────────
# Adds dev deps + source and runs the suite during build, so CI can gate simply
# with `docker build --target test` (a red test => a failed build).
FROM builder AS test
RUN poetry install --with dev --no-root
WORKDIR /app
COPY . .
RUN pytest -q

# ── runtime ──────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime
ARG YTDLP_VERSION=latest
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ffmpeg (+ aria2 for segmented downloads) and the yt-dlp binary. Retry rides out
# transient Debian mirror "Hash Sum mismatch" hiccups; curl is removed after use.
RUN set -eux; \
    for i in 1 2 3; do \
      rm -rf /var/lib/apt/lists/*; \
      apt-get update -o Acquire::Retries=3 \
      && apt-get install -y --no-install-recommends ffmpeg aria2 curl \
      && break; \
      echo "apt attempt $i failed; retrying..."; sleep 5; \
    done; \
    if [ "$YTDLP_VERSION" = "latest" ]; then \
      url="https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"; \
    else \
      url="https://github.com/yt-dlp/yt-dlp/releases/download/${YTDLP_VERSION}/yt-dlp"; \
    fi; \
    curl -fL "$url" -o /usr/local/bin/yt-dlp && chmod +x /usr/local/bin/yt-dlp; \
    apt-get purge -y curl && apt-get autoremove -y; \
    rm -rf /var/lib/apt/lists/*

# Bring the installed deps over from the builder; leave poetry/compilers behind.
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
# Re-fetch yt-dlp last so the site-packages copy above can't clobber it.
RUN [ -x /usr/local/bin/yt-dlp ] || (echo "yt-dlp missing" && exit 1)

WORKDIR /app
COPY . .

EXPOSE 8000
# Dev compose overrides this (uvicorn --reload / arq worker). Sensible prod default:
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
