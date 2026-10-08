<!-- Received 2026-09-15 from the operator ("attached is chat gpts recommendation"), stored verbatim.
     Status: DESIGN INPUT for the staging-templates step, NOT the next task. Assessment: ps1-factory-assessment.md -->

# PS1 Short-Form 3D Video Factory

> Master implementation specification for Claude Code  
> Target: Linux + Blender + Claude connected through Blender MCP  
> Output: original 9:16 low-poly educational and storytelling shorts inspired by the pacing and visual clarity of HisStory and Zack D. Films—without copying their branding, scripts, characters, voices, or proprietary assets.

---

## 0. Instructions to Claude Code

You are the lead engineer for this repository. Treat this document as the product specification and source of truth.

Build a modular, testable production system that turns a topic or approved script into a rendered PS1-style vertical short.

Use Blender as the deterministic 3D engine. Use Claude and Blender MCP as the directing and control layer. Prefer reusable assets, standardized rigs, procedural animation, and explicit shot specifications over end-to-end frame generation.

Do not attempt to install every research model during the first implementation. Complete the deterministic MVP first. Keep every model-dependent component behind an adapter so that it can be added or removed without changing the core pipeline.

Before changing an existing repository:

1. Inspect the repository, operating system, Blender version, Python version, installed MCP server, available GPU, FFmpeg availability, and existing files.
2. Read any existing `README.md`, `CLAUDE.md`, `AGENTS.md`, `pyproject.toml`, requirements files, and Blender scripts.
3. Preserve user code and unrelated changes.
4. Write a short implementation plan based on what is actually present.
5. Implement the smallest end-to-end vertical slice first.
6. Run tests and a smoke render before moving to optional systems.
7. Record exact setup commands and observed versions in `docs/SETUP.md`.
8. Do not claim an integration works until a smoke test proves it.

When this specification conflicts with the actual installed API of a dependency, use the current official API and document the deviation.

---

# 1. Product Vision

Build an AI-directed low-poly 3D content engine capable of receiving a request such as:

> Make a 50-second short explaining what happened inside Pompeii during the eruption.

The finished system should eventually produce:

- A researched, source-backed factual outline
- An original short-form script
- Narration
- A beat sheet and shot list
- Structured shot JSON
- Selected or generated assets
- Automatically assembled Blender scenes
- Character and object animation
- Camera moves, lighting, and effects
- Low-resolution PS1-style renders
- Captions, sound effects, and music
- A final 1080 × 1920 MP4
- A manifest containing sources, licenses, prompts, assets, models, and build logs

The project should eventually become a general AI 3D short-film factory capable of producing:

- Historical stories
- Science explanations
- Anatomy visualizations
- Engineering explainers
- True-crime reconstructions
- Military-history videos
- Educational storytelling
- Short cinematic documentaries

The initial product should be narrower: reliable, original, narrated shorts with simple characters and clear action.

## Core Thesis

Do not ask AI to invent every frame.

Ask AI to direct a standardized, scriptable 3D studio.

The long-term moat is not a single motion model. It is the accumulated library of:

- Characters
- Clothing
- Props
- Historical environments
- Anatomy assets
- Standardized rigs
- Cleaned animations
- Camera moves
- Lighting setups
- Procedural effects
- Proven shot templates
- Quality-control rules
- Metadata and licensing provenance

Every completed production should make the next production faster.

---

# 2. Product Boundaries

## MVP Must Do

- Accept a topic, supplied script, or supplied shot plan.
- Convert an approved script into validated shot JSON.
- Search a local asset catalog.
- Assemble multi-shot Blender scenes automatically.
- Support one canonical low-poly humanoid skeleton.
- Apply reusable animation clips.
- Animate simple props and cameras procedurally.
- Render 360 × 640 frames in Eevee.
- Upscale to 1080 × 1920 using nearest-neighbor scaling.
- Generate or accept narration.
- Generate timed captions.
- Combine shots, narration, captions, music, and sound effects with FFmpeg.
- Output a reproducible build manifest.
- Fail clearly when required assets, programs, or models are missing.

## MVP Must Not Depend On

- UniMate checkpoints
- Local motion-model training
- Photorealistic humans
- Advanced facial acting
- Automatic publishing
- Perfect text-to-3D generation
- Cloud services with unclear commercial terms
- One specific Blender MCP implementation

## Version 1 Non-Goals

- No autonomous posting to social platforms.
- No cloned voices without documented permission.
- No scraped or copied creator scripts.
- No dependency on lip sync for normal narration-driven videos.
- No attempt to generate a new 3D character for every shot.
- No dynamic cloth, hair, or fluid simulation unless a shot specifically requires it.
- No claim of production readiness until a full video can be regenerated from a clean project state.

---

# 3. Core Workflow

## Primary Command

~~~bash
ps1film make \
  --topic "What happened inside Pompeii during the eruption?" \
  --duration 50 \
  --format vertical \
  --preset historical_ps1 \
  --review-script
~~~

## Expected Workflow

1. Create a project ID and immutable input manifest.
2. Research factual claims or ingest user-provided sources.
3. Write an original script with citations linked to claims.
4. Pause for script approval when review mode is enabled.
5. Break the script into beats and shots.
6. Validate every shot against the shot schema.
7. Resolve characters, props, environments, and motions.
8. Generate a storyboard or low-cost viewport preview.
9. Pause for storyboard approval when review mode is enabled.
10. Build Blender scenes through Blender Python, optionally invoked through MCP.
11. Render each shot.
12. Create narration, captions, and audio mix.
13. Assemble the final video.
14. Run automated quality checks.
15. Export the video and production manifest.

## Project State Machine

~~~text
DRAFT
  -> SCRIPT_READY
  -> SCRIPT_APPROVED
  -> SHOTS_PLANNED
  -> ASSETS_RESOLVED
  -> PREVIEW_RENDERED
  -> PREVIEW_APPROVED
  -> FINAL_RENDERED
  -> EDITED
  -> QC_PASSED
  -> DELIVERED
~~~

Any failed stage must be resumable without repeating successful expensive stages.

---

# 4. High-Level Architecture

~~~text
Topic or script
      |
      v
Research and script layer
      |
      v
Validated production plan
      |
      v
Shot JSON + asset requirements
      |
      v
Asset router ------------------------------+
  |         |          |          |        |
local    approved    approved   generated   |
catalog  CC assets   imports    fallback    |
  +---------+----------+----------+----------+
                       |
                       v
                 PS1 normalization
                       |
                       v
                 Blender scene builder
                  |       |       |
               motion   camera  effects
                  |       |       |
                  +-------+-------+
                       |
                       v
                  Eevee rendering
                       |
                       v
