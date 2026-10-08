# --- v2 set builders, exec'd by the runner after helpers.py when MVP_SETS=1 ------------------
# A shot = one set + optional dressing + a character + a camera. Everything here was judged as
# stills in v1 (mvp/stills/*_b*.png); the PS1 pass handles decimation and texel size.
import random as _random


def night(world_strength=0.26, fog=0.014, aniso=0.6, color=(0.006, 0.009, 0.020)):
    world(color=color, strength=world_strength, fog=fog, anisotropy=aniso)


def key_cold(location, at, energy=2400, spot_deg=36, size=0.15):
    return light("SPOT", location, at, energy, size=size, color=(0.62, 0.76, 1.0), spot_size=math.radians(spot_deg))


def fill_cold(location, at, energy=90, size=3.0):
    return light("AREA", location, at, energy, size=size, color=(0.58, 0.70, 1.0))


def mud_ground(scale=2.4, wet=0.22, value=0.30):
    g = ground(size=200, texture="brown_mud_dry", scale=scale, wet=wet)
    shade(g.data.materials[0], value, 0.65)
    return g


def cobble_ground(scale=2.4, wet=0.8):
    return ground(size=300, texture="cobblestone_03", scale=scale, wet=wet)


def headstones(n=7, seed=3, cx=0.0, cy=5.5, spread=(3.2, 2.6), avoid=None, value=0.42):
    """Scatter n rough headstones around (cx, cy); avoid = (x, y, r) keeps a clear plot."""
    r = _random.Random(seed)
    out = []
    while len(out) < n:
        x, y = cx + r.uniform(-spread[0], spread[0]), cy + r.uniform(-spread[1], spread[1])
        if avoid and math.hypot(x - avoid[0], y - avoid[1]) < avoid[2]:
            continue
        size = (r.uniform(0.5, 0.66), 0.14, r.uniform(0.66, 0.95))
        out.append(shade(headstone((x, y), rot_deg=r.uniform(-25, 25), size=size, tilt_deg=r.uniform(-8, 8)).data.materials[0], value, 0.5))
    return out


def churchyard(seed=3, lamp_at=(-2.4, 9.0), lamp_toward=(0.0, 5.0), statue_at=(2.4, 7.9), wall_y=11.0, avoid=(0, 0.6, 2.2)):
    """Mud churchyard: stones, a chest tomb, rock masses and a lamp behind, statue as a far shape."""
    mud_ground()
    headstones(seed=seed, avoid=avoid)
    shade(tbox((1.7, 0.85, 0.6), (-2.9, 3.2), texture="aerial_rocks_02", tiles=1.4, rot_deg=10, name="Tomb").data.materials[0], 0.4, 0.5)
    if statue_at:
        place("gothic_statue", at=statue_at, rot_deg=160)
    place("rock_face_01", at=(-4.2, wall_y - 0.5), rot_deg=30)
    place("rock_face_02", at=(4.6, wall_y - 1.5), rot_deg=-40)
    place("namaqualand_boulder_02", at=(-3.4, wall_y - 2.8), rot_deg=25)
    place("dead_tree_trunk", at=(2.9, 4.6), rot_deg=80)
    if lamp_at:
        lamp(at=lamp_at, toward=lamp_toward, energy=700, color=(1.0, 0.64, 0.32))


