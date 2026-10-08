import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sample as S  # noqa: E402

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)


def test_iso_seconds():
    assert S.iso_seconds("PT59S") == 59
    assert S.iso_seconds("PT1M2S") == 62
    assert S.iso_seconds("PT1H") == 3600
    assert S.iso_seconds("P0D") is None or S.iso_seconds("P0D") == 0
    assert S.iso_seconds("") is None and S.iso_seconds(None) is None and S.iso_seconds("junk") is None


def test_record_flattens_and_computes_views_per_day():
    item = {"id": "v1", "snippet": {"title": "T", "publishedAt": "2026-09-05T00:00:00Z", "tags": ["a"]},
            "statistics": {"viewCount": "1000", "likeCount": "10"}, "contentDetails": {"duration": "PT45S"}}
    r = S.record(item, "zack", NOW)
    assert r["duration_s"] == 45 and r["views"] == 1000 and r["likes"] == 10 and r["comments"] is None
    assert r["views_per_day"] == 100.0 and r["channel"] == "zack"


def test_record_survives_hidden_counts():
    r = S.record({"id": "v2", "snippet": {"publishedAt": "2026-01-01T00:00:00Z"}, "statistics": {},
                  "contentDetails": {"duration": "PT30S"}}, "c", NOW)
    assert r["views"] is None and r["views_per_day"] is None


def _rows(k, n_old=0):
    rows = []
    for i in range(k):                                  # views fall with i; published dates spread over 2025
        rows.append({"id": f"v{i:04d}", "views": 10_000_000 - i * 1000, "duration_s": 40,
                     "published": f"2025-{(i % 12) + 1:02d}-15T00:00:00Z", "views_per_day": 1.0, "live": "none"})
    for j in range(n_old):                              # very old, mid views: outside the winners' span
        rows.append({"id": f"old{j}", "views": 5_000_000, "duration_s": 40,
                     "published": "2019-01-01T00:00:00Z", "views_per_day": 1.0, "live": "none"})
    return rows


def test_select_buckets_are_disjoint_and_sized():
    out = S.select(_rows(600), n=50)
    sets = [set(out[k]) for k in ("winners", "median", "holdout_winners", "holdout_median")]
    assert [len(s) for s in sets] == [50, 50, 50, 50]
    assert sum(len(s) for s in sets) == len(set().union(*sets))
    assert out["winners"][0] == "v0000" and out["holdout_winners"][0] == "v0050"


def test_select_median_bucket_stays_inside_winners_date_span():
    out = S.select(_rows(600, n_old=300), n=50)
    assert not any(i.startswith("old") for i in out["median"] + out["holdout_median"])
    assert out["span"][0] >= "2025-01-15"


def test_select_excludes_long_and_live_and_reports_them():
    rows = _rows(600)
    rows[0]["duration_s"] = 200                         # would have been the top winner; over the Shorts cap
    rows[1]["live"] = "upcoming"
    rows.append({"id": "long", "views": 1, "duration_s": 900, "published": "2025-05-01T00:00:00Z",
                 "views_per_day": 0, "live": "none"})
    out = S.select(rows, n=50)
    assert "v0000" not in out["winners"] and "v0001" not in out["winners"]
    assert out["counts"]["excluded_longer"] == 2
    assert S.SHORT_MAX_S == 180                         # His/Her Story Shorts are 61-180 s


def test_select_refuses_a_thin_channel():
    with pytest.raises(ValueError):
        S.select(_rows(120), n=50)
