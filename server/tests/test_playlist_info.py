from unittest.mock import AsyncMock, patch

import pytest

from src.features.playlist.schemas import PlaylistItem


@pytest.mark.anyio
async def test_playlist_info_returns_items(client):
    with patch("src.features.playlist.router.fetch_playlist_info", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = [
            PlaylistItem(id="vid1", title="Episode 1", duration=300, thumbnail="https://i/vid1.jpg"),
            PlaylistItem(id="vid2", title="Episode 2", duration=420, thumbnail="https://i/vid2.jpg"),
        ]
        resp = await client.post("/api/playlist/info", json={"url": "https://youtube.com/playlist?list=abc"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["title"] == "Episode 1"
    assert data["items"][0]["duration"] == 300


@pytest.mark.anyio
async def test_playlist_info_invalid_url(client):
    with patch("src.features.playlist.router.fetch_playlist_info", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = RuntimeError("Not a playlist URL")
        resp = await client.post("/api/playlist/info", json={"url": "https://youtube.com/watch?v=single"})
    assert resp.status_code == 422
