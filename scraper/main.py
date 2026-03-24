from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from ossapi import Ossapi

from parser import HtmlClient
from config import ARTISTS_DIR, INDEX_PATH
from build import build_artist_record


load_dotenv()


def write_artist(artist: dict) -> None:
    ARTISTS_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTISTS_DIR / f"{artist['id']}.json"
    path.write_text(json.dumps(artist, ensure_ascii=False, indent=2), encoding="utf-8")


def write_index(artists: list[dict]) -> None:
    index = {
        "metadata": {
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_artists": len(artists),
            "total_songs": sum(len(a["tracks"]) for a in artists),
        },
        "artists": [
            {
                "id": a["id"],
                "name": a["name"],
                "song_count": len(a["tracks"]),
                "ranked_count": sum(1 for t in a["tracks"] if t.get("ranked_modes")),
                "updated_at": a["updated_at"],
            }
            for a in sorted(artists, key=lambda x: x["name"].lower())
        ],
    }
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def run() -> None:
    client_id     = os.environ.get("OSU_CLIENT_ID")
    client_secret = os.environ.get("OSU_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: OSU_CLIENT_ID and OSU_CLIENT_SECRET required", file=sys.stderr)
        sys.exit(1)

    html_client = HtmlClient()
    api         = Ossapi(int(client_id), client_secret)

    print("Fetching Featured Artist list…", flush=True)
    raw_artists = html_client.get_featured_artists()
    print(f"Found {len(raw_artists)} Featured Artists.\n", flush=True)

    results: list[dict] = []

    for i, raw in enumerate(raw_artists, 1):
        print(f"[{i}/{len(raw_artists)}] ", end="", flush=True)
        try:
            artist = build_artist_record(html_client, api, raw)
            write_artist(artist)
            results.append(artist)
        except Exception as exc:
            print(f"✗ {raw['name']} → {exc}", file=sys.stderr)

    write_index(results)

    print(f"\n✓ Wrote {len(results)} artist files + {INDEX_PATH}")


if __name__ == "__main__":
    run()