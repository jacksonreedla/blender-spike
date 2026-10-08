# PS1 factory spec: assessment (2026-09-15)

Input: `ps1-factory-spec.md` (ChatGPT, given by the operator 2026-09-15). The operator
asked for a judgement and delegated the call ("do what you think"). **Decision: the spec is
the design for the staging-templates step (status board item 9). It is not the next task.
The reference-channel study stays first.**

## Adopted (matches what we measured)
- The planner emits validated data and tested Blender code builds the scene. That is the
  three-round finding (LLM staging 1/7 usable) turned into an architecture: the LLM picks
  `(template, params)` and never stages.
- Semantic environment anchors and camera/lighting presets aim straight at the judges'
  failure mode: right object, missing or wrong environment.
- Render at 360x640 and nearest-neighbour upscale. That is 9x fewer pixels than today's
  1080x1920 (3.75 s/frame). **Unmeasured**: EEVEE time is not linear in pixels, so benchmark
  before promising a number.
- One `.blend` per shot, idempotent builds, a manifest that can rebuild the video, and a
  licence gate (unknown licence = no final render).
- A golden offline fixture (`wooden_crate_demo`) as the acceptance test.

## Rejected or deferred, with reasons
1. **Building before the study.** It commits to a PS1 low-poly look the reference channels
   do not use. Whether that look earns views is the study's question.
2. **Phases 3-4 models** (MDM/DiP, GVHMR, TRELLIS, TripoSR, InstantMesh, UniMate) expect a
   CUDA GPU. The HP has a Vega 11 iGPU and ~5 GB usable RAM. Not runnable here; they need
   rented GPU time, which is a separate decision.
3. **Blender MCP as a pipeline dependency.** The addon talks to a live Blender instance and
   this box is headless. Headless `blender -b -P` scripts already work. MCP stays an
   optional interactive layer, as the spec itself says.
4. **A new repo that re-implements audio/captions.** ClipVault already has Kokoro TTS
   (`tts.py`, `narrate.py`), caption timing and a ducked, loudness-mastered mix
   (`longrender.py`). Import them, as `PROJECT-3D.md` "Gate 5" already plans.
5. **Checklist-only visual QC.** Round 3: every frame passed the numeric gate and 6/7 failed
   the judge panel. The 3-lens panel is the visual QC gate, not a list of rules.

## Underestimated by the spec
- **Characters.** The library has zero rigged humans. A canonical skeleton plus 50 cleaned
  clips is weeks of asset work with licence questions (Mixamo caveat in `assets/LICENCES.md`),
  and the reference channels' look is character-driven. Price this before committing.

## If templates are greenlit after the study
Start from a trimmed Phase 1: the two-shot `wooden_crate_demo` with props and cameras only
(no humanoid), 360x640, `preamble.py` helpers promoted to templates, ClipVault audio chain,
judge panel as QC. Add `PS1_HUMANOID_V1` only once one character shot is proven to matter.
