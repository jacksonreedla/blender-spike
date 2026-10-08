# Blender spike — findings

*2026-09-10, apollo-server (Ryzen 5 3400G, Vega 11, ~3.7 GB free RAM).
Revised the same evening after an independent audit and a 3-lens judge panel
overturned two of my own conclusions. The corrections are marked.*

**Verdict: rendering is solved; composition is not — yet. Objects were never the
real problem. Environments and atmosphere are, and those are the iterable kind.**

---

## Gate 1 — headless EEVEE on the iGPU: PASS

Needed `libegl1` / `libegl-mesa0` (absent on this minimal Ubuntu Server image).
EGL came up on GBM with **OpenGL 4.6 core** (Mesa 26.0.8, radeonsi/raven),
above EEVEE Next's 4.3 floor. Blender **4.5.13 LTS**, portable tarball at
`~/blender-spike/blender`; bundles its own Python, touches no venv.

## Gate 2 — fast enough: PASS

All rows below were measured on the **lit** representative scene (volumetric
fog, spot key with cast shadow, area fill, figure, moving camera), 1080×1920.
The independent audit reproduced the 32-sample row at 3.81 s/frame.

| samples | s/frame | 30 s Short | 60 s Short |
|---|---|---|---|
| 8 | 1.31 | 20 min | 39 min |
| 16 | 2.14 | 32 min | 64 min |
| 32 | 3.75 | 56 min | **113 min** |
| 64 | 7.04 | 106 min | 211 min |

Bar was ≤4 s/frame; 32 samples clears it. Peak RSS 2.1 GB.

*Correction:* the first version of this table's 64-sample row, and the entire
"what is not the cost" ablation set (volumetrics, PNG vs JPEG, no file write,
view transform, compositor), were measured on an accidentally **black** scene,
which renders ~17% cheaper. The 64 row above is re-measured. The ablation
*conclusion* — cost is pixel- and sample-bound GPU work, not encoding or colour
management — still holds directionally, but those specific numbers are not
re-measured and should not be quoted.

## Gate 3 — licence-clean assets: PASS

Poly Haven (CC0) HDRI and five models download and render. Record in
`assets/LICENCES.md`.

## Gate 4 — can the LLM write a usable shot

Scored by an independent panel: three lenses per shot (fidelity to prompt,
technical defects, "would an editor ship it"), usable = 2 of 3 say yes.

| condition | shots | usable | mean score /5 |
|---|---|---|---|
| free-form (model builds everything) | 5 | 1 | 1.87 |
| asset-composed (model places library models, builds only environment) | 7 | 1 | 1.90 |

Numerically a wash. **The failure class is not.**

### Free-form: one systematic unit error, not a reasoning failure — CORRECTION

I originally wrote that "a chair is five shapes in a relationship and the model
does not hold that relationship." **That was wrong.** The audit read the
generated scripts: the disassembled chair and the floating monolith come from
the model calling `primitive_cube_add(size=1)` while positioning every part as
if the cube were Blender's default 2 units. Halve every extent and the parts
stop touching. Re-rendering the *same script* with `size=2` produces a
structurally correct ladder-back chair (`out/shots/shot_02_size2.png`).

So free-form modelling of simple objects fails on an API-semantics gap, exactly
like the earlier legacy-EEVEE gap, and is fixable the same way (state it in the
contract, or route geometry through a helper whose units are explicit).

### Asset-composed: objects solved, environments exposed

The judges' notes on all seven asset shots say the same thing: the *object* is
fine — "properly grounded", "decent scanned asset", "single continuous bust, no
floating, no clipping" — and the *environment* is missing: a grey lightbox
instead of a cave, an untextured plane instead of cracked desert, no fog, no
moonlight, "a product shot in a studio cyc". One shot (the bust, 3.33) cleared
the bar. Two had hard defects: a wall the model built between camera and
subject blacked out half a frame, and a fog density of 0.055 over a 9 m
sightline turned the corridor near-black.

Part of that is my experimental design: I gave the model five *props* and asked
for caves, deserts and cobbled streets. There were no environment assets, and
the "lantern" was a 0.38 m brass diya that reads as a shell casing. The library
was the wrong shape for the prompts.

What the helper layer did achieve, measurably: **zero API errors** in seven
scripts (the model never touches `bpy`), and **zero floating objects** — the
`place()` helper subtracts the measured base offset, so grounding is a property
of the code, not the model.

## What I got wrong

1. Benchmarked a black frame for several runs (a guessed spot-light euler aimed
   into the void). Fixed with `TRACK_TO`.
2. First quality gate was "file exists and >20 KB"; a black gradient passed it.
3. Diagnosed the chair as a spatial-reasoning limit. It was `size=1` vs `size=2`.
4. Eyeballed the asset run as "roughly 4 of 7 usable". The panel said 1 of 7.
   Same error, third time: I was judging *is the object right* and the panel was
   judging *would this ship*. The panel is the standard.

## Recommendation

The pipeline works end-to-end and renders fast enough for a video a day. The
open problem is **staging**, and it splits cleanly:

- **Objects** — solved by a library. `place()` grounds them by construction.
  Add environment-scale assets (rock, terrain, architecture, ground textures)
  to the library; the current five props cannot make a cave.
- **Free-form geometry** — closer than reported. Fix the unit contract
  (`box()` already takes explicit metres) and re-measure before writing it off.
- **Atmosphere and framing** — the model does not reliably produce fog,
  directional light, or a clear sightline unless told exactly how. Every judged
  failure here is *visible in the frame*, which makes it the right target for a
  render → vision-judge → retry loop. The judge panel built today is that judge.

Next spike, if wanted: environment assets in the library, fog/exposure ranges
and a "nothing between camera and subject" rule in the contract, `size` units
stated, and the 3-lens panel as an automatic retry gate. Measure against the
same 2-of-3 bar. Gate 5 (a narrated 30 s video through ClipVault's TTS and mix)
still has not been run and still should not be until a shot clears the bar
without hand-fixing.