Narration + captions + SFX + music
                       |
                       v
                 FFmpeg assembly
                       |
                       v
              final.mp4 + manifest.json
~~~

## Architectural Rules

- The planner produces data; it does not directly manipulate Blender.
- Blender scripts consume validated data; they do not interpret vague prose.
- All external tools and models sit behind adapters.
- Search the asset library before generating an asset.
- Use known animation clips before generative motion.
- Use deterministic keyframes or physics for simple object movement.
- Every artifact is associated with a stable project ID.
- Record the model, prompt, seed, version, and license for generated results.
- A production must be rebuildable from its manifest.
- MCP is an interface, not the source of truth.
- Durable production behavior belongs in version-controlled code.

---

# 5. Recommended Repository Structure

~~~text
ps1-short-factory/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── .env.example
├── configs/
│   ├── default.yaml
│   ├── presets/
│   │   ├── historical_ps1.yaml
│   │   ├── anatomy_ps1.yaml
│   │   └── explainer_ps1.yaml
│   └── schemas/
│       ├── project.schema.json
│       ├── script.schema.json
│       ├── shot.schema.json
│       └── asset.schema.json
├── src/ps1film/
│   ├── cli.py
│   ├── config.py
│   ├── logging.py
│   ├── pipeline.py
│   ├── state.py
│   ├── models/
│   │   ├── project.py
│   │   ├── script.py
│   │   ├── shot.py
│   │   ├── asset.py
│   │   └── manifest.py
│   ├── planning/
│   │   ├── researcher.py
│   │   ├── scriptwriter.py
│   │   ├── beat_planner.py
│   │   ├── shot_planner.py
│   │   └── validators.py
│   ├── assets/
│   │   ├── catalog.py
│   │   ├── resolver.py
│   │   ├── provenance.py
│   │   ├── importers.py
│   │   └── ps1ify.py
│   ├── characters/
│   │   ├── generator.py
│   │   ├── wardrobe.py
│   │   ├── rig.py
│   │   └── presets.py
│   ├── motion/
│   │   ├── router.py
│   │   ├── library.py
│   │   ├── retarget.py
│   │   ├── procedural.py
│   │   └── adapters/
│   │       ├── base.py
│   │       ├── mdm.py
│   │       ├── dip.py
│   │       ├── unimate.py
│   │       ├── gvhmr.py
│   │       └── freemocap.py
│   ├── blender/
│   │   ├── bridge.py
│   │   ├── scene_builder.py
│   │   ├── materials.py
│   │   ├── lighting.py
│   │   ├── cameras.py
│   │   ├── effects.py
│   │   ├── render.py
│   │   └── bootstrap_blender.py
│   ├── audio/
│   │   ├── narration.py
│   │   ├── captions.py
│   │   ├── sfx.py
│   │   └── mix.py
│   ├── edit/
│   │   ├── ffmpeg.py
│   │   └── timeline.py
│   ├── qc/
│   │   ├── technical.py
│   │   ├── visual.py
│   │   ├── factual.py
│   │   └── licensing.py
│   └── adapters/
│       ├── llm.py
│       ├── tts.py
│       └── storage.py
├── blender/
│   ├── templates/
│   │   ├── vertical_base.blend
│   │   └── humanoid_stage.blend
│   ├── scripts/
│   │   ├── build_project.py
│   │   ├── build_shot.py
│   │   ├── render_shot.py
│   │   └── validate_scene.py
│   └── addons/
├── assets/
│   ├── catalog.sqlite
│   ├── characters/
│   ├── environments/
│   ├── props/
│   ├── anatomy/
│   ├── motions/
│   ├── cameras/
│   ├── lights/
│   ├── sfx/
│   └── music/
├── projects/
│   └── .gitkeep
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── smoke/
├── scripts/
│   ├── check_environment.sh
│   ├── index_assets.py
│   └── smoke_render.sh
└── docs/
    ├── SETUP.md
    ├── ASSET_POLICY.md
    ├── BLENDER_MCP.md
    ├── STYLE_BIBLE.md
    ├── MOTION_BACKENDS.md
    └── TROUBLESHOOTING.md
~~~

If the repository already has a sensible structure, adapt this design instead of replacing it gratuitously.

---

# 6. Technology Defaults

Use these as defaults, not unchangeable assumptions:

- Python 3.11+ for orchestration
- Blender-supported Python for in-Blender scripts
- Blender with Eevee for scene generation and rendering
- Pydantic v2 for internal data contracts
- Typer for the command-line interface
- YAML for human-edited configuration
- JSON for project manifests and shot interchange
- SQLite for the local asset catalog
- pytest for tests
- FFmpeg and ffprobe for video and audio processing
- Structured JSON logging
- Subprocess boundaries for Blender and FFmpeg
- Optional Claude/LLM adapter for planning
- Optional Blender MCP adapter for interactive direction and debugging

Pin versions after the first successful environment audit. Do not hard-code a Blender version before inspecting the installed version.

---

# 7. Data Contracts

## 7.1 Project Specification

~~~yaml
project_id: pompeii_001
title: "The Last Minutes of Pompeii"
topic: "What happened inside Pompeii during the eruption?"
format: vertical
duration_seconds: 50
fps: 24
style_preset: historical_ps1
language: en-US

review_gates:
  script: true
  storyboard: true
  final: true

research:
  required: true
  minimum_primary_sources: 2

output:
  working_resolution: [360, 640]
  delivery_resolution: [1080, 1920]
  container: mp4
  video_codec: h264
  audio_codec: aac
~~~

## 7.2 Script Model

~~~yaml
title: "The Last Minutes of Pompeii"
hook: "Pompeii did not disappear in a wall of lava."

narration:
  - id: n001
    text: "The first warning was a towering column of ash."
    estimated_start: 0.0
    estimated_end: 4.2
    claims: [claim_001]

claims:
  - id: claim_001
    text: "The eruption produced a tall column of ash before later destructive flows."
    sources: [source_001, source_002]

sources:
  - id: source_001
    title: "Source title"
    url: "https://example.org/source"
    source_type: primary
    accessed_at: "ISO-8601 timestamp"
~~~

## 7.3 Shot Model

Every shot must have one clear narrative purpose and one dominant visual idea.

~~~yaml
shot_id: s014
duration_seconds: 3.1
narration_ids: [n004]
purpose: "Build suspense before the guard reacts."

