from __future__ import annotations

import json
import os
import sys

from dotenv import load_dotenv
from ossapi import Ossapi

from parser import HtmlClient
from config import OUT_PATH
from build import build_artist_record


load_dotenv()


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
            results.append(build_artist_record(html_client, api, raw))
        except Exception as exc:
            print(f"✗ {raw['name']} → {exc}", file=sys.stderr)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # merge with the existing file by id
    existing = {}
    if OUT_PATH.exists():
        try:
            data = json.loads(OUT_PATH.read_text(encoding="utf-8"))
            existing = {a["id"]: a for a in data if isinstance(a, dict) and "id" in a}
        except Exception:
            pass

    for new in results:
        existing[new["id"]] = new

    final_list = list(existing.values())

    OUT_PATH.write_text(
        json.dumps(final_list, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


    print(f"\n✓ Wrote {OUT_PATH}")


if __name__ == "__main__":
    run()