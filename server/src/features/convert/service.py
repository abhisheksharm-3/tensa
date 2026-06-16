from __future__ import annotations

from pathlib import Path

from redis.asyncio import Redis

from src.core.redis import publish_event
from src.engines.ffmpeg import run_ffmpeg
from src.features.convert.constants import (
    AUDIO_CODEC,
    CODEC_MAP,
    DEFAULT_CODEC,
    DEFAULT_CRF,
    GIF_FILTER,
    GIF_FORMAT,
)


def _build_convert_args(input_path: Path, output_path: Path, params: dict) -> list[str]:
    video_format = params.get("video_format", "mp4")
    trim_start = params.get("trim_start")
    trim_end = params.get("trim_end")
    scale_width = params.get("scale_width")

    args = ["-y"]
    if trim_start is not None:
        args += ["-ss", str(trim_start)]
    args += ["-i", str(input_path)]
    if trim_end is not None:
        duration = trim_end - trim_start if trim_start is not None else trim_end
        args += ["-t", str(duration)]

    if video_format == GIF_FORMAT:
        args += ["-vf", GIF_FILTER, "-loop", "0"]
    else:
        codec = CODEC_MAP.get(params.get("codec", "h264"), DEFAULT_CODEC)
        args += ["-vcodec", codec, "-crf", str(params.get("crf", DEFAULT_CRF))]
        if scale_width:
            args += ["-vf", f"scale={scale_width}:-2"]
        args += ["-acodec", AUDIO_CODEC]

    args.append(str(output_path))
    return args


async def produce_convert(redis: Redis, job_id: str, params: dict, job_dir: Path) -> Path:
    """Convert an uploaded video to the requested format/codec with ffmpeg."""
    input_path = Path(params["input_path"])
    video_format = params.get("video_format", "mp4")
    output_file = job_dir / f"{input_path.stem}_converted.{video_format}"

    await run_ffmpeg(_build_convert_args(input_path, output_file, params))
    await publish_event(job_id, {"type": "progress", "percent": 100.0, "speed": "—", "eta": "done"})
    return output_file
