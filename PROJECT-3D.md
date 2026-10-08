# Project 3D — handoff for the next session

*Written 2026-09-11 on apollo-server. Self-contained: a fresh session should be
able to pick this up without the conversation that produced it. Companion
docs: `~/OMNICHROME.md` (section "Blender / 3D explainer spike"), memory
`blender-3d-spike.md`, and `findings.md` beside this file.*

## What this is, in one paragraph

The operator asked whether ZachDFilms / His Story / Her Story-style 3D
explainer shorts can be made now that AI can drive Blender. Over 2026-09-10 the
answer was measured: **rendering is solved, the asset library and helper
toolkit are built and proven, and an LLM cannot stage a shot** — three rounds
of LLM-authored scenes each scored 1 usable in 7 by an independent judge panel.
Operator decision 2026-09-11: **stop that line.** Two things follow it, in
order: (1) a **study of the reference channels** (what earns their views —
sample, method and outputs all decided, plan below, not yet started), and (2)
only if warranted, **hand-built shot templates** where the LLM merely picks
`(template, params)`. No destination for the content (channel / long-form /
client work) has been chosen — deliberately.

**Update 2026-09-15:** the operator supplied a ChatGPT spec for a "PS1 short-form 3D video factory" (`docs/ps1-factory-spec.md`, verbatim). It is the design for the templates step, not the next task. Assessment, with what was adopted and rejected: `docs/ps1-factory-assessment.md`. Status is also on the ops page https://ops.omnichrome.net/p/3d, which renders `project.json`.

## Status board

| item | state |
|---|---|
| Blender 4.5.13 LTS headless on the Vega 11 iGPU | **works** — `~/blender-spike/blender/blender` |
| Render speed, lit volumetric 1080×1920 | 3.75 s/frame @32 samples → 60 s Short ≈ 113 min |
| CC0 library | 14 models (51 MB) + 6 ground textures, `assets/`, licences in `assets/LICENCES.md` |
| Helper toolkit `scenes/preamble.py` | proven: a hand-built scene is in the target style (`out/smoke_env2.png`) |
| LLM authors the scene | **1/7 usable, three rounds — parked** |
| Render→judge→retry loop | built, **unmeasured** (session limit killed 6 of 9 retries) |
| Judge panel (3 lenses, workflow) | reusable: `~/.claude/projects/-home-apollo-omniclipper-server/*/workflows/scripts/shot-judge-panel-*.js` |
| Reference-channel study | **planned, not started** — see below |
| Templates | not started; resume path only |
| Destination | undecided |

Nothing from this project runs unattended: no timers, crons, or services.

## Where everything is

```
~/blender-spike/
  PROJECT-3D.md          this file
  findings.md            measured results, corrections, recommendation (round 1-2 state; round 3 below)
  blender/               Blender 4.5.13 portable (bundles its own Python; touches no venv)
  scenes/
    preamble.py          the helper toolkit prepended to every generated script (see "Toolkit")
    representative.py    the benchmark scene (lit; the first version was black - see traps)
    trivial.py           gate-1 smoke scene
    measure.py           blender -b -P: measures every model's bbox/base -> assets/models/manifest.json
    generated/           free-form LLM scripts (round 1)
    generated_assets_v1/ asset-mode scripts, round 2
    generated_assets/    asset-mode scripts, round 3 (+ _a2/_a3 retries)
  shotgen.py             prompt -> DeepSeek -> bpy script -> render -> numeric gate. --assets, --attempt N, --feedback-file
  fetch_models.py        Poly Haven glTF fetcher (needs a curl-like User-Agent; urllib's default 403s)
  assets/
    models/<id>/          glTF + textures; manifest.json = measured size_m, base_z, centre_xy per model
    textures/<id>/        PBR jpg sets; manifest.json = diff/rough/nor/arm paths + description
    studio.hdr            Poly Haven HDRI (CC0)
    LICENCES.md           what each source permits (Poly Haven CC0; Mixamo/BlenderKit caveats)
  out/
    shots/                round 1 renders; shot_02_size2.png = the corrected chair
    shots_assets_v1/      round 2
    shots_assets/         round 3 (+ _a2/_a3)
    shotgen*.json         per-run stats (mean luma, sd, dark/blown share)
    smoke_env2.png        the hand-built style sample
    .render.lock          flock: one Blender at a time (a render peaks ~2 GB; box has ~3.7 GB free)
```

