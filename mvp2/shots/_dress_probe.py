sc = reset(); night(); mud_ground()
r = person("robber", "Walk_Loop", at=(0, 0), facing_deg=180, travel=0)
a = person("anatomist", "Fixing_Kneeling", at=(1.5, 0), facing_deg=180)
import collections
for root in (r, a):
    for m in root.children_recursive:
        if m.type == "MESH" and m.name.startswith("SuperHero"):
            c = collections.Counter(p.material_index for p in m.data.polygons)
            print("PROBE", m.name, dict(c), [ms.material.name for ms in m.material_slots], "groups:", len(m.vertex_groups), [g.name for g in m.vertex_groups][:6])
CAM_START = (0, -4, 1.2); CAM_END = (0, -3.9, 1.2); CAM_AT = (0.5, 0, 0.9); LENS = 35