environment:
  asset_id: medieval_castle_corridor_v2
  location: [0.0, 0.0, 0.0]

characters:
  - instance_id: guard_01
    asset_id: humanoid_guard_v1
    spawn:
      location: [0.0, -2.0, 0.0]
      rotation_euler: [0.0, 0.0, 0.0]
    action:
      semantic: "walk cautiously, stop suddenly, look toward the floor"
      backend: auto
      fallback_motion_ids:
        - walk_cautious_v1
        - stop_alert_v1

props:
  - instance_id: torch_01
    asset_id: wall_torch_v1
    animation:
      type: procedural
      preset: flame_flicker

camera:
  preset: slow_dolly_medium
  lens_mm: 35
  subject: guard_01
  start:
    location: [0.0, -6.0, 1.6]
  end:
    location: [0.0, -4.4, 1.6]

lighting:
  preset: torch_moonlight

effects:
  - preset: dust_particles_low

caption:
  emphasis_words: ["heard", "beneath"]

transitions:
  in: cut
  out: cut
~~~

## 7.4 Asset Metadata

~~~yaml
asset_id: medieval_table_wood_v3
name: "Low-poly medieval wooden table"
kind: prop

source:
  provider: local
  source_url: null
  creator: internal

license:
  identifier: CC0-1.0
  commercial_use: true
  attribution_required: false
  proof_path: licenses/medieval_table_wood_v3.txt

files:
  blend: props/medieval/table_v3.blend
  glb: props/medieval/table_v3.glb

geometry:
  triangles: 412
  dimensions_m: [1.8, 0.8, 0.75]

style:
  tags:
    - low_poly
    - ps1
    - medieval
    - wood

rig:
  type: none

review:
  geometry_passed: true
  material_passed: true
  license_passed: true

checksum: "sha256:..."
~~~

Reject assets whose licensing information is missing. Unknown-license assets may enter a quarantine folder but may not enter a production render.

---

# 8. PS1 Visual Style Bible

The low-poly aesthetic is a production advantage, not merely a filter.

## Default Output Settings

~~~yaml
render:
  engine: BLENDER_EEVEE_NEXT
  fps: 24

  working_resolution:
    width: 360
    height: 640
    percentage: 100

  delivery_resolution:
    width: 1080
    height: 1920

  upscale_filter: neighbor
  motion_blur: false
  ambient_occlusion: true
  transparent_background: false

geometry:
  characters:
    target_triangles_min: 600
    target_triangles_max: 2500

  hero_props:
    target_triangles_max: 1200

  background_props:
    target_triangles_max: 500

  triangulate: true
  flat_shading: true

textures:
  background_size: 64
  standard_size: 128
  hero_size: 256
  interpolation: closest
  color_quantization: optional
  texture_atlas_preferred: true

materials:
  roughness_default: 1.0
  metallic_default: 0.0
  node_complexity: minimal

post:
  anti_aliasing: low_or_disabled
  dithering: true
  chromatic_aberration: subtle_optional
  scanlines: false_by_default
  film_grain: subtle
  vertex_jitter: subtle_optional
  affine_texture_warp: optional
~~~

## Readability Rules

- Silhouette and staging matter more than geometry.
- Use a restrained palette with one focal accent.
- Keep the subject away from caption-safe areas.
- Avoid dense facial detail.
- Favor narration over dialogue.
- Use exaggerated poses that remain readable on a phone.
- Use cuts, push-ins, cutaways, x-ray views, and object tracking to explain ideas.
- Background crowds may use palette and scale variants of a small number of models.
- Do not make retro defects so aggressive that anatomy or historical action becomes unclear.

## Required `ps1ify()` Function

Implement an idempotent operation conceptually equivalent to:

~~~python
result = ps1ify(
    source_object,
    target_triangles=800,
    texture_size=128,
    flat_shading=True,
    triangulate=True,
    texture_filter="closest",
    quantize_palette=True,
    vertex_jitter_strength=0.0,
)
~~~

It should:

1. Duplicate the source into a non-destructive working collection.
2. Normalize scale and transforms.
3. Remove hidden or irrelevant geometry when safe.
4. Decimate toward the target triangle budget.
5. Triangulate the mesh.
6. Set flat shading.
7. Reduce and consolidate materials.
8. Resize or rebake textures.
9. Force nearest-neighbor texture sampling.
10. Optionally quantize colors.
11. Optionally add subtle shader-based or post-process vertex jitter.
12. Validate normals, UVs, missing textures, and triangle count.
13. Record before-and-after metrics.
14. Cache the result using the source checksum and preset version.

Never destructively modify the original imported asset.

---

# 9. Asset System

## Search Order

~~~text
1. Approved local catalog
2. Existing project assets
3. Approved external CC0 or commercially usable libraries
4. Procedural construction in Blender
5. Image-to-3D generation
6. Manual review queue
~~~

Do not regenerate a cannon, chair, tree, or generic human if an approved reusable asset already exists.

## Initial Asset Sources

- **Poly Pizza:** Useful low-poly discovery source. Licenses vary by asset. Prefer explicit CC0 assets and store licensing proof.
- **Kenney:** Strong source of low-poly packs, commonly CC0. Verify and record the license for every downloaded pack.
- **Existing local assets:** Models owned or licensed by the user.
- **BlenderKit:** Use only when the asset-specific license is recorded and commercially compatible.
- **MPFB2:** Possible bootstrap system for human variants, followed by aggressive simplification.
- **TRELLIS, TripoSR, or InstantMesh:** Optional missing-asset generators after reviewing code licenses, weight licenses, model-card terms, and output rights.

## Asset Router Interface

~~~python
class AssetResolver(Protocol):
    def resolve(self, request: AssetRequest) -> AssetResolution:
        """Return an approved asset, generation job, or actionable failure."""
~~~

~~~python
class AssetRequest(BaseModel):
    kind: Literal[
        "character",
        "prop",
        "environment",
        "anatomy",
        "vehicle",
        "animal",
    ]
    query: str
    required_tags: list[str] = []
    optional_tags: list[str] = []
    style: str = "ps1_low_poly"
    max_triangles: int | None = None
    rig_type: str | None = None
    commercial_use_required: bool = True
~~~

## Catalog Features

- Full-text search across name, description, tags, era, region, and usage
- Stable asset IDs independent of filenames
- Geometry and texture statistics
- Rig and animation compatibility
- Thumbnail or turntable preview
- Source, creator, URL, license, proof, and attribution
- File checksum and normalized-cache checksum
- Approved, rejected, quarantine, and needs-review states
- Usage count so common assets can be improved first

## Catalog Hierarchy

~~~text
assets/
├── characters/
│   ├── humanoid/base/
│   ├── historical/roman/
│   ├── historical/medieval/
│   └── modern/
├── props/
│   ├── weapons/
│   ├── furniture/
│   ├── medical/
│   ├── food/
│   └── tools/
├── environments/
│   ├── ancient/
│   ├── medieval/
│   ├── industrial/
│   └── modern/
├── anatomy/
│   ├── skeleton/
│   ├── organs/
│   └── cutaways/
└── motions/
    ├── locomotion/
    ├── reactions/
    ├── combat/
    ├── labor/
    └── social/
~~~

---

# 10. Character System

Build a modular low-poly character system instead of generating every person independently.

## Canonical Body Families

~~~text
male_small
male_average
male_large
male_old

female_small
female_average
female_large
female_old

teen
child
~~~

These are visual presets, not separate skeleton standards unless their proportions require a controlled retargeting step.

## Modular Components

~~~text
heads/
eyes/
hair/
beards/
torsos/
hands/
shirts/
jackets/
pants/
skirts/
boots/
hats/
armor/
uniforms/
accessories/
~~~

## Canonical Skeleton

All ordinary humanoids should target a versioned skeleton called `PS1_HUMANOID_V1`.

~~~text
root
└── pelvis
    ├── spine
    │   └── chest
    │       ├── neck
    │       │   └── head
    │       ├── upper_arm.L
    │       │   └── forearm.L
    │       │       └── hand.L
    │       └── upper_arm.R
    │           └── forearm.R
    │               └── hand.R
    ├── thigh.L
    │   └── shin.L
    │       └── foot.L
    └── thigh.R
        └── shin.R
            └── foot.R
~~~

The production skeleton may contain twist, toe, finger, facial, and control bones, but the deformation and export contract must remain stable and versioned.

## Example Character Recipe

~~~yaml
character_id: napoleon_v1
skeleton: PS1_HUMANOID_V1
body: male_average
age_visual: 45
head: head_04
hair: dark_short_03
facial_hair: none

wardrobe:
  - french_officer_coat_01
  - white_breeches_01
  - riding_boots_01
  - bicorne_01

palette:
  skin: light_warm_02
  coat: navy_01
  accents: gold_01
~~~

Use Rigify internally if it improves authoring, but export and motion routing must target the canonical deform skeleton. Do not couple the entire library to volatile control-rig bone names.

## Faces and Speech

Narration is the default.

Most characters should communicate through:

- Posture
- Head turns
- Hand gestures
- Movement
- Camera framing

Optional PS1 mouth states:

- Closed
- Open
- O
- E
- Smile
- Grimace

Rhubarb Lip Sync may be added as an optional adapter for occasional dialogue. It is not an MVP dependency.

---

# 11. Motion System

## Routing Principle

Use the cheapest reliable technique that satisfies the shot.

~~~text
Action request
    |
    v
Exact approved clip available? ---- yes ---> use clip
    |
    no
    v
Can it be procedural? ------------- yes ---> keyframes/constraints/physics
    |
    no
    v
Can clips be blended? ------------- yes ---> compose and bake
    |
    no
    v
Human text-to-motion available? --- yes ---> MDM/DiP adapter
    |
    no
    v
Reference video available? -------- yes ---> GVHMR/FreeMoCap adapter
    |
    no
    v
Arbitrary skeleton model ready? --- yes ---> UniMate adapter
    |
    no
    v
Create review task with closest fallback
~~~

## Initial Reusable Motion Library

The first 50 clips should focus on high-frequency actions:

- Idle neutral
- Idle alert
- Idle afraid
- Idle injured
- Walk
- Cautious walk
- Run
- Sprint
- Limp
- Stop
- Turn left
- Turn right
- Look up
- Look down
- Point
- Wave
- Salute
- Handshake
- Sit
- Stand
- Kneel
- Crouch
- Pick up
- Put down
- Push
- Pull
- Carry
- Punch
- Block
- Sword slash
- Stab
- Recoil
- Fall forward
- Fall backward
- Collapse
- Trip
- Recover
- Open door
- Close door
- Climb short ladder
- Shovel
- Hammer
- Write
- Inspect
- Cover face
- Clutch chest
- Grab shoulder
- Crowd panic loop
- Crowd cheer loop

Add animal movements only as projects require them.

Every motion clip needs:

- Stable motion ID
- Source and license
- Source skeleton
- Target skeleton compatibility
- Duration and frame rate
- Root-motion status
- Contact annotations
- Looping status
- Tags and semantic description
- Preview
- Retarget quality score

## Motion Adapter Interface

~~~python
class MotionBackend(ABC):
    name: str

    @abstractmethod
    def available(self) -> Availability:
        ...

    @abstractmethod
    def supports(self, request: MotionRequest) -> bool:
        ...

    @abstractmethod
    def generate(self, request: MotionRequest) -> MotionResult:
        ...
~~~

~~~python
class MotionRequest(BaseModel):
    semantic_action: str
    skeleton_id: str
    duration_seconds: float
    fps: int = 24
    loop: bool = False
    root_motion: bool = True
    start_pose_id: str | None = None
    end_pose_id: str | None = None
    reference_video: Path | None = None
~~~

## Motion Backends

### Reusable BVH, FBX, or Blender Actions

Primary MVP backend.

Use these for common motions such as:

- Walking
- Running
- Pointing
- Falling
- Sitting
- Striking
- Carrying objects

### Procedural Blender Animation

Primary MVP backend for:

- Props
- Mechanisms
- Cameras
- Doors
- Projectiles
- Cutaways
- Anatomical transitions
- Basic gestures
- Simple crowds

### MDM and DiP

Optional human text-to-motion backends.

Example:

~~~text
"He staggers backward and collapses."
        |
        v
MDM or DiP
        |
        v
Motion representation
        |
        v
BVH conversion
        |
        v
Retarget to PS1_HUMANOID_V1
~~~

### GVHMR

Optional reference-video-to-motion backend.

Example:

~~~text
reference_sword_swing.mp4
        |
        v
GVHMR
        |
        v
Recovered human motion
        |
        v
Retarget and clean
        |
        v
PS1 knight animation
~~~

### FreeMoCap

Optional custom markerless motion-capture system.

Record useful actions once, clean them, and store them permanently.

### UniMate

Future text-to-animation backend for varied skeleton topologies.

Potential applications include:

- Humans
- Dogs
- Horses
- Birds
- Insects
- Snakes
- Dragons
- Articulated machines

UniMate should not be the backbone of the initial system.

Implement a disabled adapter and capability check so it can be activated later without changing the shot schema.

~~~yaml
motion:
  backends:
    library:
      enabled: true
      priority: 100

    procedural:
      enabled: true
      priority: 90

    dip:
      enabled: false
      priority: 60

    mdm:
      enabled: false
      priority: 50

    gvhmr:
      enabled: false
      priority: 40

    unimate:
      enabled: false
      priority: 30
~~~

When official checkpoints, dependencies, and inference behavior are practical, enable the adapter without changing `Shot`, `MotionRequest`, or Blender scene interfaces.

The adapter must reject unsupported skeletons clearly. It must never silently return an animation for the wrong topology.

---

# 12. Blender and MCP Integration

Claude is connected to Blender through MCP.

Use MCP for:

- High-level direction
- Environment inspection
- Interactive corrections
- Triggering stable operations
- Previewing scenes
- Diagnosing failed scenes

Put durable production logic in version-controlled Blender Python scripts.

## MCP Chat History Is Not the Build System

A scene must be reproducible through explicit data and scripts:

~~~bash
blender \
  --background blender/templates/vertical_base.blend \
  --python blender/scripts/build_project.py \
  -- \
  --project projects/pompeii_001/project.json
~~~

The exact Blender invocation may vary by installed version and operating system.

The bridge must construct subprocess argument arrays safely and avoid shell interpolation.

## MCP Tool Surface

If the installed Blender MCP server permits custom tools, expose a small stable API:

~~~text
inspect_blender_environment()
validate_project(project_path)
search_asset(query, filters)
import_asset(asset_id, collection)
ps1ify_object(object_name, preset)
create_character(recipe_path)
apply_motion(character_name, motion_id)
build_shot(shot_path)
preview_shot(shot_id)
render_shot(shot_id, quality)
inspect_scene(shot_id)
run_scene_qc(shot_id)
~~~

Do not expose dozens of low-level mesh operations to the planner when one tested high-level operation will work.

## Scene Isolation

Each shot should be independently buildable and renderable.

Possible approaches:

- One `.blend` file per shot
- A base `.blend` with linked collections and deterministic shot assembly

For the MVP, one generated `.blend` per shot is easier to debug and resume.

## Scene Collections

~~~text
SHOT_ROOT
├── ENVIRONMENT
├── CHARACTERS
├── PROPS
├── FX
├── LIGHTS
├── CAMERA
└── DEBUG
~~~

The final render must disable the `DEBUG` collection automatically.

## Idempotency

Running the same build command twice must not duplicate:

- Objects
- Actions
- Cameras
- Lights
- Collections
- Materials

Generated objects should use stable names derived from project and instance IDs.

---

# 13. Camera Director

The camera system should use tested shot presets plus automatic framing.

## Initial Presets

- `establishing_wide`
- `medium_static`
- `closeup_static`
- `slow_dolly_medium`
- `orbit_reveal`
- `overhead_explainer`
- `object_tracking`
- `anatomy_cutaway`
- `first_person_reconstruction`
- `rapid_push_in`
- `lateral_follow`
- `impact_freeze`

## Automatic Framing Requirements

- Resolve a named subject or target object.
- Compute its world-space bounds.
- Choose distance using lens and desired frame occupancy.
- Respect vertical safe zones for captions and application overlays.
- Prevent near-plane clipping.
- Ray-test for major occlusion.
- Warn if the subject leaves the frame.
- Apply damped tracking or generated keyframes.
- Allow manual overrides in Shot JSON.

## Pacing

Short-form videos often benefit from a new visual beat every one to four seconds, but do not force cuts that damage comprehension.

Narration beats should determine shot duration.

---

# 14. Lighting and Environments

Use a small set of reliable lighting presets:

- `daylight_soft`
- `sunset_dramatic`
- `moonlight_cool`
- `torch_moonlight`
- `clinical_bright`
- `industrial_harsh`
- `interior_window`
- `silhouette_backlight`
- `anatomy_explainer`

Each preset should define:

- World color and strength
- Key light
- Fill light
- Rim light
- Shadow softness
- Exposure
- Optional volumetrics
- Palette tags

Keep lighting deterministic and inexpensive.

The PS1 style does not excuse unreadable silhouettes.

## Environment Anchors

Environments should use semantic anchors such as:

~~~text
DOOR_MAIN
TABLE_CENTER
STREET_PATH_A
WINDOW_PRIMARY
CAMERA_ESTABLISHING_01
CHARACTER_START_A
CHARACTER_TARGET_A
~~~

Claude should position actors relative to semantic anchors instead of guessing raw coordinates whenever possible.

---

# 15. Procedural Explainer Effects

Zack D.-style explanatory visuals often depend more on procedural Blender systems than complicated character motion.

Build reusable systems for:

- Transparency and x-ray material transitions
- Anatomical cutaways
- Object-follow paths
- Liquid or particle proxies
- Impact visualization
- Trajectory lines
- Exploded assemblies
- Before-and-after splits
- Time slowdown
- Cross-section reveals
- Heat
- Smoke
- Sparks
- Dust
- Debris
- Crowd duplication and variation
- Arrows and visual highlights

Effects must expose declarative parameters and provide inexpensive preview settings.

Example:

~~~yaml
effects:
  - preset: xray_reveal
    target: body_01
    reveal_start: 0.4
    reveal_end: 1.0
    preserve_objects:
      - skeleton_01
      - arrow_01

  - preset: path_tracer
    object: arrow_01
    path: arrow_trajectory
    color: red
~~~

---

# 16. Narration, Captions, and Editing

## Narration

Create a provider interface.

A local Kokoro adapter is a strong option, but the project must also accept user-supplied WAV files.

~~~python
class TTSProvider(Protocol):
    def synthesize(
        self,
        text: str,
        voice: str,
        output_path: Path,
    ) -> TTSResult:
        ...
~~~

Record:

- Provider
- Model and version
- Voice ID
- Settings
- Input-text checksum
- Output checksum
- Consent and provenance for custom voices

Do not imitate a recognizable living person's voice without documented permission.

## Captions

Use narration timing directly when available. Otherwise use `whisper.cpp` or another timing adapter.

Caption defaults:

- Large, readable type
- Maximum two lines
- Short semantic chunks
- High contrast
- Safe vertical placement
- Optional highlighted word
- Exact transcript preserved in accessibility output

Generate:

- SRT
- ASS
- Clean video master
- Captioned video master

Burn the ASS captions into the social-media delivery file while preserving the clean master and SRT.

## Audio Mix

- Normalize narration first.
- Duck music beneath narration.
- Keep sound effects subordinate unless they are the narrative focus.
- Detect clipping and excessive true peak.
- Export stems where practical.
- Use only licensed or owned music and sound effects.

## Timeline Manifest

The editing layer consumes a timeline manifest, not loose guesses.

~~~yaml
timeline:
  fps: 24

  shots:
    - shot_id: s001
      file: renders/s001/final.mp4
      in: 0.0
      duration: 2.6

    - shot_id: s002
      file: renders/s002/final.mp4
      in: 0.0
      duration: 3.2

  narration: audio/narration.wav
  music: audio/music.wav

  sfx:
    - file: audio/sfx/rumble.wav
      start: 4.1
      gain_db: -9.0

  captions: captions/final.ass
~~~

Use `ffprobe` to validate every input before final assembly.

---

# 17. Research and Factual Integrity

Historical, medical, and scientific shorts can spread errors at scale.

The content pipeline needs claim-level provenance.

## Rules

- Separate sourced facts from dramatized connective tissue.
- Store citations beside the claim they support.
- Prefer primary and authoritative sources.
- Require stronger review for medical, legal, financial, or graphic claims.
- Never show an uncertain reconstruction as confirmed fact without signaling uncertainty.
- Save source title, URL, author or organization, publication date, and access date.
- Recheck time-sensitive facts at production time.
- Run a consistency check between narration, captions, visuals, and cited claims.
- Do not invent a materially false visual mechanism merely because it looks more dramatic.

---

# 18. Originality and Licensing

The goal is to learn from successful explanatory-video grammar, not clone another creator.

## Required Constraints

- Original scripts
- Original channel name
- Original logo
- Original typography
- Original characters
- Original sound identity
- No shots traced from a specific creator video
- No reuploaded creator audio
- No assets without recorded permission or licensing
- No assumption that code, model weights, datasets, and generated outputs share the same license
- Review commercial restrictions before enabling any model
- Store attribution even when it is not legally required
- Maintain a machine-readable production bill of materials

## Tool and Model Caveats

- Blender, FFmpeg, Rigify, and individual add-ons have their own licenses and obligations.
- MDM or DiP code licensing does not automatically clear every dataset or body-model dependency.
- MPFB2 code and assets must be reviewed separately.
- Hunyuan3D variants may use custom terms and must not automatically be treated as MIT or Apache software.
- Poly Pizza asset licenses vary.
- Kenney licenses should be recorded per pack.
- UniMate code, checkpoints, datasets, and downstream asset rights must each be reviewed before commercial activation.
- Verify current terms from primary sources during setup instead of relying solely on this planning document.

---

# 19. Configuration

Example `configs/default.yaml`:

~~~yaml
project_root: projects
asset_root: assets
cache_root: .cache/ps1film

blender:
  executable: blender
  template: blender/templates/vertical_base.blend
  use_mcp: true
  timeout_seconds: 900

render:
  preview:
    resolution: [180, 320]
    samples: 8

  final:
    resolution: [360, 640]
    samples: 32

  delivery: [1080, 1920]
  fps: 24

assets:
  catalog: assets/catalog.sqlite
  require_license: true

  allowed_licenses:
    - CC0-1.0
    - CC-BY-4.0
    - proprietary-owned

  search_local_first: true
  allow_network_downloads: false

motion:
  canonical_skeleton: PS1_HUMANOID_V1
  default_backend: auto
  require_preview_for_generated_motion: true

audio:
  tts_provider: kokoro
  caption_provider: whisper_cpp
  loudness_target_lufs: -14

review:
  script: true
  storyboard: true
  generated_assets: true
  generated_motion: true
  final: true
~~~

Network downloads should be opt-in and logged.

Tests must never require network access.

---

# 20. CLI Design

~~~bash
# Audit local dependencies
ps1film doctor

# Initialize a project
ps1film init \
  --topic "How Roman concrete survived seawater" \
  --id roman_concrete_001

# Create or import a script
ps1film script create projects/roman_concrete_001
ps1film script import projects/roman_concrete_001 script.md
ps1film approve script projects/roman_concrete_001

# Plan and validate shots
ps1film shots plan projects/roman_concrete_001
ps1film shots validate projects/roman_concrete_001

# Manage assets
ps1film assets index
ps1film assets search "roman harbor stone"
ps1film assets inspect roman_wall_v2
ps1film assets ps1ify source.glb --preset prop_standard

# Preview and render
ps1film preview projects/roman_concrete_001 --shot s003
ps1film render projects/roman_concrete_001 --quality preview
ps1film render projects/roman_concrete_001 --quality final --resume

# Audio and final assembly
ps1film narrate projects/roman_concrete_001
ps1film captions projects/roman_concrete_001
ps1film assemble projects/roman_concrete_001
ps1film qc projects/roman_concrete_001

# Run the approved pipeline
ps1film make projects/roman_concrete_001 --resume
~~~

Every command must support `--help`.

Mutating or expensive commands should support `--dry-run` where useful.

---

# 21. Observability and Reproducibility

Every project writes:

~~~text
projects/{project_id}/
├── project.yaml
├── state.json
├── script/
├── shots/
├── assets.lock.json
├── scenes/
├── previews/
├── renders/
├── audio/
├── captions/
├── final/
│   ├── clean_master.mp4
│   ├── captioned_master.mp4
│   └── final_manifest.json
└── logs/
~~~

The final manifest must include:

- Project and pipeline versions
- Timestamps
- Script checksum
- Source list and claim map
- Shot specifications
- Every asset ID and checksum
- Every asset source and license
- Every motion ID or generation record
- Blender and FFmpeg versions
- Render settings
- TTS and transcription metadata
- Output checksums
- QC results
- Warnings and manual overrides

Use deterministic seeds when a dependency supports them.

Cache expensive work using input hashes rather than filenames alone.

---

# 22. Quality Control

## Technical Checks

- Output is exactly 1080 × 1920.
- Frame rate and duration are within the configured tolerance.
- Video decodes from start to finish.
- Audio exists and is synchronized.
- Audio does not clip.
- No missing textures.
- No pink Blender materials.
- No empty shots.
- No unintended black frames.
- Camera does not clip through the primary subject.
- No unapproved debug objects appear.
- Captions remain inside safe zones.
- All referenced files exist.
- All assets pass the licensing policy.

## Visual Checks

- The dominant subject is readable on a phone.
- Action matches narration.
- Character feet do not visibly slide in important shots.
- Hands and props do not obviously separate during contact.
- No severe mesh intersections.
- No photorealistic asset accidentally breaks the style.
- Palette and lighting remain coherent.
- Retro effects do not obscure the explanation.
- The first two seconds communicate a hook.
- Every shot has a clear purpose.

## Factual and Editorial Checks

- Every factual assertion has a source or is labeled as interpretation.
- Captions match spoken words.
- Dates, quantities, names, and labels are consistent.
- The video does not present dramatization as archival footage.
- The script and shot sequence are original.
- Graphic anatomy or violence is suitable for the target platform and audience.

---

# 23. Testing Strategy

## Unit Tests

Test:

- Pydantic validation for every schema
- Asset-license gating
- Asset-ranking behavior
- Stable naming
- Scene idempotency
- Motion-router priority and fallback
- Timing calculations
- FFmpeg command generation
- Cache keys and checksums
- Caption chunking
- Safe-zone calculations

## Integration Tests

Test the ability to:

- Build a shot from fixture JSON
- Import a known GLB
- Normalize it with `ps1ify`
- Apply a known animation
- Position a camera
- Render a tiny preview
- Inspect the output with `ffprobe`
- Assemble two shots with synthetic narration
- Verify final dimensions and duration

## Golden Smoke Project

Create:

~~~text
tests/fixtures/projects/wooden_crate_demo
~~~

The fixture must require no external downloads and should contain:

- One low-poly room
- One humanoid or simple mannequin
- One wooden crate
- One walk or point animation
- Two shots
- Synthetic or supplied tone audio
- Captions
- A ten-second final video

This fixture proves the pipeline without research models or network access.

## Acceptance-Test Command

~~~bash
ps1film doctor
pytest
ps1film make tests/fixtures/projects/wooden_crate_demo --offline --resume
ps1film qc tests/fixtures/projects/wooden_crate_demo
~~~

---

# 24. Security and Reliability

- Treat imported `.blend` files and add-ons as executable-risk inputs.
- Do not automatically execute Python embedded in downloaded Blender files.
- Prefer GLB, FBX, or OBJ for untrusted assets.
- Quarantine downloads until scanned and reviewed.
- Store secrets only in environment variables or an approved secret store.
- Never place API keys in manifests, logs, prompts, screenshots, or committed files.
- Use subprocess argument arrays instead of interpolated shell strings.
- Set timeouts for Blender, FFmpeg, TTS, and model processes.
- Limit generated file sizes and render durations.
- Validate paths to prevent writes outside configured project roots.
- Record failed-stage state safely so `--resume` can continue.
- Clean temporary files only inside a resolved project-specific temporary directory.
- Do not install Blender add-ons or model code from arbitrary repositories without review.

---

# 25. Implementation Phases

## Phase 0: Environment Audit and Skeleton

Deliver:

- Repository audit
- `docs/SETUP.md`
- `pyproject.toml`
- Typed configuration
- CLI with `ps1film doctor`
- Structured logging
- Project-state model
- Core schemas
- Unit-test framework

Exit criteria:

- `doctor` reports Blender, Python, FFmpeg, GPU, and MCP status.
- Configuration loads successfully.
- Tests run locally.
- No external model is required.

## Phase 1: Deterministic Vertical Slice

Deliver:

- Local SQLite asset catalog
- Fixture asset importer
- Initial PS1 material and render preset
- Basic `ps1ify` implementation
- Shot JSON validation
- Blender scene builder
- Static and dolly camera presets
- Reusable animation application
- Eevee preview and final rendering
- FFmpeg assembly
- Captions generated from known timing
- Final production manifest
- Golden smoke project

Exit criteria:

- One command creates a ten-second, two-shot, captioned 1080 × 1920 video from offline fixtures.
- Rerunning with `--resume` does not repeat unchanged work.
- The manifest and QC report are complete.

## Phase 2: Production MVP

Deliver:

- Script and beat-planner adapters
- Human review gates
- Fifty-motion starter catalog
- `PS1_HUMANOID_V1` pipeline
- Modular character recipes
- Environment anchors
- Eight to twelve camera presets
- Six to ten lighting presets
- Kokoro adapter or user-audio path
- `whisper.cpp` timing adapter
- Sound and music mixing
- Storyboard previews
- Three original sample shorts

Exit criteria:

- Three different topics render without code edits.
- Each uses primarily catalog assets.
- Outputs pass technical QC.
- A person can approve the script and preview before final rendering.

## Phase 3: Asset Expansion

Deliver:

- Approved external asset-source adapters where APIs and terms permit
- License ingestion and quarantine workflow
- Improved `ps1ify` caching and texture baking
- MPFB2-based or custom modular human factory
- Optional TRELLIS, TripoSR, and InstantMesh adapters
- Turntable review UI or static review sheets

Exit criteria:

- Missing assets create explicit jobs.
- No unknown-license asset reaches a final build.
- Normalized assets can be reused across projects.

## Phase 4: Advanced Motion

Deliver:

- Retargeting pipeline
- MDM or DiP adapter
- GVHMR adapter
- FreeMoCap ingestion
- Generated-motion preview and approval
- Contact and foot-slide checks
- UniMate adapter when usable checkpoints and terms are verified

Exit criteria:

- Custom human motion can be generated or recovered, previewed, retargeted, approved, and reused.
- The arbitrary-skeleton backend can be enabled without schema changes.

## Phase 5: Scaling

Deliver:

- Render queue
- Worker isolation
- Content-addressed cache
- Asset-popularity analytics
- Batch topic processing
- Cost and time dashboard
- Automated regression renders
- Optional publishing adapters with explicit review and credentials

Exit criteria:

- Multiple projects can run concurrently without collisions.
- Failed workers resume safely.
- Production cost and time can be measured per shot and per video.

---

# 26. Priority Decisions

When engineering tradeoffs appear, prioritize:

1. Reproducibility
2. Clear visual storytelling
3. Asset and licensing provenance
4. Human review for consequential choices
5. Reuse and caching
6. Render speed
7. Visual detail
8. Experimental novelty

A crude shot that is correct, readable, and reproducible is more valuable than a beautiful shot that cannot be regenerated or legally reused.

---

# 27. Open-Source and Open-Weight Candidates

These are candidates to evaluate, not automatic dependencies.

| Layer | Candidate | Role | Timing |
|---|---|---|---|
| 3D engine | Blender | Scene assembly, animation, Eevee rendering | MVP |
| Agent bridge | Blender MCP | Claude-to-Blender interaction | MVP |
| Rig authoring | Rigify | Rig creation and controls | MVP |
| Assets | Poly Pizza | Low-poly discovery; verify license | MVP/Phase 2 |
| Assets | Kenney | Low-poly packs; record pack license | MVP/Phase 2 |
| Humans | MPFB2 | Bootstrap procedural humans | Phase 3 |
| Motion | BVH/Blender actions | Reliable reusable movement | MVP |
| Text-to-motion | MDM/DiP | Generate human motion | Phase 4 |
| Video-to-motion | GVHMR | Recover motion from video | Phase 4 |
| Mocap | FreeMoCap | Record custom movement | Phase 4 |
| Retargeting | BVH retarget tools | Normalize motion to canonical rig | Phase 2/4 |
| Universal motion | UniMate | Varied-skeleton text animation | Phase 4 |
| Image-to-3D | TRELLIS | Generate missing assets | Phase 3 |
| Image-to-3D | TripoSR | Missing-asset fallback | Phase 3 |
| Image-to-3D | InstantMesh | Missing-asset fallback | Phase 3 |
| Narration | Kokoro | Local text-to-speech | Phase 2 |
| Lip sync | Rhubarb Lip Sync | Optional mouth animation | Later |
| Captions | whisper.cpp | Transcription and timing | Phase 2 |
| Assembly | FFmpeg | Editing, encoding, scaling, mixing | MVP |

Perform current primary-source verification before installing anything. Research repositories, model releases, checkpoints, and licenses change quickly.

---

# 28. Reference Links

Use official repositories, project pages, documentation, papers, and license files as authority.

- Blender MCP: https://github.com/ahujasid/blender-mcp
- Blender: https://www.blender.org/
- Blender Python API: https://docs.blender.org/api/current/
- Rigify manual: https://docs.blender.org/manual/en/latest/addons/rigging/rigify/
- Poly Pizza: https://poly.pizza/
- Kenney assets: https://kenney.nl/assets
- MPFB2: https://github.com/makehumancommunity/mpfb2
- MDM/DiP: https://github.com/GuyTevet/motion-diffusion-model
- GVHMR: https://github.com/zju3dv/GVHMR
- FreeMoCap: https://github.com/freemocap/freemocap
- UniMate project: https://linzhanmou.com/unimate/
- UniMate repository: https://github.com/Friedrich-M/UniMate
- TRELLIS: https://github.com/microsoft/TRELLIS
- TripoSR: https://github.com/VAST-AI-Research/TripoSR
- InstantMesh: https://github.com/TencentARC/InstantMesh
- Rhubarb Lip Sync: https://github.com/DanielSWolf/rhubarb-lip-sync
- whisper.cpp: https://github.com/ggml-org/whisper.cpp
- FFmpeg: https://ffmpeg.org/
- Kokoro: https://github.com/hexgrad/kokoro

Repository URLs, checkpoint availability, support status, and licenses must be rechecked at implementation time.

---

# 29. First Assignment for Claude Code

Begin with Phase 0 and Phase 1 only.

## Required First-Pass Deliverables

1. Inspect the current repository and machine.
2. Report what already exists and which dependencies are available.
3. Create or update the repository structure without deleting user work.
4. Implement typed models for:
   - Project
   - Script
   - Shot
   - Asset
   - MotionRequest
   - Timeline
   - Manifest
5. Implement configuration loading with clear validation errors.
6. Implement `ps1film doctor`.
7. Implement an SQLite asset catalog with index, search, and inspect commands.
8. Implement a deterministic asset resolver using approved local assets only.
9. Implement an initial non-destructive `ps1ify` Blender function.
10. Implement a Blender scene builder for a two-shot fixture.
11. Implement `static_medium` and `slow_dolly_medium` camera presets.
12. Apply one reusable animation to a canonical mannequin or humanoid.
13. Render at 360 × 640 using Eevee.
14. Upscale to 1080 × 1920 using nearest-neighbor scaling in FFmpeg.
15. Add synthetic narration/audio or accept a fixture WAV.
16. Generate and burn simple captions.
17. Write a final manifest and QC report.
18. Add unit and integration tests.
19. Run the offline golden smoke project.
20. Update `README.md` with exact commands and known limitations.

## Engineering Behavior

- Make reasonable assumptions and record them.
- Ask only when a missing choice would materially change the architecture or require credentials, paid services, destructive work, or license acceptance.
- Prefer real implementations over placeholder functions.
- If Blender is unavailable, complete the pure-Python layers and provide the exact blocked smoke-test command. Do not falsely mark the render as completed.
- If Blender MCP is unavailable, use headless Blender scripts and document how MCP will invoke those same stable operations later.
- Keep optional AI-model adapters behind interfaces.
- Do not download multi-gigabyte model weights during Phase 1.
- Do not train UniMate.
- Do not add automatic social-media publishing.
- Do not copy scripts, logos, characters, voices, or proprietary assets from reference creators.

End the first pass with:

- Files changed
- Commands run
- Tests passed and failed
- Smoke-render path
- Remaining blockers
- Exact recommended next task

## Definition of Done

The first pass is complete only when this command path is real:

~~~bash
ps1film doctor
pytest
ps1film make tests/fixtures/projects/wooden_crate_demo --offline
ps1film qc tests/fixtures/projects/wooden_crate_demo
~~~

It must produce:

- A valid captioned vertical MP4
- A clean video master
- A machine-readable production manifest
- A QC report

If a system dependency prevents rendering, Claude must return a precise and honest dependency error explaining the single next action required.

---

# 30. Final Direction

Build the deterministic studio before adding experimental intelligence.

The correct initial stack is:

~~~text
Claude + Blender MCP
        |
        v
Structured shot JSON
        |
        v
Local low-poly asset library
        |
        v
PS1_HUMANOID_V1
        |
        v
Reusable motion clips
        |
        v
Procedural cameras and effects
        |
        v
Eevee rendering
        |
        v
Kokoro or supplied narration
        |
        v
Captions + FFmpeg
        |
        v
Finished vertical short
~~~

After the deterministic pipeline works, add advanced systems in this order:

1. MDM or DiP
2. Improved asset generation with TRELLIS
3. GVHMR and FreeMoCap
4. UniMate
5. Distributed rendering and batch production

Treat Claude as a film director manipulating standardized LEGO pieces—not as a model expected to regenerate an entire studio for every shot.