Run anything with ClipVault's venv: `/home/apollo/clipvault/.venv/bin/python`.
DeepSeek and Groq keys are in `~/clipvault/.env` (names only here). There is a
Claude author backend in `~/omniclipper-server/clip_vod.py::_make_ask(backend="claude")`
but **no `ANTHROPIC_API_KEY` on the box**.

## Toolkit (`scenes/preamble.py`) — what each helper prevents

Every helper exists because the model got that exact thing wrong, measured:

- `reset()` — EEVEE Next, 1080×1920, 32 samples. The model writes Blender ≤4.1
  code (`use_volumetric_lights`, `use_gtao`… all removed in 4.2) unless told.
- `place(name, at, rot_deg, scale)` — imports a library model with its **base on
  the ground** using the manifest's measured `base_z`. Floating objects became
  impossible. **Gap: no `z=` — the model tried `place(..., z=1.2)` to put a
  bust on a plinth and crashed. Add elevation if resumed.**
- `box(size, at, ...)` — environment geometry only, explicit metres. The
  model's free-form `primitive_cube_add(size=1)` while positioning for the
  default 2-unit cube is what produced the "exploded chair".
- `light(kind, location, at, energy, ...)` / `camera(location, at, lens)` —
  aimed by `TRACK_TO`; guessed eulers aimed a spot into the void and produced a
  black frame that still cost full render time.
- `lamp(at, toward, energy)` — a street lamp **with its bulb offset out of the
  lamp mesh**; a point light at the lamp head is shadowed by its own housing
  (luma 0.6 → 104 by moving it 0.5 m).
- `ground(texture=..., scale, wet)` / `pbr_material` — textured floors; `wet`
  lowers roughness for the wet-street reflection.
- `world(color, strength, hdri, fog, anisotropy)` — fog **clamped at 0.03**;
  0.055 over a 9 m sightline rendered near-black.
- `render(path)` → `check_sightline()` first: raycasts camera→subject and
  **raises** if something sits in between (the model walled off half a frame).

`shotgen.py`'s numeric gate (mean luma, contrast, crushed-black and blown-out
share) rejects black/flat frames, but **passing it is not "usable"** — every
round-3 frame passed the gate and only 1 of 7 passed the judges.

## Results, three rounds (all judged by the 3-lens panel, usable = 2 of 3)

| round | change | usable | notes |
|---|---|---|---|
| 1 free-form | API contract only | 1/5 | chair exploded, monolith floated, "cave" absent |
| 2 assets | 5 props + helpers | 1/7 | every object fine, every environment missing |
| 3 assets+env | +9 env models, 6 textures, sightline guard, fog clamp, lamp() | 1/7 | same; retries unmeasured |

**Diagnosis:** the toolkit is sufficient (hand-built scene passes); the
*author* is the bottleneck, specifically at **staging**. The cave shot is the
exhibit: three judges wrote the identical fix — "camera inside the cave looking
out at a bright opening, figure silhouetted" — twice, and DeepSeek twice
produced a front-lit statue in front of a rock wall (`out/shots_assets/shot_01_a3.png`).
Every mechanical gap found was fixed and the number never moved.

**Corrections made along the way, so nobody re-learns them:**
1. Blender's `Time:` counter under-reports (0.24 s shown, 3.2 s real).
2. "File exists and >20 KB" passed a black gradient. Then the numeric gate
   passed frames the judges failed. **The panel is the standard, not any eye —
   mine scored 4/7 where the panel scored 1/7.**
3. "The model can't hold spatial relationships" was wrong — it was `size=1` vs
   `size=2`. Re-render of the same script: a correct chair.
4. A workflow's *failed* agents must be treated as missing, not scored 0: the
   aggregate code once produced a false "assets 0/7" that way. Read
   `journal.jsonl` before trusting a summary number.
5. Session limits cut two workflows mid-run; both were resumable with
   `resumeFromRunId` (cached agents replay free).
6. `pgrep -f "<pattern>"` inside a waiter loop matches its own command line
   and never exits — two zombie loops from that.

## NEXT: the reference-channel study (decided 2026-09-11, not started)

**Question:** what makes Zack D. Films / His Story / Her Story shorts get
views. **Method:** reuse ClipVault's `scriptstudy.py` (`metrics` → `beat_map`
→ `aggregate` → `render_report`; it never copies source phrasing and has a
tripwire test) and add a within-channel comparison plus a visual dimension.

Channels (resolved, unambiguous):

| channel | id | subs | videos | views |
|---|---|---|---|---|
| Zack D. Films | `UCvz84_Q0BbvZThy75mbd-Dg` | 28.4M | 3,910 | 76.3B |
| His Story | `UCrwSMlDM6FGLwHOtZ5JZpVA` | 6.1M | 1,504 | 8.9B |
| Her Story | `UCpHpLD-URpThtttHTxefZ4A` | 2.75M | 1,151 | 3.6B |

Operator decisions: **top 50 vs median 50 per channel** (300 deep, from
full-channel metadata); **captions + frames, downloads throttled** (one at a
time, keep frames, delete the mp4); output **`report.md` + a machine-readable
`contract.json`** in the shape `clipvault/script.py` consumes.

Work in `~/blender-spike/study/` (NOT `~/clipvault/study/`, which is the other
session's Regular Show study inside a production repo). Import from ClipVault,
change nothing there.

Phases:
- **A. harvest + sample** (API only, ~300 quota units): `channels.list` →
  uploads playlist → `playlistItems.list` → `videos.list` (50/batch) → keep
  duration ≤ 60 s → `videos.jsonl`. Winners = top 50 by views; median = the 50
  straddling the median **from the same publish-date span** (age is the
  confound; also record views/day). Use ClipVault's token **in memory only** —
  never rewrite `~/clipvault/secrets/rs_token.json`; never the campaign client.
- **B. fetch** (background, 2–3 h): auto-captions via the `yt_dlp` module
  (2026.08.19, in the venv) → transcripts in the shape `scriptstudy.metrics()`
  reads (check its loader, don't invent a second shape); then one download at
  a time, 20–40 s jitter, keyframes at 0/1/3/8/mid/end−2 + scene-change count,
  **delete the mp4**. `--limit 5` dry pass first. **Home IP: stop on the first
  403/429, never cycle egress, never parallelise.**
- **C. analyse**: `metrics()` per transcript; title features (number,
  question, "what if", "you", caps, emoji); duration, cuts/s, hashtags,
  publish time. `beat_map()` = 300 DeepSeek calls. First-seconds visuals = a
  **resumable Workflow**, one agent per video reading the 0/1/3 s frames →
  structured labels; failed agents = missing.
- **D. aggregate**: winners vs median per channel and pooled; title clusters
  via `clipvault.embed.embed_documents` (local, free); `render_report()` →
  numbers only; `contract.json` = winner-bucket targets (hook window, WPM,
  duration band, cut rate, title shapes, first-3-s visual profile, beat order).
- **E. validate**: score held-out ranks 51–100 vs the median neighbours with
  the contract; report whether it discriminates, either way.

Verification targets: ~6,500 harvested; 300 sampled with overlapping date
spans; ≥90 % captions and frames; zero mp4s left; report has the delta and
cluster tables; `contract.json` parses with numeric targets; a 12-word span
from any transcript does not appear in the report.

### Phase A result (DONE 2026-09-15)
`study/harvest.py` (retries YouTube 5xx; raw cache `study/raw/<slug>.json`, so re-sampling costs 0 units) +
`study/sample.py` (pure, 7 tests in `study/tests/`). 269 quota units, token never rewritten.
**Deviation from the plan: the Shorts cap is 180 s, not 60 s.** His Story and Her Story started 2026-02 and
their Shorts run 61-180 s (only 45 and 50 videos are 60 s or less); on both, the median view count RISES with length
(His: 3.2M at 60 s or less -> 5.3M at 121-180 s). Zack is 99% 60 s or less, so its sample barely moved.

| channel | winners views med | median views med | winners views/day | median views/day | dur med (W / M) |
|---|---|---|---|---|---|
| Zack D. Films | 97.9M | 16.5M | 133k | 25k | 30 / 31 s |
| His Story | 24.8M | 4.2M | 194k | 58k | 121.5 / 107.5 s |
| Her Story | 12.4M | 2.2M | 124k | 24k | 98 / 98.5 s |

Confound to carry into C-D: His Story's median bucket is ~2 months younger than its winners, so compare views/day
as well as views. Holdouts (ranks 51-100 and the median's neighbours) are in `sample.json` for phase E.
**Next = phase B** (captions + frames on the home IP, throttled, `--limit 5` dry pass first).

### MVP video pipeline (BUILT 2026-09-15, operator: "go step by step till we have an mvp vid")
`~/blender-spike/mvp/` (README there). Script from a 4-angle judge panel -> "The Graves That Wore Iron"
(Georgian grave robbing, mortsafes, Anatomy Act 1832; 5 beats, 68 words). Kokoro narration per sentence at 1.1x
(27.4 s), one Blender shot per beat with a camera move (`runner.py` still|anim), PNG sequences -> ffmpeg via
ClipVault's longrender mix graph + moviecaptions word-pop captions -> `mvp/final/graves-that-wore-iron.mp4`.
- **Author agents (Opus) built the first scenes; the 3-lens panel rejected all five** (means 1.0-2.0): flat-colour
  boxes read as lightbox cards, no churchyard, the narrative object missing. Hand fixes that turned them: rock
  textures with BOX projection on every cut stone, `rock_face_*` masses in fog instead of walls, world strength
  ~0.25 with fog 0.011-0.018 at anisotropy 0.55-0.75, one cold key. One author built a real dug pit
  (displaced grid mesh, shot_02) and another a proper mortsafe from cylinders (shot_04) - both kept.
- Subagent usage limits hit twice mid-build (Fable weekly, then a session cap to 18:30 UTC); the judge/author
  stages were re-run on `model: 'opus'` and the last fix round was done by hand in the main session.
- Render: 1080x1920, 16 samples, 24 fps, 676 frames as `mvp-render.service` (systemd-run --user, flock-serialised).

### v2 (2026-09-16): PS1 aesthetic, body model, fast lo-fi voice
Operator direction after watching v1. `~/blender-spike/mvp2/` (README there): 320x569 PS1 pass, reusable set builders,
CC0 Quaternius rig with 43 clips, narration 1.3x + bitcrush, 12 shots cut on words, ~7 min render. Delivered
`mvp2/final/graves-that-wore-iron.mp4`. Subagent caps hit again mid-build; judges did not run on v2 stills.

## AFTER the study, if warranted: templates (resume path, not started)

Hand-build ~6 staging templates as Python on top of `preamble.py` — the study
should say which six — each with parameters (asset, ground texture, colour
temperature, fog, camera distance/height, key angle), each validated once by
the judge panel. The LLM then only chooses `(template, params)` per narration
beat, a structured choice it is reliable at; this is how ClipVault's Top 5
format already works. Only then run "Gate 5": a narrated 30 s piece through
ClipVault's existing chain — `script.py` → `narrate.py`/`tts.py` (Kokoro,
local) → `longrender.py` (ducked mix). The seam is `timeline.Shot` →
`longrender.cut_shot(shot, src, ...)`: a rendered shot is just a source file
with `src_start=0`. Optional 30-minute side test if a key appears: the same
prompts through the Claude author backend.

## Constraints that do not move

- Never publish, never redistribute downloaded video; frames are analysis
  artefacts. Never copy the channels' phrasing into anything.
- Do not touch `~/clipvault` code or its index; another session works there.
- `~/OMNICHROME.md` is the single source of truth — update it when this changes.
- Two open operator calls elsewhere are NOT this project's: the half-paused
  Whop campaign posts publishing unfiled, and `PRECHECK_FORMATS` for Shorts.

## Close-out still owed for the spike (small)

Rewrite `findings.md` to the round-3 state above (it currently reflects rounds
1–2); add the same to `~/OMNICHROME.md` and memory `blender-3d-spike.md`;
delete the ~32 scratch files under `/tmp` (`fb_*.txt`, `smoke_*.py`, `rep64*`,
`{variant,t,s,f,v}_*.py`, `sweep.py`, `shot_02_size2.py`, `preamble_smoke.py`,
`audit_rep`); keep all renders and assets (1.4 GB; 175 GB free); leave
`libegl1`/`libegl-mesa0` installed.

## How to resume, mechanically

```
cd ~/blender-spike
./blender/blender --version                                   # 4.5.13 LTS
./blender/blender -b -P scenes/trivial.py -- out/check.png    # ~9 s, proves EEVEE on the iGPU
/home/apollo/clipvault/.venv/bin/python shotgen.py --assets "a stone statue in a fog-filled clearing"   # one LLM shot
# study: create study/harvest.py per Phase A above; start with the harvest, it is API-only and safe.
```
