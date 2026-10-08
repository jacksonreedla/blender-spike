"""Phase A: harvest full-channel metadata for the three reference channels, then sample.

Read-only Data API calls with ClipVault's channel token, held IN MEMORY: load_creds()
builds credentials from rs_token.json and nothing here writes the token back. Never
search.list (100 units). Cost: 1 unit per channels.list / playlistItems page /
videos.list batch, ~280 for all three channels. Raw API items are cached in
study/raw/<slug>.json so re-sampling spends no quota (--refresh to re-fetch).

Outputs: study/videos.jsonl (every upload, flat rows) and study/sample.json.
Run with ClipVault's venv:  /home/apollo/clipvault/.venv/bin/python study/harvest.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, "/home/apollo/clipvault")
import sample as S  # noqa: E402

CHANNELS = {"zackdfilms": "UCvz84_Q0BbvZThy75mbd-Dg",
            "hisstory": "UCrwSMlDM6FGLwHOtZ5JZpVA",
            "herstory": "UCpHpLD-URpThtttHTxefZ4A"}
RAW = HERE / "raw"


def _exec(req, quota: list, tries: int = 6):
    """execute() with backoff on YouTube's transient 5xx (backendError mid-pagination).
    Every attempt is counted against quota; 4xx is raised at once."""
    import time
    from googleapiclient.errors import HttpError
    for attempt in range(tries):
        quota[0] += 1
        try:
            return req.execute()
        except HttpError as e:
            if e.resp.status < 500 or attempt == tries - 1:
                raise
            wait = 2 ** (attempt + 1)
            print(f"    {e.resp.status} from YouTube, retry {attempt + 1}/{tries - 1} in {wait}s", flush=True)
            time.sleep(wait)


def fetch_channel(svc, channel_id: str, quota: list) -> dict:
    ch = _exec(svc.channels().list(part="snippet,statistics,contentDetails", id=channel_id), quota)
    item = (ch.get("items") or [None])[0]
    if not item:
        raise RuntimeError(f"channel {channel_id} not found")
    uploads = item["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while True:
        page = _exec(svc.playlistItems().list(part="contentDetails", playlistId=uploads,
                                              maxResults=50, pageToken=token), quota)
        ids += [it["contentDetails"]["videoId"] for it in page.get("items", [])]
        token = page.get("nextPageToken")
        if not token:
            break
    ids = list(dict.fromkeys(ids))
    videos = []
    for i in range(0, len(ids), 50):
        r = _exec(svc.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])), quota)
        videos += r.get("items", [])
    return {"channel": item, "video_ids": ids, "videos": videos,
            "fetched_at": datetime.now(timezone.utc).isoformat()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="re-fetch even if study/raw/<slug>.json exists")
    ap.add_argument("--only", choices=sorted(CHANNELS), action="append")
    args = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    quota, svc = [0], None
    now = datetime.now(timezone.utc)
    rows, samples = [], {}
    for slug in args.only or CHANNELS:
        path = RAW / f"{slug}.json"
        if args.refresh or not path.exists():
            if svc is None:
                from googleapiclient.discovery import build
                from clipvault import publish
                svc = build("youtube", "v3", credentials=publish.load_creds(), cache_discovery=False)
            raw = fetch_channel(svc, CHANNELS[slug], quota)
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(raw))
            tmp.replace(path)
        raw = json.loads(path.read_text())
        now = datetime.fromisoformat(raw["fetched_at"])
        recs = [S.record(v, slug, now) for v in raw["videos"]]
        rows += recs
        st = raw["channel"].get("statistics", {})
        print(f"  {slug:11} uploads={len(raw['video_ids'])} got={len(raw['videos'])} "
              f"(channel says {st.get('videoCount')})")
        try:
            samples[slug] = S.select(recs)
        except ValueError as e:
            samples[slug] = {"error": str(e)}
            print(f"    sample failed: {e}")
            continue
        s = samples[slug]
        print(f"    counts {s['counts']}  span {s['span'][0]}..{s['span'][1]}")
        for b in ("winners", "median", "holdout_winners", "holdout_median"):
            x = s["summary"][b]
            print(f"    {b:16} n={x['n']} views_med={x['views_median']:>12,.0f} vpd_med={x['vpd_median']:>10,.0f} "
                  f"pub {x['published_min']}..{x['published_max']} (med {x['published_median']}) dur_med={x['duration_median']}s")
    with open(HERE / "videos.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    (HERE / "sample.json").write_text(json.dumps({"generated_at": now.isoformat(), "channels": samples}, indent=1))
    print(f"  wrote {len(rows)} rows to study/videos.jsonl and study/sample.json; quota spent this run: {quota[0]} units")
    return 0 if all("error" not in s for s in samples.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
