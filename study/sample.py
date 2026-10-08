"""Phase A sampling for the reference-channel study (pure, no network).

record()  - one videos.list item -> the flat row written to study/videos.jsonl
select()  - per channel: top N by views ("winners") vs the N straddling the median
            of the SAME publish-date span, plus held-out ranks N+1..2N and the
            median's neighbours for phase E. Age is the confound: an old video has
            had longer to collect views, so the median bucket is drawn only from
            the window the winners were published in, and views/day is recorded.
"""
from __future__ import annotations

import re
import statistics
from datetime import datetime

SHORT_MAX_S = 180         # YouTube Shorts limit. Was 60 (2026-09-11 plan); the harvest showed His/Her Story
                          # Shorts run 61-180 s (<=60 s: 45 and 50 videos), so 60 made them unsampleable.
N = 50
_ISO = re.compile(r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$")


def iso_seconds(s: str | None) -> int | None:
    m = _ISO.match(s or "")
    if not m or not any(m.groups()):
        return None
    d, h, mi, se = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def record(item: dict, channel: str, now: datetime) -> dict:
    sn, st, cd = item.get("snippet") or {}, item.get("statistics") or {}, item.get("contentDetails") or {}
    pub = sn.get("publishedAt") or ""
    views = _int(st.get("viewCount"))
    try:
        age_d = max((now - datetime.fromisoformat(pub.replace("Z", "+00:00"))).total_seconds() / 86400, 1.0)
    except ValueError:
        age_d = None
    return {"id": item["id"], "channel": channel, "title": sn.get("title", ""), "published": pub,
            "duration_s": iso_seconds(cd.get("duration")), "views": views,
            "likes": _int(st.get("likeCount")), "comments": _int(st.get("commentCount")),
            "views_per_day": round(views / age_d, 1) if views is not None and age_d else None,
            "tags": sn.get("tags") or [], "live": sn.get("liveBroadcastContent")}


def _summary(rows: list[dict]) -> dict:
    if not rows:
        return {"n": 0}
    return {"n": len(rows), "views_median": statistics.median(r["views"] for r in rows),
            "vpd_median": statistics.median(r["views_per_day"] or 0 for r in rows),
            "published_min": min(r["published"] for r in rows)[:10],
            "published_max": max(r["published"] for r in rows)[:10],
            "published_median": sorted(r["published"] for r in rows)[len(rows) // 2][:10],
            "duration_median": statistics.median(r["duration_s"] for r in rows)}


def select(records: list[dict], n: int = N, short_max_s: int = SHORT_MAX_S) -> dict:
    usable = [r for r in records if r.get("views") is not None and r.get("duration_s")]
    pool = [r for r in usable if r["duration_s"] <= short_max_s and r.get("live") in (None, "none")]
    ranked = sorted(pool, key=lambda r: (-r["views"], r["id"]))
    if len(ranked) < 4 * n:
        raise ValueError(f"only {len(ranked)} videos <= {short_max_s}s; need {4 * n}")
    winners, holdout_winners = ranked[:n], ranked[n:2 * n]
    lo, hi = min(r["published"] for r in winners), max(r["published"] for r in winners)
    taken = {r["id"] for r in ranked[:2 * n]}
    span = [r for r in ranked if lo <= r["published"] <= hi and r["id"] not in taken]   # still views-desc
    if len(span) < 2 * n:
        raise ValueError(f"only {len(span)} videos in the winners' date span; need {2 * n}")
    start = len(span) // 2 - n // 2
    median = span[start:start + n]
    holdout_median = span[max(0, start - n // 2):start] + span[start + n:start + n + n // 2]
    return {"n": n, "short_max_s": short_max_s, "span": [lo[:10], hi[:10]],
            "counts": {"all": len(records), "shorts": len(pool), "in_span": len(span),
                       "excluded_longer": sum(1 for r in usable if r["duration_s"] > short_max_s)},
            "winners": [r["id"] for r in winners], "median": [r["id"] for r in median],
            "holdout_winners": [r["id"] for r in holdout_winners],
            "holdout_median": [r["id"] for r in holdout_median],
            "summary": {"winners": _summary(winners), "median": _summary(median),
                        "holdout_winners": _summary(holdout_winners), "holdout_median": _summary(holdout_median)}}
