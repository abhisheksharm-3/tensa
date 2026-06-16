from __future__ import annotations

import asyncio


async def run_ffmpeg(args: list[str]) -> None:
    """Run an ffmpeg invocation to completion, raising on a non-zero exit.

    Callers pass the full argument list after the ``ffmpeg`` binary (the leading
    ``-y`` and trailing output path included); command construction is the caller's
    responsibility since it is feature-specific. On cancellation or timeout the
    subprocess is killed so it does not outlive the job.
    """
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    try:
        await proc.communicate()
    finally:
        if proc.returncode is None:
            proc.kill()
            await proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")
