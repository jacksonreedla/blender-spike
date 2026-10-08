"""Fetch CC0 models from Poly Haven into assets/models/<id>/, glTF + its includes.

Poly Haven's glTF is multi-file: the .gltf references a .bin and a textures/
folder by RELATIVE path, so the include layout has to be preserved exactly or
Blender imports untextured geometry (or nothing).

    .venv/bin/python fetch_models.py dining_chair_02 barrel_03 ...
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEST = HERE / "assets" / "models"
API = "https://api.polyhaven.com/files/{}"


# Poly Haven 403s the default urllib User-Agent; curl's is fine.
UA = {"User-Agent": "curl/8.5 (omnichrome blender-spike)"}


def _open(url: str, timeout: int):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)


def fetch(url: str, to: Path) -> int:
    to.parent.mkdir(parents=True, exist_ok=True)
    with _open(url, 120) as r, open(to, "wb") as f:
        n = f.write(r.read())
    return n


def get_model(asset: str, res: str = "1k") -> Path:
    with _open(API.format(asset), 60) as r:
        files = json.load(r)
    entry = files["gltf"][res]["gltf"]
    root = DEST / asset
    main = root / Path(entry["url"]).name
    total = fetch(entry["url"], main)
    for rel, inc in (entry.get("include") or {}).items():
        total += fetch(inc["url"], root / rel)
    print(f"  {asset}: {main.name} + {len(entry.get('include') or {})} files, "
          f"{total / 1e6:.1f} MB")
    return main


if __name__ == "__main__":
    for a in sys.argv[1:]:
        get_model(a)