def gate_set():
    """The v1 hook shot: closed iron gate on wet cobbles, churchyard through the bars."""
    cobble_ground()
    place("large_iron_gate", at=(0.0, 0.0))
    tbox((6.0, 0.60, 0.09), (0.0, 0.05), texture="asphalt_03", tiles=3.0, wet=0.6, name="Threshold")
    headstones(n=9, seed=7, cx=0.3, cy=4.2, spread=(3.0, 2.4), value=0.4)
    shade(tbox((16.0, 0.45, 1.25), (-0.8, 8.6), texture="cobblestone_03", tiles=6.0, rot_deg=7, name="Wall").data.materials[0], 0.22, 0.6)
    place("gothic_statue", at=(2.75, 8.9), rot_deg=40)
    place("rock_face_01", at=(-5.2, 11.5), rot_deg=25)
    place("rock_face_02", at=(5.4, 10.8), rot_deg=-35)
    lamp(at=(-2.15, 2.85), toward=(0.0, -0.30), energy=560, color=(1.0, 0.63, 0.30))
    light("SPOT", (-2.00, 2.60, 3.05), (0.55, 0.15, 0.50), 1600, size=0.35, color=(1.0, 0.66, 0.34), spot_size=math.radians(44))
    light("SPOT", (3.10, 3.20, 2.40), (-0.50, -1.00, 0.10), 2000, size=0.25, color=(0.72, 0.82, 1.0), spot_size=math.radians(30))
    light("AREA", (2.60, -3.60, 1.70), (0.0, 0.0, 1.30), 150, size=3.0, color=(0.58, 0.70, 1.0))


def fresh_grave(at=(0.0, 0.55), rot_deg=4):
    m = mound(at, size=(0.66, 1.15, 0.30), rot_deg=rot_deg, tiles=0.9, wet=0.25)
    shade(m.data.materials[0], 0.24, 0.8)
    m.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.85
    head = place("rock_face_02", at=(at[0], at[1] + 1.3), rot_deg=0, scale=0.30)
    for d, r, s in (((0.72, -0.9), 20, 1.6), ((-0.66, -0.4), -50, 1.3), ((0.58, 0.5), 65, 1.2)):
        place("moon_rock_01", at=(at[0] + d[0], at[1] + d[1]), rot_deg=r, scale=s)
    return m, head


def open_grave(at=(0.0, 0.0), rot_deg=0.0, length=2.0, width=0.9, depth=0.6):
    """A dug pit with a spoil heap at its head: a displaced grid patch dropped into the ground."""
    ax, ay = at
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    PATCH, N = 10.0, 120
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=N, y_subdivisions=N, size=PATCH, location=(ax, ay, 0.02))
    o = bpy.context.object
    me = o.data
    hl, hw = length / 2, width / 2
    for v in me.vertices:
        x, y = v.co.x, v.co.y
        u, w = c * x + s * y, -s * x + c * y            # pit-local
        z = 0.02 * math.sin(1.3 * x) * math.cos(1.1 * y) + 0.012 * math.sin(3.1 * y) * math.cos(2.7 * x)
        r = max(abs(u) / hl, abs(w) / hw)
        if r < 1.15:
            t = min(1.0, (1.15 - r) / 0.15)
            z -= depth * (t * t * (3 - 2 * t))
        md = ((u) / (hl * 0.55)) ** 2 + ((w - hw - 0.55) / 0.5) ** 2      # spoil heaped beside the far long edge
        if md < 1.0:
            z += 0.32 * (1 - md) ** 1.2
        edge = max(abs(x), abs(y)) / (PATCH / 2)
        if edge > 0.8:
            k = min(1.0, (edge - 0.8) / 0.2)
            z = z * (1 - k) - 0.15 * k
        v.co.z = z
    for p in me.polygons:
        p.use_smooth = False
    mat = pbr_material("Dug", "brown_mud_dry", 7.0, wet=0.4)
    shade(mat, 0.18, 0.85)
    me.materials.append(mat)
    slab = tbox((1.7, 0.8, 0.18), (ax + c * 0.3 - s * 1.6, ay + s * 0.3 + c * 1.6), texture="aerial_rocks_02", tiles=1.4,
                rot_deg=rot_deg + 28, tilt_deg=-9, z=0.1, name="Slab")
    shade(slab.data.materials[0], 0.5, 0.5)
    return o, slab


