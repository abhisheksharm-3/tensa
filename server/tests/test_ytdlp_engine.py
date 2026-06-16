import pytest

from src.engines.ytdlp import build_yt_dlp_cmd, parse_progress_line


def test_parse_progress_line_valid():
    result = parse_progress_line("download: 67.2%|8.4MiB/s|00:00:12")
    assert result is not None
    assert result["type"] == "progress"
    assert result["percent"] == pytest.approx(67.2)
    assert result["speed"] == "8.4MiB/s"
    assert result["eta"] == "00:00:12"


def test_parse_progress_line_invalid():
    assert parse_progress_line("[download] Destination: video.mp4") is None
    assert parse_progress_line("") is None
    assert parse_progress_line("download: NA%|Unknown|Unknown") is None


def test_build_cmd_adds_android_flag_for_youtube():
    cmd = build_yt_dlp_cmd(
        url="https://www.youtube.com/watch?v=abc",
        fmt="bestvideo+bestaudio/best",
        output_template="/tmp/%(title)s.%(ext)s",
    )
    assert "--extractor-args" in cmd
    assert "android" in cmd[cmd.index("--extractor-args") + 1]


def test_build_cmd_no_android_flag_for_instagram():
    cmd = build_yt_dlp_cmd(
        url="https://www.instagram.com/reel/abc/",
        fmt="bestvideo+bestaudio/best",
        output_template="/tmp/%(title)s.%(ext)s",
    )
    assert "--extractor-args" not in cmd


def test_build_cmd_audio_uses_extract_flag():
    cmd = build_yt_dlp_cmd(
        url="https://youtu.be/abc",
        fmt="bestaudio[ext=m4a]",
        output_template="/tmp/%(title)s.%(ext)s",
        audio_only=True,
        audio_format="mp3",
    )
    assert "-x" in cmd
    assert cmd[cmd.index("--audio-format") + 1] == "mp3"
