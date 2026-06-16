from __future__ import annotations

import asyncio
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

from redis.asyncio import Redis

from src.config import settings
from src.core.files import get_job_output_file

PROGRESS_RE = re.compile(r"TENSA_DL\|\s*(\d+\.?\d*)%\|([^|]+)\|(\S+)")

YOUTUBE_DOMAINS = ("youtube.com", "youtu.be", "youtube-nocookie.com")
# Per yt-dlp docs, --progress-template is "optionally prefixed with one of
# 'download:' (default) ... 'postprocess:' ...". That prefix is a TYPE *selector*
# consumed by yt-dlp, never printed. So a literal "download:" never appears in
# output; we emit our own "TENSA_DL|" sentinel inside the template and key the
# parser off it. https://github.com/yt-dlp/yt-dlp#:~:text=--progress-template
PROGRESS_TEMPLATE = (
    "download:TENSA_DL|%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s"
)
UNKNOWN_VALUES = ("UNKNOWN", "N/A")

# Production reliability knobs applied to every download.
_RELIABILITY_ARGS = [
    "--retries", "10",
    "--fragment-retries", "10",
    "--file-access-retries", "3",
    "--retry-sleep", "linear=1::2",
    "--socket-timeout", "30",
    "-N", "4",  # concurrent fragments
]
# Predictable quality ordering.
_FORMAT_SORT = ["-S", "res,fps,vcodec:h264,acodec:m4a"]


def _aria2c_args() -> list[str]:
    """External-downloader args if aria2c is on PATH, else empty (graceful fallback)."""
    if shutil.which("aria2c") is None:
        return []
    return ["--downloader", "aria2c", "--downloader-args", "aria2c:-x16 -s16 -k1M"]


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
    """True only when the URL's *host* is a known YouTube domain.

    Matching the parsed hostname (not a substring of the whole URL) prevents
    spoofs like https://youtube.com.evil.com/ or https://evil.com/?x=youtube.com.
    """
    host = (urlsplit(url).hostname or "").lower()
    if not host:
        return False
    return any(host == domain or host.endswith(f".{domain}") for domain in YOUTUBE_DOMAINS)


def youtube_args() -> list[str]:
    """yt-dlp args that harden YouTube extraction: cookies, player clients, PO token."""
    args: list[str] = []
    cookies = settings.youtube_cookies_file
    if cookies and cookies.exists():
        args += ["--cookies", str(cookies)]

    extractor_parts: list[str] = []
    if settings.youtube_player_clients:
        extractor_parts.append(f"player_client={settings.youtube_player_clients}")
    if settings.youtube_po_token:
        extractor_parts.append(f"po_token={settings.youtube_po_token}")
    if settings.youtube_pot_provider_url:
        # Point the bgutil PO-token plugin at the provider sidecar.
        extractor_parts.append(f"getpot_bgutil_baseurl={settings.youtube_pot_provider_url}")
    if extractor_parts:
        args += ["--extractor-args", f"youtube:{';'.join(extractor_parts)}"]
    return args


def build_yt_dlp_cmd(
    url: str,
    fmt: str,
    output_template: str,
    audio_only: bool = False,
    audio_format: str = "mp3",
    embed_subs: bool = False,
    sponsorblock: bool = False,
    extra_args: list[str] | None = None,
) -> list[str]:
    """Build a yt-dlp argv list with production-grade defaults.

    Applies YouTube hardening (cookies/clients/PO token), retries, concurrent
    fragments, an external aria2c downloader when available, a --max-filesize
    disk-safety ceiling, single-video mode, and (for video) metadata/thumbnail/
    chapter embedding. Subtitles and SponsorBlock are opt-in.
    """
    cmd = ["yt-dlp", "--newline", "--no-playlist"]
    if is_youtube(url):
        cmd += youtube_args()
    cmd += ["--progress-template", PROGRESS_TEMPLATE]
    cmd += _RELIABILITY_ARGS
    cmd += _aria2c_args()
    cmd += ["--max-filesize", settings.max_download_filesize]

    if audio_only:
        cmd += ["-x", "--audio-format", audio_format, "-f", fmt]
        cmd += ["--embed-metadata", "--embed-thumbnail"]
    else:
        cmd += ["-f", fmt, "--merge-output-format", "mp4"]
        cmd += _FORMAT_SORT
        cmd += ["--embed-metadata", "--embed-thumbnail", "--embed-chapters"]
        if embed_subs:
            cmd += ["--embed-subs", "--sub-langs", "all"]

    if sponsorblock:
        cmd += ["--sponsorblock-remove", "default"]

    cmd += ["-o", output_template]
    if extra_args:
        cmd += extra_args
    cmd.append(url)
    return cmd


