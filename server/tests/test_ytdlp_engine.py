import pytest

from src.engines.ytdlp import build_yt_dlp_cmd, parse_progress_line


def test_parse_progress_line_valid():
    # yt-dlp emits the template with our sentinel, without a "download:" prefix
    # (that prefix is consumed by yt-dlp as the progress-type selector).
    result = parse_progress_line("TENSA_DL| 67.2%|8.4MiB/s|00:00:12")
    assert result is not None
    assert result["type"] == "progress"
    assert result["percent"] == pytest.approx(67.2)
    assert result["speed"] == "8.4MiB/s"
    assert result["eta"] == "00:00:12"


def test_parse_progress_line_invalid():
    assert parse_progress_line("[download] Destination: video.mp4") is None
    assert parse_progress_line("") is None
    assert parse_progress_line("TENSA_DL| NA%|Unknown|Unknown") is None


def test_build_cmd_injects_cookies_and_clients_for_youtube(monkeypatch, tmp_path):
    cookies = tmp_path / "cookies.txt"
    cookies.write_text("# netscape")
    monkeypatch.setattr("src.engines.ytdlp.settings.youtube_cookies_file", cookies)
    monkeypatch.setattr("src.engines.ytdlp.settings.youtube_player_clients", "tv,web_safari")

    cmd = build_yt_dlp_cmd(
        url="https://www.youtube.com/watch?v=abc",
        fmt="bestvideo+bestaudio/best",
        output_template="/tmp/%(title)s.%(ext)s",
    )
    assert cmd[cmd.index("--cookies") + 1] == str(cookies)
    assert "youtube:player_client=tv,web_safari" in cmd[cmd.index("--extractor-args") + 1]


def test_build_cmd_no_youtube_args_for_instagram(monkeypatch, tmp_path):
    cookies = tmp_path / "cookies.txt"
    cookies.write_text("# netscape")
    monkeypatch.setattr("src.engines.ytdlp.settings.youtube_cookies_file", cookies)

    cmd = build_yt_dlp_cmd(
        url="https://www.instagram.com/reel/abc/",
        fmt="bestvideo+bestaudio/best",
        output_template="/tmp/%(title)s.%(ext)s",
    )
    assert "--cookies" not in cmd
    assert "--extractor-args" not in cmd


def test_build_cmd_youtube_unconfigured_stays_default():
    cmd = build_yt_dlp_cmd(
        url="https://youtu.be/abc",
        fmt="bestvideo+bestaudio/best",
        output_template="/tmp/%(title)s.%(ext)s",
    )
    assert "--cookies" not in cmd
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
