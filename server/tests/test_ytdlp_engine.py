import pytest

from src.engines.ytdlp import build_yt_dlp_cmd, is_youtube, parse_progress_line


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


def test_build_cmd_youtube_unconfigured_stays_default(monkeypatch):
    # With every YouTube lever unset (including the POT provider that the Docker
    # env wires up by default), no extractor args should be added.
    monkeypatch.setattr("src.engines.ytdlp.settings.youtube_player_clients", "")
    monkeypatch.setattr("src.engines.ytdlp.settings.youtube_po_token", None)
    monkeypatch.setattr("src.engines.ytdlp.settings.youtube_pot_provider_url", "")
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


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.youtube.com/watch?v=abc", True),
        ("https://youtu.be/abc", True),
        ("https://m.youtube.com/watch?v=abc", True),
        ("https://www.youtube-nocookie.com/embed/abc", True),
        # Spoofs that the old substring check would have wrongly matched:
        ("https://youtube.com.evil.com/watch?v=abc", False),
        ("https://evil.com/?next=https://youtube.com", False),
        ("https://notyoutube.com/abc", False),
        ("https://www.instagram.com/reel/abc/", False),
    ],
)
def test_is_youtube_matches_hostname_not_substring(url, expected):
    assert is_youtube(url) is expected


def test_build_cmd_applies_production_defaults(monkeypatch):
    monkeypatch.setattr("src.engines.ytdlp.settings.max_download_filesize", "4G")
    cmd = build_yt_dlp_cmd(
        url="https://youtu.be/abc",
        fmt="bestvideo+bestaudio/best",
        output_template="/tmp/%(title)s.%(ext)s",
    )
    assert "--no-playlist" in cmd
    assert cmd[cmd.index("--max-filesize") + 1] == "4G"
    assert cmd[cmd.index("--retries") + 1] == "10"
    assert cmd[cmd.index("--fragment-retries") + 1] == "10"
    assert cmd[cmd.index("-N") + 1] == "4"
    # Video downloads embed metadata/thumbnail/chapters by default.
    assert "--embed-metadata" in cmd
    assert "--embed-thumbnail" in cmd
    assert "--embed-chapters" in cmd
    # Format sorting for predictable quality.
    assert "-S" in cmd
    # Opt-in flags off by default.
    assert "--embed-subs" not in cmd
    assert "--sponsorblock-remove" not in cmd


def test_build_cmd_aria2c_when_present(monkeypatch):
    monkeypatch.setattr("src.engines.ytdlp.shutil.which", lambda _: "/usr/bin/aria2c")
    cmd = build_yt_dlp_cmd(
        url="https://youtu.be/abc",
        fmt="bestvideo+bestaudio/best",
        output_template="/tmp/%(title)s.%(ext)s",
    )
    assert cmd[cmd.index("--downloader") + 1] == "aria2c"
    assert "aria2c:-x16 -s16 -k1M" in cmd[cmd.index("--downloader-args") + 1]


def test_build_cmd_aria2c_graceful_fallback(monkeypatch):
    monkeypatch.setattr("src.engines.ytdlp.shutil.which", lambda _: None)
    cmd = build_yt_dlp_cmd(
        url="https://youtu.be/abc",
        fmt="bestvideo+bestaudio/best",
        output_template="/tmp/%(title)s.%(ext)s",
    )
    assert "--downloader" not in cmd


def test_build_cmd_embed_subs_and_sponsorblock_opt_in():
    cmd = build_yt_dlp_cmd(
        url="https://youtu.be/abc",
        fmt="bestvideo+bestaudio/best",
        output_template="/tmp/%(title)s.%(ext)s",
        embed_subs=True,
        sponsorblock=True,
    )
    assert "--embed-subs" in cmd
    assert cmd[cmd.index("--sponsorblock-remove") + 1] == "default"
