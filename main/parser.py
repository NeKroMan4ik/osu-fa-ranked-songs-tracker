from __future__ import annotations

import json
import requests
from bs4 import BeautifulSoup

from config import BASE_URL

class HtmlClient:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({"Accept": "text/html,application/json"})

    def _get_html(self, path: str) -> BeautifulSoup:
        resp = self._session.get(f"{BASE_URL}{path}", timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def get_featured_artists(self) -> list[dict]:
        soup = self._get_html("/beatmaps/artists")
        artists = []

        for box in soup.select("div.artist__box"):
            a = box.select_one("a.artist__name")
            count_div = box.select_one("div.artist__track-count")
            if not a or not count_div:
                continue
            name = a.get_text(strip=True)
            href = a.get("href", "")
            try:
                artist_id = int(href.rstrip("/").split("/")[-1])
                song_count = int(count_div.get_text(strip=True).split()[0])
                artists.append({"id": artist_id, "name": name, "song_count": song_count})
            except (ValueError, IndexError):
                continue

        if not artists:
            raise RuntimeError("Parsed 0 artists — HTML structure changed?")
        return artists

    def get_artist_tracks(self, artist_id: int) -> list[dict]:
        soup = self._get_html(f"/beatmaps/artists/{artist_id}")
        seen: set[str] = set()
        tracks: list[dict] = []
        for script in soup.find_all("script", {"type": "application/json"}):
            sid = script.get("id", "")
            if not (sid.startswith("album-json-") or sid.startswith("singles-json-")):
                continue
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else data.get("tracks", [])
                for t in items:
                    title = (t or {}).get("title", "").strip()
                    track_artist_id = (t or {}).get("artist_id")
                    if title and title not in seen:
                        seen.add(title)
                        tracks.append({"title": title, "artist_id": track_artist_id})
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        return sorted(tracks, key=lambda t: t["title"])

    def get_artist_track_previews(self, artist_id: int) -> dict[str, str]:
        soup = self._get_html(f"/beatmaps/artists/{artist_id}")
        previews = {}
        for script in soup.find_all("script", {"type": "application/json"}):
            sid = script.get("id", "")
            if not (sid.startswith("album-json-") or sid.startswith("singles-json-")):
                continue
            try:
                data = json.loads(script.string or "")
                tracks = data if isinstance(data, list) else data.get("tracks", [])
                for t in tracks:
                    title = (t or {}).get("title", "").strip()
                    preview = (t or {}).get("preview", "").strip()
                    if title and preview:
                        previews[title] = preview
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        return previews