async def _stream_and_wait(proc: asyncio.subprocess.Process, job_id: str, redis: Redis) -> None:
    """Stream progress lines to pub/sub; on cancellation/error, kill the subprocess.

    The kill in ``finally`` is what makes job cancellation and job_timeout actually
    stop yt-dlp (and any aria2c child) rather than leaking the process.
    """
    try:
        assert proc.stdout is not None
        async for raw_line in proc.stdout:
            event = parse_progress_line(raw_line.decode(errors="replace").strip())
            if event:
                await redis.publish(f"job:{job_id}", json.dumps(event))
        await proc.wait()
    finally:
        if proc.returncode is None:
            proc.kill()
            await proc.wait()


async def run_ytdlp(
    url: str,
    fmt: str,
    output_dir: Path,
    job_id: str,
    redis: Redis,
    audio_only: bool = False,
    audio_format: str = "mp3",
    embed_subs: bool = False,
    sponsorblock: bool = False,
    extra_args: list[str] | None = None,
) -> Path:
    """Run yt-dlp as a subprocess, streaming parsed progress to the job's pub/sub channel."""
    cmd = build_yt_dlp_cmd(
        url=url,
        fmt=fmt,
        output_template=str(output_dir / "%(title)s.%(ext)s"),
        audio_only=audio_only,
        audio_format=audio_format,
        embed_subs=embed_subs,
        sponsorblock=sponsorblock,
        extra_args=extra_args,
    )

    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    await _stream_and_wait(proc, job_id, redis)

    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp exited with code {proc.returncode}")

    output = get_job_output_file(output_dir)
    if output is None:
        raise RuntimeError("yt-dlp produced no output file")
    return output


async def dump_playlist_json(url: str) -> list[dict]:
    """Fetch flat playlist metadata as a list of raw yt-dlp JSON dicts (one per entry)."""
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings"]
    if is_youtube(url):
        cmd += youtube_args()
    cmd.append(url)
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


async def dump_video_metadata(url: str) -> dict:
    """Fetch a single media item's metadata (no download) as a raw yt-dlp JSON dict.

    Uses --flat-playlist so a playlist/channel URL resolves to its own header
    info quickly instead of probing every entry.
    """
    cmd = [
        "yt-dlp",
        "--dump-single-json",
        "--no-warnings",
        "--flat-playlist",
        "--no-download",
    ]
    if is_youtube(url):
        cmd += youtube_args()
    cmd.append(url)
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr.decode(errors="replace").strip() or "yt-dlp failed")
    try:
        return json.loads(stdout.decode(errors="replace"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("could not parse media metadata") from exc


def best_thumbnail(entry: dict) -> str | None:
    """Pick a usable thumbnail URL from a yt-dlp entry.

    Prefers an explicit thumbnail, then the largest from a thumbnails list, and
    finally synthesizes a YouTube thumbnail from the video id (flat-playlist
    entries often omit thumbnails but always carry the id).
    """
    thumb = entry.get("thumbnail")
    if thumb:
        return thumb
    thumbs = entry.get("thumbnails")
    if isinstance(thumbs, list) and thumbs:
        with_url = [t for t in thumbs if t.get("url")]
        if with_url:
            return with_url[-1]["url"]
    vid = entry.get("id")
    ie = (entry.get("ie_key") or entry.get("extractor") or "").lower()
    if vid and ("youtube" in ie or entry.get("webpage_url_domain", "").endswith("youtube.com")):
        return f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg"
    return None
