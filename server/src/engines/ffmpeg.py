from __future__ import annotations

import asyncio


async def run_ffmpeg(args: list[str]) -> None:
    """Run an ffmpeg invocation to completion, raising on a non-zero exit.

    Callers pass the full argument list after the ``ffmpeg`` binary (the leading
    ``-y`` and trailing output path included); command construction is the caller's
    responsibility since it is feature-specific.
    """
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")
