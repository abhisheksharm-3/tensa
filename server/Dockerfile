FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp \
    && chmod +x /usr/local/bin/yt-dlp

WORKDIR /app

RUN pip install poetry==1.8.3
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry lock --no-interaction \
    && poetry install --no-interaction --no-ansi

COPY . .