def mortsafe(at=(0.0, 0.0), rot_deg=-15.0, hu=1.10, hv=0.50, top=1.0):
    """The v1 cage: uprights on four sides, three rails, a top grid, a padlock, over a slab."""
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))

    def Wp(u, v, z=0.0):
        return (at[0] + c * u - s * v, at[1] + s * u + c * v, z)

    slab = tbox((2.0, 0.9, 0.16), at, texture="aerial_rocks_02", tiles=1.4, rot_deg=rot_deg + 3, z=0.02, name="Slab")
    shade(slab.data.materials[0], 0.5, 0.5)
    for i in range(19):
        u = -hu + i * (2 * hu / 18)
        for v in (-hv, hv):
            ibar(Wp(u, v, -0.08), Wp(u, v, top + 0.02), 0.031 if i in (0, 18) else 0.019)
    for u in (-hu, hu):
        for j in range(1, 8):
            ibar(Wp(u, -hv + j * 0.125, -0.08), Wp(u, -hv + j * 0.125, top + 0.02), 0.019)
    for z in (0.10, 0.58, top):
        for v in (-hv, hv):
            ibar(Wp(-hu, v, z), Wp(hu, v, z), 0.021)
        for u in (-hu, hu):
            ibar(Wp(u, -hv, z), Wp(u, hv, z), 0.021)
    for v in (-0.375, -0.125, 0.125, 0.375):
        ibar(Wp(-hu, v, top), Wp(hu, v, top), 0.017)
    for k in range(1, 8):
        ibar(Wp(-hu + k * 0.275, -hv, top), Wp(-hu + k * 0.275, hv, top), 0.017)
    lx, ly, _ = Wp(0.06, -0.55)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, ly, 0.55))
    lock = bpy.context.object
    lock.scale, lock.rotation_euler = (0.13, 0.07, 0.17), (0, 0, math.radians(rot_deg))
    lock.data.materials.append(material("Lock", (0.21, 0.20, 0.18), rough=0.26, metal=1.0))
    return slab


# --- the body model: Quaternius Universal Animation Library (CC0), one rig, 43 clips -------------
CHAR_GLB = ("/home/apollo/blender-spike/assets/characters/quaternius-universal-animation-library/"
            "Universal Animation Library[Standard]/Unreal-Godot/UAL1_Standard.glb")   # clips play IN PLACE
CLIP_SPEED = {"Walk_Loop": 0.97, "Walk_Formal_Loop": 0.9, "Jog_Fwd_Loop": 2.4, "Sprint_Loop": 4.5, "Crouch_Fwd_Loop": 0.6}


