# MVP explainer pipeline (2026-09-15)

One narrated 9:16 3D explainer, built end to end on the HP. First title:
**"The Graves That Wore Iron"** (grave robbing in Georgian England, mortsafes, the
Anatomy Act 1832), 5 shots, 68 words, ~28 s.

```
script.json          the plan (beats, sentences, shot specs)      <- design judge panel
assemble.py narrate  Kokoro 1.1x per sentence -> audio/, script.timed.json, render_plan.json (frames per shot)
shots/shot_NN.py     one scene per beat: preamble helpers + helpers.py, camera as CAM_START/CAM_END/CAM_AT/LENS
runner.py            still <png> (midpoint of the move, judged) | anim <dir> <frames> [samples w h]
render_all.sh        all shots, flock-serialised, under systemd-run --user (mvp-render.service), logs/render.log
assemble.py post     PNG seqs -> bed.mp4 (-bf 0, explicit durations) + brown-noise wind bed
                     -> moviecaptions "pop" .ass -> longrender mix graph (-16 VO, duck, -14 master) -> final/<slug>.mp4 -> QC
```
Run everything with `/home/apollo/clipvault/.venv/bin/python` from `~/blender-spike`.

- Stills are judged at 1080x1920 / 32 samples; the animation renders at 16 samples (~2 s/frame -> ~25 min for 676 frames).
- `helpers.py`: `tbox()` textured boxes with BOX projection (a cube's UVs stretch each face), `headstone()`,
  `mound()` (half-buried ellipsoid of earth = a fresh grave), `ibar()` iron bars, `shade()` (brown_mud_dry is a bright tan).
- What the judge panel rejected in round 1 (all five shots, means 1.0-2.0): flat-colour boxes read as
  "lightbox" cards/crates; no churchyard; the narrative object missing; warm where cold was asked; top of frame void.
  Fixes that worked: rock textures on every cut stone, rock_face_* masses in fog instead of walls, world strength
  ~0.25 + fog 0.011-0.018 with anisotropy 0.55-0.75 (isotropic fog under a strong bulb = milky wall), one cold key.
- AUTHOR_CONTRACT.md is what the author agents get; `stills/` keeps every attempt (`_aN` authors, `_bN` hand fixes).

## Judge panel on the delivered stills (2026-09-15, Opus judges, `logs/panel_round2.json`)

| shot | fidelity | technical | editorial | mean | verdict |
|---|---|---|---|---|---|
| shot_01 | 3 | 2 | 2 | 2.33 | rejected |
| shot_02 | 2 | 2 | 2 | 2.00 | rejected |
| shot_03 | 2 | 1 | 2 | 1.67 | rejected |
| shot_04 | 1 | 2 | 2 | 1.67 | rejected |
| shot_05 | 3 | 2 | 3 | 2.67 | usable |

v2 fix list (the notes every lens repeated): contact shadows / AO under every object; the gate's pickets end above the
ground (add a bottom rail or sink it); shot_04 needs the key BEHIND the cage so bar shadows rake toward the lens (that is
the shot); shot_03's mound reads as a buried egg (rectangular, ragged, spoil heap, a spade); shot_05 and shot_02 grade warm
where the brief is cold; put something in the top quarter of every frame (roofline, branches); vignette the lower third
for the caption. Full notes per lens in the JSON.
