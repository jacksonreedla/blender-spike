"""Measure every model in assets/models/ and write manifest.json.

Runs INSIDE Blender. For each .gltf: import, take the world-space bounding box
across all imported meshes, record its size and where its base sits. The LLM
cannot be trusted to know that a chair is 0.9 m tall or that an imported
model's origin is nowhere near its feet - so the manifest tells it, and the
place() helper uses the base offset to rest things on the ground by
construction rather than by hope.

    blender -b -P scenes/measure.py
"""
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path("/home/apollo/blender-spike/assets/models")
OUT = ROOT / "manifest.json"


def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH"
           for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


manifest = {}
for gltf in sorted(ROOT.glob("*/*.gltf")):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(gltf))
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    if not meshes:
        print(f"  SKIP {gltf.parent.name}: no meshes")
        continue
    lo, hi = bbox(meshes)
    size = hi - lo
    manifest[gltf.parent.name] = {
        "path": str(gltf),
        "size_m": [round(size.x, 3), round(size.y, 3), round(size.z, 3)],
        "base_z": round(lo.z, 4),            # world z of the lowest point at import
        "centre_xy": [round((lo.x + hi.x) / 2, 3), round((lo.y + hi.y) / 2, 3)],
        "mesh_count": len(meshes),
        "tris": sum(len(o.data.polygons) for o in meshes),
    }
    print(f"  {gltf.parent.name}: {size.x:.2f} x {size.y:.2f} x {size.z:.2f} m, "
          f"base_z={lo.z:+.3f}, {len(meshes)} mesh(es)")

OUT.write_text(json.dumps(manifest, indent=1))
print(f"wrote {OUT} ({len(manifest)} models)")
