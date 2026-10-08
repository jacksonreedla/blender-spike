# Asset licences — check before anything is published

Monetised video is commercial use. Every asset below is recorded with what it
actually permits, because a licence mistake surfaces after the money, not before.

## In use

| Asset | Source | Licence | Commercial | Attribution |
|---|---|---|---|---|
| `studio.hdr` (moonless_golf 1k) | Poly Haven | **CC0** | Yes | Not required |

Poly Haven publishes everything as CC0 (public domain dedication) — HDRIs,
textures and models. No attribution, no share-alike, monetised video is fine.
It is the safest default source and should be the first place we look.

## Evaluated, not yet used

- **Mixamo** (Adobe) — free rigged characters and motion-capture animations.
  Requires an Adobe account. The licence permits use in commercial projects
  including video; it does **not** permit redistributing the characters or
  animations as assets themselves. Fine for rendering into a video, not fine
  for shipping a pack. Needs a browser login to download, so it cannot be
  automated headlessly — characters get fetched by hand and cached locally.
- **BlenderKit** — mixed licensing. The free tier contains both CC0 and
  royalty-free-with-conditions assets, so each asset's licence must be checked
  individually. Do not treat "free tier" as "CC0".
- **Blender's own bundled assets** — the default asset bundles ship CC0.

## Rules for this project

1. **CC0 first.** Poly Haven for HDRIs and textures; procedural geometry for
   everything a script can build. Procedural has no licence question at all,
   which is one more reason the LLM-writes-the-scene approach is attractive.
2. Anything not CC0 gets a row in the table above, with the licence text
   archived next to it, before it is used in a render.
3. No scraped or "found" models. A model of unknown provenance in a monetised
   video is the same exposure as unlicensed music, and Content ID is not the
   only enforcement route — a DMCA takedown against the channel is worse.
4. **Fonts count.** Anything on screen needs a licence that covers embedding in
   video; the repo already bundles Bangers for the Shorts, which is OFL.

## Characters (`assets/characters/`)

| Asset | Source | Licence | Commercial | Attribution |
|---|---|---|---|---|
| `quaternius-universal-animation-library/` — "Mannequin" rigged humanoid (65-bone universal rig, 43 animation clips, 13,743 tris, 1.80 m) | Quaternius, [Universal Animation Library](https://quaternius.itch.io/universal-animation-library) (Standard/free zip, fetched 2026-09-15) | **CC0 1.0** | Yes | Not required |

Verified from the pack's own `License.txt` (CC0 1.0 + the creativecommons.org
deed URL), the itch.io "Asset license" field, and the quaternius.com pack page —
licence text archived at
`assets/characters/quaternius-universal-animation-library/LICENCE.txt`.
The GLB carries mesh + rig + all 43 clips in one file, so every clip shares one
armature and no retargeting step exists. Two variants ship: `UAL1_Standard.glb`
(in-place, root travel 0.0000 m over Walk_Loop — use with a fixed camera) and
`UAL1_Standard_RM.glb` (root motion baked, 1.2594 m per walk cycle).
Import recipe next to the asset: `import_recipe.py`.
