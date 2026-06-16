from __future__ import annotations

import asyncio
from pathlib import Path

from src.config import settings

TRANSCRIPT_EXTENSIONS = {"txt": ".txt", "srt": ".srt", "vtt": ".vtt"}


async def run_whisper(
    audio_path: Path,
    output_dir: Path,
    model: str,
    language: str | None,
    output_format: str,
) -> Path:
    """Transcribe an audio file with the Whisper CLI, returning the generated transcript path."""
    cmd = [
        "whisper",
        str(audio_path),
        "--model", model,
        "--output_format", output_format,
        "--output_dir", str(output_dir),
        "--model_dir", str(settings.whisper_models_dir),
        "--fp16", "False",
    ]
    if language:
        cmd += ["--language", language]

    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    try:
        await proc.communicate()
    finally:
        if proc.returncode is None:
            proc.kill()
            await proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"whisper exited with code {proc.returncode}")

    extension = TRANSCRIPT_EXTENSIONS.get(output_format, ".txt")
    output_file = output_dir / f"{audio_path.stem}{extension}"
    if not output_file.exists():
        raise RuntimeError("Whisper produced no output file")
    return output_file