def character(clip="Idle_Loop", at=(0.0, 0.0), facing_deg=180.0, travel=None, phase=0, cloth=(0.30, 0.21, 0.13),
              skin=None, scale=1.0, freeze_at=None):
    """The plain mannequin (colour by vertex group), on the shared rig. See _rig_setup for the contract."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=CHAR_GLB)
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == "ARMATURE")
    meshes = [o for o in new if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers)]
    for o in [o for o in new if o.type == "MESH" and o not in meshes]:
        bpy.data.objects.remove(o, do_unlink=True)
    coat = material(f"Cloth_{len(bpy.data.materials)}", cloth, rough=0.92)
    skinm = material(f"Skin_{len(bpy.data.materials)}", skin or (0.62, 0.42, 0.30), rough=0.85)
    SKIN_GROUPS = ("Head", "neck_01", "hand_l", "hand_r")
    for m in meshes:
        m.data.materials.clear()
        m.data.materials.append(coat)
        m.data.materials.append(skinm)
        gi = {g.index for g in m.vertex_groups if g.name in SKIN_GROUPS or g.name.startswith(("index", "middle", "ring", "pinky", "thumb"))}
        wt = [sum(g.weight for g in v.groups if g.group in gi) for v in m.data.vertices]
        for poly in m.data.polygons:
            if sum(wt[i] for i in poly.vertices) / len(poly.vertices) > 0.5:
                poly.material_index = 1
    return _rig_setup(arm, meshes, clip, at, facing_deg, travel, phase, freeze_at, scale)


def _rig_setup(arm, meshes, clip, at, facing_deg, travel, phase, freeze_at, scale):
    """Play `clip` (looped for any shot length, or one pose held with freeze_at), stand the rig at
    `at` facing `facing_deg` (0 = +Y away from a camera on -Y; 180 = toward it), feet on z=0.
    `travel` = m/s along the facing (default: the clip's natural speed for locomotion clips, else 0);
    the parent empty is keyframed across the shot. Refuses a path through set geometry."""
    act = bpy.data.actions[clip]
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act
    if getattr(arm.animation_data, "action_slot", None) is None and act.slots:
        arm.animation_data.action_slot = act.slots[0]
    if freeze_at is not None:
        for fc in act.fcurves:
            kps = fc.keyframe_points
            for i in range(len(kps) - 1, -1, -1):
                if abs(kps[i].co.x - freeze_at) > 0.5:
                    kps.remove(kps[i])
            fc.extrapolation = "CONSTANT"
    else:
        for fc in act.fcurves:
            if not any(m.type == "CYCLES" for m in fc.modifiers):
                fc.modifiers.new("CYCLES")
    if phase and freeze_at is None:
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.co.x += phase
                kp.handle_left.x += phase
                kp.handle_right.x += phase
    root = _link(bpy.data.objects.new("char_root", None))
    top = arm.parent or arm
    top.parent = root
    top.rotation_euler = (top.rotation_euler.x, top.rotation_euler.y, top.rotation_euler.z + math.pi)  # rig rests facing -Y
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    lo = None
    for m in meshes:
        ev = m.evaluated_get(dg)
        me = ev.to_mesh()
        for v in me.vertices:
            z = (ev.matrix_world @ v.co).z
            lo = z if lo is None else min(lo, z)
        ev.to_mesh_clear()
    top.location.z -= lo or 0.0
    root.scale = (scale, scale, scale)
    root.rotation_euler = (0, 0, math.radians(facing_deg))
    root.location = (at[0], at[1], 0.0)
    v = CLIP_SPEED.get(clip, 0.0) if travel is None else travel
    dx, dy = -math.sin(math.radians(facing_deg)), math.cos(math.radians(facing_deg))
    fr = bpy.context.scene.render.fps
    n = int(globals().get("SHOT_FRAMES", 48))
    if v:
        root.keyframe_insert("location", frame=1)
        root.location = (at[0] + dx * v * n / fr, at[1] + dy * v * n / fr, 0.0)
        root.keyframe_insert("location", frame=n)
        root.location = (at[0], at[1], 0.0)
        for fc in root.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    _path_check(root, meshes, at, (at[0] + (dx * v * n / fr if v else 0), at[1] + (dy * v * n / fr if v else 0)))
    return root


def _path_check(root, own, p0, p1):
    """Refuse a character whose standing spot or travel path runs through set geometry."""
    for m in own:
        m.hide_viewport = True
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    try:
        probes = [(Vector((p0[0], p0[1], 0.9)), Vector((0, 0, 0.6)))]          # torso at the standing spot
        if (p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2 > 1e-4:
            for z in (0.45, 1.2):                                              # the travel path
                a, b = Vector((p0[0], p0[1], z)), Vector((p1[0], p1[1], z))
                probes.append((a, b - a))
        if True:
            for probe in probes:
                o, d = probe
                if d.length < 1e-6:
                    continue
                hit, loc, nrm, idx, obj, mw = sc.ray_cast(dg, o, d.normalized(), distance=d.length)
                if hit and not obj.name.startswith(("Plane", "Grid")):
                    raise RuntimeError(f"PATH BLOCKED: character at {p0} -> {p1} runs into '{obj.name}' at "
                                       f"({loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f}). Move the character or the prop.")
    finally:
        for m in own:
            m.hide_viewport = False


# --- props in hands + set pieces the words need --------------------------------------------------
def _arm_of(root):
    return next(o for o in root.children_recursive if o.type == "ARMATURE")


def hold(root, obj, bone="hand_r", offset=(0.0, 0.0, 0.0), rot_deg=(0.0, 0.0, 0.0)):
    """Parent a prop to a hand bone of a character() root. offset/rot are in the bone's space
    (origin = bone tail: +Y along the fingers)."""
    arm = _arm_of(root)
    obj.parent = arm
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    obj.location = offset
    obj.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    return obj


def prop_purse(r=0.07, color=(0.25, 0.16, 0.08)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=12, ring_count=8)
    o = bpy.context.object
    o.scale = (1.0, 1.0, 1.25)
    o.data.materials.append(material("Purse", color, rough=0.9))
    return o


def prop_shovel(length=1.25):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=length, location=(0, 0, 0))
    shaft = bpy.context.object
    shaft.data.materials.append(material("Shaft", (0.22, 0.14, 0.07), rough=0.9))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -length / 2 - 0.12))
    blade = bpy.context.object
    blade.scale = (0.2, 0.02, 0.26)
    blade.data.materials.append(iron())
    blade.parent = shaft
    return shaft


def prop_lantern(root, bone="hand_r", energy=140, color=(1.0, 0.72, 0.4)):
    """A small lit lantern in the hand: brass body + a POINT light riding with it."""
    before = set(bpy.data.objects)
    place("brass_diya_lantern", at=(0, 0), scale=1.4)
    lroot = next(o for o in bpy.data.objects if o not in before and "_root" in o.name)
    hold(root, lroot, bone, offset=(0.0, 0.06, -0.25), rot_deg=(0, 0, 0))
    ld = bpy.data.lights.new("HandLamp", "POINT")
    ld.energy, ld.color, ld.shadow_soft_size = energy, color, 0.08
    lo = _link(bpy.data.objects.new("HandLamp", ld))
    lo.parent = lroot
    lo.location = (0, 0, 0.3)
    return lroot


def coins(at, n=9, seed=2, color=(0.95, 0.75, 0.25), z=0.0):
    r = _random.Random(seed)
    out = []
    for i in range(n):
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.045, depth=0.006,
                                            location=(at[0] + r.uniform(-0.18, 0.18), at[1] + r.uniform(-0.12, 0.12), z + 0.002 + 0.004 * (i % 3)))
        o = bpy.context.object
        o.data.materials.append(material("Coin", color, rough=0.35, metal=1.0))
        out.append(o)
    return out


def gallows(at=(0.0, 0.0), rot_deg=0.0, height=4.2, span=2.2):
    """Two uprights, a crossbeam, a rope; returns the point (x, y, z) the noose hangs from."""
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    for u in (-span / 2, span / 2):
        p = (at[0] + c * u, at[1] + s * u)
        shade(tbox((0.22, 0.22, height), p, texture="aerial_rocks_02", tiles=1.0, rot_deg=rot_deg, name="Post").data.materials[0], 0.25, 0.4)
    beam = shade(tbox((span + 0.5, 0.2, 0.22), at, texture="aerial_rocks_02", tiles=1.0, rot_deg=rot_deg, z=height - 0.22, name="Beam").data.materials[0], 0.25, 0.4)
    top = (at[0], at[1], height - 0.25)
    ibar(top, (at[0], at[1], top[2] - 0.7), r=0.02, mat=material("Rope", (0.45, 0.38, 0.25), rough=0.95))
    return (at[0], at[1], top[2] - 0.7)


def hanged(at, rot_deg, drop=0.9, facing_deg=180):
    """A still figure hanging from gallows(); the root is lifted so the head sits under the rope."""
    root = character("Idle_Loop", at=at[:2], facing_deg=facing_deg, travel=0, freeze_at=10, cloth=(0.5, 0.48, 0.42))
    root.location.z = at[2] - 1.52        # neck under the rope end
    return root
