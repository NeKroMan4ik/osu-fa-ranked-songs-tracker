"""
Output format per track:
{
  "title": "...",
  "ranked_modes": ["mania", "osu"],
  "beatmapset_ids_by_mode": {
    "mania": [2449706],
    "osu": [1987654]
  }
}
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from ossapi import Ossapi

from parser import HtmlClient
from config import SEARCH_DELAY
from api_beatmapset_search import find_ranked_beatmapsets

def build_artist_record(
    html_client: HtmlClient,
    api: Ossapi,
    raw_artist: dict,
) -> dict:
    artist_id   = raw_artist["id"]
    artist_name = raw_artist["name"]

    print(f"  → {artist_name} (id={artist_id})", flush=True)

    track_titles = html_client.get_artist_tracks(artist_id)
    tracks: list[dict] = []

    for title in track_titles:
        all_ids, mode_to_ids = find_ranked_beatmapsets(api, artist_name, title)

        ranked_modes = sorted(mode_to_ids.keys())

        track_entry = {
            "title": title,
            "ranked_modes": ranked_modes,                # always list
            "beatmapset_ids_by_mode": mode_to_ids        # always dict
        }

        tracks.append(track_entry)

        time.sleep(SEARCH_DELAY)

    # sorted by ranked then title
    tracks.sort(key=lambda t: (0 if "ranked_modes" in t else 1, t["title"].lower()))

    return {
        "id": artist_id,
        "name": artist_name,
        "tracks": tracks,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
