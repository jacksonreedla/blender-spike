"""v2 post-production: PS1 look, fast lo-fi narration, cuts on words.

  python mvp2/assemble.py narrate      # Kokoro per sentence at SPEED -> lo-fi chain -> script.timed.json + render_plan.json
  python mvp2/assemble.py render-cmds  # writes mvp2/render_all.sh (MVP_PS1=1, flock-serialised)
  python mvp2/assemble.py post         # PNG seqs -> neighbour upscale + 15-bit quantise -> bed -> captions -> mix -> QC
  python mvp2/assemble.py qc <mp4>

script.json shape: beats[{label, act, sentences[{text}]}] + shots[{id, beat (1-based), cut_on (a word in that
beat's sentences; the shot starts when the narrator reaches it), description, ...}]. The first shot of the
video starts at 0 regardless. Run with /home/apollo/clipvault/.venv/bin/python.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/home/apollo/clipvault")
from clipvault import config  # noqa: E402,F401
from clipvault import longrender as LR  # noqa: E402
from clipvault import moviecaptions, narrate, tts  # noqa: E402

MVP = Path("/home/apollo/blender-spike/mvp2")
BLENDER = "/home/apollo/blender-spike/blender/blender"
FPS = 24
W, H = 1080, 1920
SPEED = float(os.environ.get("MVP2_SPEED", "1.3"))      # ~210 wpm
TAIL_S = 0.5
WIND_LUFS = -34
SR = 48000
GAPS = dict(GAP_SENT=0.18, GAP_BEAT=0.32, GAP_REVEAL=0.55, GAP_CTA=0.3)   # narrate's defaults are 0.35/0.8/1.2/0.6
LOFI = ("aresample=11025,aresample=48000,highpass=f=180,lowpass=f=4200,"
        "acrusher=bits=8:mode=log:aa=1:mix=0.7,acompressor=threshold=-20dB:ratio=6:attack=4:release=90:makeup=4")
PS1_POST = "scale=%d:%d:flags=neighbor,lutrgb=r='trunc(val/8)*8':g='trunc(val/8)*8':b='trunc(val/8)*8',format=yuv420p" % (W, H)
_W = re.compile(r"[^a-z0-9']+")


def _run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:220])
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def _norm(w: str) -> str:
    return _W.sub("", w.lower())


def frames_for(t0: float, t1: float) -> int:
    return max(1, round(t1 * FPS) - round(t0 * FPS))


def cut_times(script: dict) -> list[dict]:
    """Shot start times from cut_on words, using the same per-word timing the captions use."""
    cues = moviecaptions.word_cues(script)          # in narration order, each {text, start_s, end_s}
    # map every cue to its beat by time
    beat_span = [(b["start_s"], b["end_s"]) for b in script["beats"]]
    shots = []
    for i, sh in enumerate(script["shots"]):
        if i == 0:
            shots.append({**sh, "t0": 0.0})
            continue
        b0, b1 = beat_span[sh["beat"] - 1]
        want = _norm(sh["cut_on"])
        hit = next((c for c in cues if b0 - 1e-3 <= c["start_s"] <= b1 + 1e-3 and _norm(c["text"]) == want), None)
        if hit is None:
            raise SystemExit(f"{sh['id']}: cut_on {sh['cut_on']!r} not found in beat {sh['beat']}")
        shots.append({**sh, "t0": round(hit["start_s"], 3)})
    shots.sort(key=lambda s: s["t0"])
    t_end = round(script["runtime_s"] + TAIL_S, 3)
    for i, s in enumerate(shots):
        s["t1"] = shots[i + 1]["t0"] if i + 1 < len(shots) else t_end
        s["frames"] = frames_for(s["t0"], s["t1"])
    return shots


def narrate_cmd() -> dict:
    script = json.loads((MVP / "script.json").read_text())
    audio = MVP / "audio" / "raw"
    shutil.rmtree(audio, ignore_errors=True)
    texts = [s["text"] for b in script["beats"] for s in b["sentences"]]
    lines = tts.synth_lines(texts, audio, speed=SPEED, speeds=[SPEED] * len(texts))
    for k, v in GAPS.items():
        setattr(narrate, k, v)
    script = narrate.apply_measured(script, [ln.duration_s for ln in lines])
    lofi = MVP / "audio" / "lofi"
    shutil.rmtree(lofi, ignore_errors=True)
    lofi.mkdir(parents=True)
    for ln in lines:
        _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", ln.path, "-af", LOFI,
              "-ar", SR, "-ac", 1, "-c:a", "pcm_s16le", lofi / ln.path.name])
    script["audio_dir"] = str(lofi)
    script["narration_mode"] = "sentence"
    shots = cut_times(script)
    plan = {"fps": FPS, "width": W, "height": H, "runtime_s": script["runtime_s"], "video_s": round(script["runtime_s"] + TAIL_S, 3),
            "total_frames": sum(s["frames"] for s in shots), "speed": SPEED, "shots": shots}
    (MVP / "script.timed.json").write_text(json.dumps(script, indent=1))
    (MVP / "render_plan.json").write_text(json.dumps(plan, indent=1))
    words = sum(len(t.split()) for t in texts)
    print(f"  {words} words, speech {sum(l.duration_s for l in lines):.1f}s, runtime {script['runtime_s']:.2f}s "
          f"({words / script['runtime_s'] * 60:.0f} wpm incl. gaps), video {plan['video_s']:.2f}s, {plan['total_frames']} frames")
    for s in shots:
        print(f"  {s['id']:8} {s['t0']:6.2f} -> {s['t1']:6.2f} {s['frames']:4d}f  cut on {s.get('cut_on', '-')!r}")
    return plan


def render_cmds() -> Path:
    plan = json.loads((MVP / "render_plan.json").read_text())
    lines = ["#!/bin/bash", "# v2 PS1 render, all shots, flock-serialised; run under systemd-run --user", "set -u",
             "cd /home/apollo/blender-spike", 'echo "RENDER_START $(date -u +%FT%TZ)"', "export MVP_PS1=1 MVP_SETS=1"]
    for s in plan["shots"]:
        out = MVP / "renders" / s["id"]
        lines.append(f"flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- "
                     f"{MVP}/shots/{s['id']}.py anim {out} {s['frames']} 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2")
    lines.append('echo "RENDER_DONE $(date -u +%FT%TZ)"')
    sh = MVP / "render_all.sh"
    sh.write_text("\n".join(lines) + "\n")
    sh.chmod(0o755)
    return sh


def bed() -> tuple[Path, Path]:
    plan = json.loads((MVP / "render_plan.json").read_text())
    work = MVP / "work"
    work.mkdir(exist_ok=True)
    parts, durs = [], []
    for s in plan["shots"]:
        d = MVP / "renders" / s["id"]
        have = sorted(d.glob("f_*.png"))
        if len(have) < s["frames"]:
            raise SystemExit(f"{s['id']}: {len(have)} of {s['frames']} frames rendered")
        v = work / f"{s['id']}.mp4"
        _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-framerate", FPS, "-start_number", 1,
              "-i", d / "f_%04d.png", "-frames:v", s["frames"], "-vf", PS1_POST, *LR.ENCODE, *LR.MP4_TIMING, "-an", v])
        parts.append(v)
        durs.append(s["frames"] / FPS)
    lst = work / "list_v.txt"
    lst.write_text(LR.concat_list(parts, durs))
    bed_v = work / "bed.mp4"
    _run(LR.concat_cmd(lst, bed_v))
    bed_a = work / "bed.wav"
    _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", f"anoisesrc=c=brown:r={SR}:a=0.6:s=7",
          "-t", f"{plan['video_s'] + 1:.3f}", "-af",
          f"lowpass=f=260,highpass=f=40,tremolo=f=0.11:d=0.35,loudnorm=I={WIND_LUFS}:TP=-6:LRA=7,aformat=channel_layouts=stereo",
          "-c:a", "pcm_s16le", "-ar", SR, "-ac", 2, bed_a])
    return bed_v, bed_a


def captions() -> Path:
    script = json.loads((MVP / "script.timed.json").read_text())
    out = MVP / "captions" / "captions.ass"
    out.parent.mkdir(exist_ok=True)
    moviecaptions.write_ass(script, out, style="pop")
    return out


def mux(bed_v: Path, bed_a: Path, ass: Path) -> Path:
    script = json.loads((MVP / "script.timed.json").read_text())
    vo = [(Path(script["audio_dir"]) / s["audio"], int(round(s["start_s"] * 1000))) for b in script["beats"] for s in b["sentences"]]
    out = MVP / "final" / f"{script.get('slug', 'mvp2')}.mp4"
    out.parent.mkdir(exist_ok=True)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", bed_v, "-i", bed_a]
    for p, _ in vo:
        cmd += ["-i", p]
    graph = f"[0:v]ass={ass}[v];" + LR.mix_graph([d for _, d in vo]).replace(
        "aresample=48000[out]", "aresample=48000,aformat=channel_layouts=stereo[out]")
    cmd += ["-filter_complex", graph, "-map", "[v]", "-map", "[out]", *LR.ENCODE, "-c:a", "aac", "-b:a", "160k",
            *LR.MP4_TIMING, "-movflags", "+faststart", out]
    _run(cmd)
    return out


def qc(mp4: Path) -> dict:
    probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(mp4)],
                                      capture_output=True, text=True, check=True).stdout)
    v = next(s for s in probe["streams"] if s["codec_type"] == "video")
    a = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)
    frames = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                 "stream=nb_read_frames", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True, check=True).stdout.strip() or 0)
    loud = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    il = [ln for ln in loud.splitlines() if "I:" in ln and "LUFS" in ln]
    plan = json.loads((MVP / "render_plan.json").read_text()) if (MVP / "render_plan.json").exists() else {}
    rep = {"file": str(mp4), "size_mb": round(mp4.stat().st_size / 1e6, 1), "width": v["width"], "height": v["height"],
           "fps": v["r_frame_rate"], "duration_s": round(float(probe["format"]["duration"]), 3), "frames": frames,
           "audio": bool(a), "audio_channels": a and a.get("channels"), "integrated_lufs": il[-1].strip() if il else None,
           "expected_frames": plan.get("total_frames")}
    rep["ok"] = (rep["width"], rep["height"]) == (W, H) and rep["audio"] and rep["audio_channels"] == 2 and \
        (rep["expected_frames"] is None or abs(frames - rep["expected_frames"]) <= 1)
    print(json.dumps(rep, indent=1))
    return rep


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "narrate":
        narrate_cmd()
    elif cmd == "render-cmds":
        print(render_cmds())
    elif cmd == "post":
        bv, ba = bed()
        return 0 if qc(mux(bv, ba, captions()))["ok"] else 2
    elif cmd == "qc":
        return 0 if qc(Path(sys.argv[2]))["ok"] else 2
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
