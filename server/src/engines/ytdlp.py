from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path

from redis.asyncio import Redis

PROGRESS_RE = re.compile(r"download:\s*(\d+\.?\d*)%\|([^|]+)\|(\S+)")

YOUTUBE_DOMAINS = ("youtube.com", "youtu.be", "youtube-nocookie.com")
ANDROID_CLIENT_ARGS = ("--extractor-args", "youtube:player_client=android")
PROGRESS_TEMPLATE = (
    "download:%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s"
)
UNKNOWN_VALUES = ("UNKNOWN", "N/A")


def parse_progress_line(line: str) -> dict | None:
    """Parse a single yt-dlp ``--newline`` progress line into an SSE progress event."""
    match = PROGRESS_RE.search(line)
    if not match:
        return None
    percent_str, speed, eta = match.group(1), match.group(2).strip(), match.group(3).strip()
    try:
        percent = float(percent_str)
    except ValueError:
        return None
    if speed.upper() in UNKNOWN_VALUES or eta.upper() in UNKNOWN_VALUES:
        return None
    return {"type": "progress", "percent": percent, "speed": speed, "eta": eta}


def is_youtube(url: str) -> bool:
    return any(domain in url for domain in YOUTUBE_DOMAINS)


def build_yt_dlp_cmd(
    url: str,
    fmt: str,
    output_template: str,
    audio_only: bool = False,
    audio_format: str = "mp3",
    extra_args: list[str] | None = None,
) -> list[str]:
    """Build a yt-dlp argv list, applying the Android-client throttling bypass for YouTube."""
    cmd = ["yt-dlp", "--newline"]
    if is_youtube(url):
        cmd += list(ANDROID_CLIENT_ARGS)
    cmd += ["--progress-template", PROGRESS_TEMPLATE]
    if audio_only:
        cmd += ["-x", "--audio-format", audio_format, "-f", fmt]
    else:
        cmd += ["-f", fmt, "--merge-output-format", "mp4"]
    cmd += ["-o", output_template]
    if extra_args:
        cmd += extra_args
    cmd.append(url)
    return cmd


async def run_ytdlp(
    url: str,
    fmt: str,
    output_dir: Path,
    job_id: str,
    redis: Redis,
    audio_only: bool = False,
    audio_format: str = "mp3",
    extra_args: list[str] | None = None,
) -> Path:
    """Run yt-dlp as a subprocess, streaming parsed progress to the job's pub/sub channel."""
    cmd = build_yt_dlp_cmd(
        url=url,
        fmt=fmt,
        output_template=str(output_dir / "%(title)s.%(ext)s"),
        audio_only=audio_only,
        audio_format=audio_format,
        extra_args=extra_args,
    )

    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    async for raw_line in proc.stdout:
        event = parse_progress_line(raw_line.decode(errors="replace").strip())
        if event:
            await redis.publish(f"job:{job_id}", json.dumps(event))
    await proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp exited with code {proc.returncode}")

    files = [f for f in output_dir.iterdir() if f.is_file()]
    if not files:
        raise RuntimeError("yt-dlp produced no output file")
    return files[0]


async def dump_playlist_json(url: str) -> list[dict]:
    """Fetch flat playlist metadata as a list of raw yt-dlp JSON dicts (one per entry)."""
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", url]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr.decode(errors="replace").strip() or "yt-dlp failed")

    entries: list[dict] = []
    for line in stdout.decode(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries
