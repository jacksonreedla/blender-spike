# v2: PS1 explainer pipeline (2026-09-16)

Operator feedback on v1: models good, too slow, wants a body model, voice too slow, go PS1. v2 delivers
`final/graves-that-wore-iron.mp4` (24.4 s, 586 frames, 12 shots, 73 words at 1.3x ~185 wpm incl. gaps).

- `ps1.py` pass (env MVP_PS1=1 in `mvp/runner.py`): 320x569, 6 samples, filter_size 0, Standard view, every mesh
  decimated to ~900 tris, flat shaded, textures 64 px Closest. Post: `scale=1080:1920:flags=neighbor` + 15-bit lutrgb.
  Frames cost 0.5-1.2 s -> a 24 s piece renders in ~7 min (`mvp2-render` unit, `render_all.sh`).
- `sets.py` (MVP_SETS=1): gate_set, churchyard, open_grave, fresh_grave, mortsafe, night/key_cold/fill_cold, and
  `character(clip, at, facing_deg, travel, phase)` on the CC0 Quaternius Universal Animation Library (43 clips,
  one rig, `assets/characters/`). Locomotion clips move the root across the shot; `phase` starts a clip mid-action.
  Feet are grounded at z=0 (no terrain following); Death01 has a flat window only at frames 37-57.
- `assemble.py`: Kokoro per sentence at SPEED (1.3) -> lo-fi chain (11 kHz, 8-bit crush, compressor) -> gaps
  0.18/0.32/0.55 s -> shots cut on `cut_on` words via moviecaptions.word_cues -> render_plan -> post.
- Stills render at frame 24 (`MVP_STILL_FRAME`) so actions read. `AUTHOR_CONTRACT.md` is the v2 author brief.
- Build: Opus author agents wrote shots 02-11 (the session cap killed the judges; unjudged), 01 and 12 by hand.
  Fix list still open: corpse re-fall on long shots, foggy cage shots (08, 10), room set is tiled cobble on all walls.

## v3 (2026-09-16): motion fixes after the operator watched v2
- **Walking backwards:** the Quaternius rig rests facing -Y (measured: Walk_Loop root motion = (0, -1.3, 0) per cycle);
  `character()` now pre-rotates the rig 180 deg so local +Y is forward, and travel follows it. Every authored facing
  was 180 deg off before this.
- **Walking through boxes:** `_path_check()` raycasts the torso at the standing spot and the travel path at knee and
  chest height and raises PATH BLOCKED (like the sightline guard). Caught 4 real collisions. The runner passes the real
  shot length (`SHOT_FRAMES`), so a still checks 48 frames and an anim the true count.
- **Movements not making sense:** PickUp/Interact/Push swapped for Fixing_Kneeling / Idle_Talking; corpses use
  `freeze_at=50` (one held pose, keys outside it removed, constant extrapolation); the steel drum dropped.

## v4 (2026-09-16): the words get their scenes; the men get colour
- `hold(root, obj, bone, offset, rot_deg)` bone-parents any mesh to a hand (origin = bone tail, +Y = fingers);
  `prop_purse()`, `prop_shovel()` (rot_deg=(90,0,0) at offset (0,0.12,0) reads), `prop_lantern(root)` (brass diya + a
  POINT light riding in the hand), `coins(at, z)`, `gallows(at, rot_deg)` -> rope end, `hanged(at3)`.
- `character(cloth=..., skin=...)`: coat colour on the body, skin on Head/neck/hands/fingers via the rig's vertex
  groups (default coat brown, skin (0.62,0.42,0.30)). Palette used: resurrection men brown, watchmen blue-grey,
  anatomist black, corpses pale (0.55,0.52,0.45).
- shot_05 = purse and coins over the slab; shot_06 = gallows + hanged man + an official; shovels in 02/07; lanterns in
  08/09/10. The lantern lookup must match "_root" in the name (a second placed lantern gets ".001").

## v5 (2026-09-17): a textured, reusable cast
- `assets/characters/quaternius-universal-base-characters/` (CC0, Standard tier): textured male/female bodies with
  faces, eyes, hair styles, beard, eyebrows, on the SAME 65-bone rig as the animation library, so all 43 clips apply.
- `mvp2/cast.py`: `person(look, clip, at, facing_deg, travel, phase, freeze_at, sex)` = same contract as `character()`.
  Dressing is by vertex group (argmax of skin / coat / trousers / boots over prefix-matched bone groups, twist bones
  included): the pack's skin texture stays on head and hands, procedural weave cloth elsewhere, plain-colour hair.
  `LOOKS` = robber, robber2, watchman, anatomist, official, corpse (pale). Add a look = add a dict entry.
- PS1 pass keeps `T_*` (pack) textures at 128 px so faces survive; the set stays at 64 px.
- Traps: the pack references `*_Normal_png.png` files that do not exist (harmless "Missing image" noise; hair got a
  plain material for that reason); a warm brown coat under a warm lamp reads as bare skin - keep coats dark or cool.
