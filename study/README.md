# Reference-channel study

Plan: `../PROJECT-3D.md` ("NEXT: the reference-channel study"). Import from ClipVault; change nothing there.
Run everything with `/home/apollo/clipvault/.venv/bin/python`.

| phase | file | state |
|---|---|---|
| A harvest + sample | `harvest.py`, `sample.py`, `tests/test_sample.py` | done 2026-09-15 |
| B captions + frames | - | next |
| C-E | - | todo |

- `raw/<slug>.json`: raw Data API items (cache; delete or `--refresh` to re-spend ~270 units).
- `videos.jsonl`: one flat row per upload (id, channel, title, published, duration_s, views, likes, comments, views_per_day, tags).
- `sample.json`: per channel, `winners` / `median` / `holdout_winners` / `holdout_median` id lists + summaries.
- Tests: `/home/apollo/clipvault/.venv/bin/python -m pytest -q study/tests/`
