"""
Output format per track:
{
  "title": "...",
  "preview": "https://assets.ppy.sh/artists/...",
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
from config import SEARCH_DELAY, ARTIST_SEARCH_ALIASES
from api_beatmapset_search import find_ranked_beatmapsets


def build_artist_record(
    html_client: HtmlClient,
    api: Ossapi,
    raw_artist: dict,
) -> dict:
    artist_id   = raw_artist["id"]
    artist_name = raw_artist["name"]

    print(f"  → {artist_name} (id={artist_id})", flush=True)

    search_names   = ARTIST_SEARCH_ALIASES.get(artist_id, [artist_name])
    track_items    = html_client.get_artist_tracks(artist_id)
    track_previews = html_client.get_artist_track_previews(artist_id)
    tracks: list[dict] = []

    for track in track_items:
        title = track["title"]
        all_ids: list[int] = []
        mode_to_ids: dict[str, list[int]] = {}

    # Split "OtherArtist - TrackTitle" when the left part contains a collaboration keyword (feat./vs./×)

        if " - " in title:
            left, right = title.split(" - ", 1)
            left_lower = left.lower()
            has_collab_keyword = any(kw in left_lower for kw in ("feat.", "vs.", "×"))
            should_split = has_collab_keyword
        else:
            should_split = False

        if should_split:
            search_artist, search_title = left, right
            searches = [(search_artist, search_title)]
            if artist_id in ARTIST_SEARCH_ALIASES:
                searches += [
                    (name, search_title) for name in search_names
                    if name.lower() != search_artist.lower()
                ]
        else:
            searches = []
            for name in search_names:
                search_title = title
                prefix = f"{name} - "
                if search_title.lower().startswith(prefix.lower()):
                    search_title = search_title[len(prefix):]
                searches.append((name, search_title))

        for s_artist, s_title in searches:
            print(f"    searching: artist={s_artist!r} title={s_title!r}", flush=True)
            ids, modes = find_ranked_beatmapsets(api, s_artist, s_title)
            all_ids.extend(ids)
            for mode, beatmapset_ids in modes.items():
                mode_to_ids.setdefault(mode, []).extend(beatmapset_ids)
            time.sleep(SEARCH_DELAY)

        # deduplicate
        all_ids = sorted(set(all_ids))
        for mode in mode_to_ids:
            mode_to_ids[mode] = sorted(set(mode_to_ids[mode]))

        ranked_modes = sorted(mode_to_ids.keys())

        tracks.append({
            "title": title,
            "preview": track_previews.get(title, ""),
            "ranked_modes": ranked_modes,
            "beatmapset_ids_by_mode": mode_to_ids,
        })

    # sorted by ranked then title
    tracks.sort(key=lambda t: (0 if t["ranked_modes"] else 1, t["title"].lower()))

    return {
        "id": artist_id,
        "name": artist_name,
        "tracks": tracks,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }