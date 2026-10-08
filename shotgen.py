"""Gate 4: shot description -> LLM-written bpy script -> rendered still.

Reuses ClipVault's DeepSeek plumbing (`describe.build_ask` -> `clip_vod._make_ask`)
rather than adding another API client, and goes through `clipvault.omni` so the
production .env leak documented in OMNICHROME.md cannot follow us in.

The measurement that matters is the RAW hit rate: one attempt per prompt, no
retries, no hand fixing. A render-analyze-fix loop would raise the number and
tell us nothing about whether the model can actually frame a shot.

    python3 shotgen.py            # all prompts
    python3 shotgen.py "a lone figure at the mouth of a cave"
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, "/home/apollo/clipvault")

BLENDER = HERE / "blender" / "blender"
OUT = HERE / "out" / "shots"
GEN = HERE / "scenes" / "generated"
HDRI = HERE / "assets" / "studio.hdr"

# The contract. Every line here exists because leaving it out produces a
# predictable failure: no camera (black frame), Cycles (minutes per frame),
# GUI operators (crash headless), or a forgotten filepath (renders nowhere).
SYSTEM = f"""You write Blender 4.5 Python (bpy) scripts that render ONE still frame.

The look you are producing: cinematic, dark, atmospheric, high contrast. A
single subject, a large empty space around it, volumetric light, deep shadows.
Think a moody documentary re-enactment, not a product shot and not a cartoon.

HARD RULES - a script that breaks any of these is useless:
- Start with: bpy.ops.wm.read_factory_settings(use_empty=True)
- scene.render.engine = "BLENDER_EEVEE_NEXT"   (never Cycles - it is 50x slower here)
- resolution 1080x1920, PNG, and set scene.render.filepath to the path given to you
- ALWAYS create a camera object and set scene.camera - a missing camera renders black
- ALWAYS create at least one light and a world background
- Finish with: bpy.ops.render.render(write_still=True)
- Only bpy/bmesh/math/mathutils. No GUI operators, no addons, no network, no file
  writes other than the render. Headless: there is no screen, no context override.
- Build geometry from primitives, modifiers and materials. You have no asset
  library except one HDRI at {HDRI} - load it with ShaderNodeTexEnvironment if it
  suits the shot, otherwise build the world procedurally.
- Volumetric atmosphere via a ShaderNodeVolumeScatter on the World Output Volume
  socket, density around 0.01-0.03. This is what sells the style.
- Keep it under ~120 lines and under 30 seconds of render time: taa_render_samples
  no higher than 48.

EEVEE NEXT API - Blender 4.2 REPLACED the old EEVEE and most tutorials you have
seen are for the old one. Getting this wrong is the most common way to fail:
- samples:            scene.eevee.taa_render_samples = 32     (NOT scene.render.*)
- shadows:            scene.eevee.use_shadows = True
- these NO LONGER EXIST and raise AttributeError: use_volumetric_lights,
  use_gtao, use_ssr, use_bloom, use_soft_shadows, volumetric_shadows.
  Bloom and ambient occlusion are gone - do not reference them at all.
- Set ONLY taa_render_samples and use_shadows on scene.eevee. If you want any
  other eevee setting, guard it: if hasattr(scene.eevee, "x"): scene.eevee.x = v
- node links live on the TREE: nt = mat.node_tree; nt.links.new(a.outputs["X"],
  b.inputs["Y"]).  nt.nodes.links does not exist.
- world volume: nt = world.node_tree; v = nt.nodes.new("ShaderNodeVolumeScatter");
  nt.links.new(v.outputs["Volume"], nt.nodes["World Output"].inputs["Volume"])
- a spot/area light points down its own -Z. Do NOT guess rotation_euler - add an
  empty at the subject and a TRACK_TO constraint:
      t = bpy.data.objects.new("Aim", None); t.location = (x, y, z)
      bpy.context.collection.objects.link(t)
      c = light_obj.constraints.new("TRACK_TO"); c.target = t

EXPOSURE - a frame that is black or blown out is a failed shot, and dark scenes
go wrong far more often than bright ones. Light the subject so it is clearly
visible: area/spot energy in the hundreds to low thousands of watts at a few
metres. "Dark and moody" means deep shadows around a LIT subject, not an
underexposed image. Give the subject a visible rim or key light.

Reply with JSON only, exactly: {{"code": "<the full python script>"}}
The value is the script as a single JSON string. No commentary, no markdown."""

PROMPTS = [
    "a lone figure standing at the mouth of an enormous cave, light pouring in behind them",
    "a single wooden chair in the centre of a vast empty concrete room, one hanging bulb above it",
    "a monolithic black stone slab on a cracked desert floor at dusk",
    "a narrow corridor of tall pillars receding into fog, floor wet and reflective",
    "an astronaut's helmet resting alone on grey regolith, earth nowhere in sight",
]


PREAMBLE = (HERE / "scenes" / "preamble.py").read_text()
MANIFEST = json.loads((HERE / "assets" / "models" / "manifest.json").read_text())
TEXTURES = json.loads((HERE / "assets" / "textures" / "manifest.json").read_text())
DESCRIBE = {
    "dining_chair_02": "a single dark leather dining chair, tufted back, wooden legs",
    "gothic_statue": "a weathered stone gothic statue of a robed figure - a good stand-in for a lone person",
    "barrel_03": "a weathered steel drum / barrel",
    "brass_diya_lantern": "a tiny brass oil lamp (0.4 m) - a table prop, NOT a street lantern",
    "marble_bust_01": "a classical marble bust of a head and shoulders",
    "rock_face_01": "a large rock face / cliff wall - stack and rotate several to make a cave or canyon",
    "rock_face_02": "a large rock face / cliff wall, different shape",
    "coastal_cliff_01": "a very large cliff mass - a horizon-scale backdrop",
    "namaqualand_boulder_02": "a rounded boulder, man-height",
    "boulder_01": "a mossy boulder",
    "moon_rock_01": "a small grey stone, 20 cm - scatter several as ground dressing; NOT a boulder",
    "dead_tree_trunk": "a bare dead tree trunk with branches",
    "street_lamp_01": "a tall iron street lamp - use light() at its head for the glow",
    "large_iron_gate": "a large wrought-iron gate - threshold, cemetery, estate",
}


def manifest_table() -> str:
    rows = []
    for name, m in MANIFEST.items():
        x, y, z = m["size_m"]
        rows.append(f'  place("{name}", at=(x, y))  # {DESCRIBE.get(name, name)}; '
                    f"footprint {x:.2f} x {y:.2f} m, height {z:.2f} m")
    return "\n".join(rows)


def texture_table() -> str:
    return "\n".join(f'  ground(texture="{n}")  # {t["desc"]}' for n, t in TEXTURES.items())


ASSET_SYSTEM = f"""You COMPOSE a shot for a cinematic, dark, atmospheric short film.
You do not model objects. Every object comes from the library below, placed with
place(). You build ONLY the environment (ground, walls, pillars, slabs) from
box() and ground(), and you light and frame the shot.

A preamble of helpers is already loaded before your code runs. Use ONLY these
(plus plain math). Do not import bpy yourself, do not call bpy.ops directly, do
not create cameras, lights or materials by hand - the helpers do it correctly.

  sc = reset()                                   # ALWAYS first line
  world(color=(r,g,b), strength=1.0, hdri=None, fog=0.015, anisotropy=0.4)
       # dark sky + volumetric fog. hdri="{HDRI}" is available.
  ground(size=80, texture=NAME|None, scale=6.0, wet=0.0, color=(r,g,b))
       # floor at z=0. ALWAYS pass a texture unless the floor is meant to be
       # featureless. wet=0.6-0.9 for rain / wet street (lights reflect).
  box(size=(sx,sy,sz), at=(x,y), color=(r,g,b), rough=0.7, rot_deg=0)
       # environment block resting on the ground (walls, pillars, plinths)
  root = place(name, at=(x,y), rot_deg=0, scale=1.0)
       # a library object with its BASE on the ground at (x,y). Never floats.
  light("SPOT"|"AREA"|"POINT", location=(x,y,z), at=(x,y,z), energy, size=1.0,
        color=(1,1,1), spot_size=1.0)          # aimed at `at`; energy in watts
  lamp(at=(x,y), toward=(sx,sy), energy=1600)  # street lamp + its bulb, placed
       # correctly. Use this for any lamp/bulb/lantern light source - a light
       # put INSIDE a lamp mesh is shadowed by the lamp and the frame goes black.
  camera(location=(x,y,z), at=(x,y,z), lens=50) # aimed at `at`
  render("{{OUT}}")                              # ALWAYS last line, exactly this

LIBRARY - OBJECTS (heights are REAL metres - frame accordingly; a 0.97 m chair
needs the camera ~1.2-1.6 m high, 3-5 m back; a 1.7 m figure ~1.4-2 m high,
4-7 m back):
{manifest_table()}

LIBRARY - GROUND TEXTURES:
{texture_table()}

ENVIRONMENT - this is where shots fail. A prompt that names a place (cave,
desert, alley, clearing, museum hall) needs that place BUILT: textured ground,
rock faces stacked and rotated into walls, trees at the edges, a cliff as a
backdrop, box() walls with a dark colour for interiors. An empty grey plane
with the subject on it reads as a product photo and will be rejected.

ATMOSPHERE RANGES (measured on this renderer):
- fog: 0.005-0.012 when the camera is more than 6 m from the subject,
  0.015-0.025 when closer. Above 0.03 the frame goes black - it is clamped.
- world strength 0.3-1.0. Dark scenes still need strength >= 0.3 or the fog has
  nothing to scatter and shadows go pure black.
- key light: SPOT 1500-4000 W within 3-6 m, or POINT 300-1200 W within 2-4 m.
  Add a dim AREA fill (40-150 W) from the other side. A "hanging bulb" or
  lamp is lamp(...) - never a POINT light at a lamp model's head.
- NEVER put a light inside or behind geometry. Lights must have a clear line
  to the subject exactly as the camera must.

SIGHTLINE - render() REFUSES to run if any object sits between the camera and
the point it aims at. Do not put walls, pillars or rocks on that line. Put
environment geometry beside and behind the subject, never in front.

EXPOSURE - the most common failure is a frame that is too dark. Put a real key
on the subject: a SPOT of 1500-4000 W a few metres away, plus a dim AREA fill
(40-150 W) from the other side so shadows have detail. "Dark and moody" means
deep shadows around a clearly LIT subject, never an underexposed image.

COMPOSITION - one subject, placed near (0,0). Camera 3-6 m back, slightly above
subject height, aimed at the subject's mid-height. Leave empty space around the
subject; that emptiness is the style.

Reply with JSON only, exactly: {{"code": "<python using only the helpers>"}}
No commentary, no markdown."""

ASSET_PROMPTS = [
    "a lone figure standing at the mouth of an enormous cave, light pouring in behind them",
    "a single wooden chair in the centre of a vast empty concrete room, one hanging bulb above it",
    "a monolithic black stone slab on a cracked desert floor at dusk",
    "a narrow corridor of tall pillars receding into fog, floor wet and reflective",
    "a marble bust on a stone plinth in a dark museum hall, one spotlight from above",
    "an old barrel and a small brass lantern on wet cobbles at night, the lantern the only warm light",
    "a stone statue alone in a fog-filled clearing under cold moonlight",
]


def strip_fence(raw: str) -> str:
    raw = (raw or "").strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        raw = re.sub(r"^(python|py)\s*", "", raw.strip(), flags=re.I)
    return raw.strip()


def generate(prompt: str, ask) -> str:
    """The house helper runs DeepSeek in JSON mode, so the script comes back as
    a JSON string field rather than raw text."""
    from clipvault.describe import _loads

    raw = ask(f"Shot description: {prompt}\n\n"
              f"Render to exactly this path: {{OUT}}\n"
              f"Reply as json: {{\"code\": \"...\"}}")
    try:
        return strip_fence(_loads(raw).get("code", ""))
    except Exception:
        return strip_fence(raw)


def judge(png: Path) -> tuple[bool, str, dict]:
    """Did we get a SHOT, or just a file?

    "The render succeeded" is not the question - a fully black frame is a
    successful render and a useless shot, and an early version of this spike
    scored one as a pass. A usable frame has to be lit (mean luma in a sane
    band), have real contrast, and not be almost entirely crushed to black.
    """
    if not png.exists():
        return False, "no file written", {}
    from PIL import Image, ImageStat

    im = Image.open(png).convert("L")
    st = ImageStat.Stat(im)
    mean, sd = st.mean[0], st.stddev[0]
    hist = im.histogram()
    dark = sum(hist[:8]) / float(im.width * im.height)      # near-black share
    blown = sum(hist[248:]) / float(im.width * im.height)
    stats = {"mean": round(mean, 1), "sd": round(sd, 1),
             "dark": round(dark, 3), "blown": round(blown, 3)}
    if mean < 6:
        return False, f"effectively black (mean luma {mean:.1f})", stats
    if sd < 8:
        return False, f"no contrast, flat frame (sd {sd:.1f})", stats
    if dark > 0.92:
        return False, f"{dark:.0%} of pixels crushed to black", stats
    if blown > 0.35:
        return False, f"{blown:.0%} of pixels blown out", stats
    return True, "", stats


def run_one(idx: int, prompt: str, ask, assets: bool = False,
            attempt: int = 1, feedback: str = "") -> dict:
    out = OUT.parent / ("shots_assets" if assets else "shots")
    gen = GEN.parent / ("generated_assets" if assets else "generated")
    out.mkdir(parents=True, exist_ok=True)
    gen.mkdir(parents=True, exist_ok=True)
    tag = f"shot_{idx:02d}" + (f"_a{attempt}" if attempt > 1 else "")
    png = out / f"{tag}.png"
    script = gen / f"{tag}.py"

    full = prompt
    if feedback:
        full = (f"{prompt}\n\nA previous attempt at this shot was REJECTED by the "
                f"editor. Their notes, which you must fix:\n{feedback}")
    code = generate(full, ask).replace("{OUT}", str(png))
    if assets:
        if "render(" not in code:
            code += f'\nrender("{png}")\n'
        code = PREAMBLE + "\n# --- generated ---\n" + code
    elif str(png) not in code:                  # model ignored the path
        code += f'\nbpy.context.scene.render.filepath = "{png}"\n' \
                'bpy.ops.render.render(write_still=True)\n'
    script.write_text(code)

    t0 = time.time()
    # One Blender at a time. A render peaks at ~2 GB with textured assets and
    # the box has ~3.7 GB free; retries launched in parallel would OOM it.
    import fcntl
    with open(HERE / "out" / ".render.lock", "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        proc = subprocess.run([str(BLENDER), "-b", "-P", str(script)],
                              capture_output=True, text=True, timeout=900)
    el = time.time() - t0
    ok, why, stats = judge(png)
    err = "" if ok else why
    if not ok and not png.exists():
        tail = [l for l in proc.stdout.splitlines() + proc.stderr.splitlines()
                if "Error" in l or "Traceback" in l or "line" in l]
        err = " | ".join(tail[-3:])[:300] or why
    return {"idx": idx, "prompt": prompt, "ok": ok, "seconds": round(el, 1),
            "png": str(png), "script": str(script), "error": err, **stats}


def main() -> int:
    from clipvault import describe as D

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", nargs="?", default=None)
    ap.add_argument("--assets", action="store_true")
    ap.add_argument("--index", type=int, default=None, help="shot number (with a single prompt)")
    ap.add_argument("--attempt", type=int, default=1)
    ap.add_argument("--feedback", default="", help="judge notes from the rejected attempt")
    ap.add_argument("--feedback-file", default=None, help="read the notes from a file")
    a = ap.parse_args()
    if a.feedback_file:
        a.feedback = Path(a.feedback_file).read_text()
    assets = a.assets
    ask = D.build_ask(system=ASSET_SYSTEM if assets else SYSTEM, max_tokens=3500)
    if a.prompt:
        prompts = [(a.index or 1, a.prompt)]
    else:
        prompts = list(enumerate(ASSET_PROMPTS if assets else PROMPTS, 1))
    rows = []
    for i, p in prompts:
        print(f"\n[{i}] attempt {a.attempt}: {p}")
        try:
            r = run_one(i, p, ask, assets=assets, attempt=a.attempt, feedback=a.feedback)
        except Exception as exc:                        # keep the batch alive
            r = {"idx": i, "prompt": p, "ok": False, "seconds": 0,
                 "error": f"{type(exc).__name__}: {exc}"[:300]}
        rows.append(r)
        print(f"    {'RENDERED' if r['ok'] else 'FAILED  '} {r['seconds']}s "
              f"{r.get('error', '')}")
    ok = sum(1 for r in rows if r["ok"])
    print(f"\nrendered {ok}/{len(rows)} on the first attempt")
    tag = ("shotgen_assets" if assets else "shotgen") + (f"_a{a.attempt}" if a.attempt > 1 else "") + ".json"
    (HERE / "out" / tag).write_text(json.dumps(rows, indent=1))
    print("RESULT_JSON " + json.dumps(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
