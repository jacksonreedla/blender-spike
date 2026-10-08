# --- the reusable cast: Quaternius Universal Base Characters (CC0) dressed by vertex group --------
# exec'd by the runner after sets.py when MVP_SETS=1. Same rig as the animation library, so
# character() machinery (clips, travel, phase, freeze, path guard, hold()) works unchanged.
UBC = ("/home/apollo/blender-spike/assets/characters/quaternius-universal-base-characters/"
       "Universal Base Characters[Standard]")
BODY_GLTF = {"male": UBC + "/Base Characters/Godot - UE/Superhero_Male_FullBody.gltf",
             "female": UBC + "/Base Characters/Godot - UE/Superhero_Female_FullBody.gltf"}
HAIR_DIR = UBC + "/Hairstyles/Rigged to Head Bone/glTF (Godot -Unreal)/"
COAT_GROUPS = ("spine", "clavicle", "upperarm", "lowerarm")
TROUSER_GROUPS = ("pelvis", "thigh", "calf")
BOOT_GROUPS = ("foot", "ball")

LOOKS = {   # name: coat, trousers, boots, hair, beard, skin tint
    "robber":    dict(coat=(0.20, 0.12, 0.06), trousers=(0.10, 0.09, 0.08), boots=(0.08, 0.06, 0.05), hair="Hair_Buzzed", beard=True, hair_color=(0.12, 0.08, 0.05)),
    "robber2":   dict(coat=(0.26, 0.26, 0.24), trousers=(0.12, 0.10, 0.09), boots=(0.08, 0.06, 0.05), hair="Hair_SimpleParted", beard=False, hair_color=(0.30, 0.18, 0.08)),
    "watchman":  dict(coat=(0.14, 0.20, 0.45), trousers=(0.14, 0.13, 0.12), boots=(0.06, 0.06, 0.06), hair="Hair_Long", beard=True, hair_color=(0.10, 0.07, 0.05)),
    "anatomist": dict(coat=(0.08, 0.08, 0.09), trousers=(0.08, 0.08, 0.09), boots=(0.05, 0.05, 0.05), hair="Hair_SimpleParted", beard=False, hair_color=(0.35, 0.30, 0.25)),
    "official":  dict(coat=(0.40, 0.36, 0.28), trousers=(0.18, 0.15, 0.12), boots=(0.06, 0.06, 0.06), hair="Hair_Buzzed", beard=False, hair_color=(0.45, 0.42, 0.38)),
    "corpse":    dict(coat=(0.66, 0.64, 0.58), trousers=(0.66, 0.64, 0.58), boots=(0.55, 0.52, 0.45), hair="Hair_Buzzed", beard=False, pale=True, hair_color=(0.2, 0.15, 0.1)),
}


def _cloth(name, color, weave=0.35):
    m = material(name, color, rough=0.95)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 120.0
    noise.inputs["Detail"].default_value = 3.0
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["Factor"].default_value = weave
    mix.inputs[6].default_value = (*color, 1.0)
    mix.inputs[7].default_value = (color[0] * 0.55, color[1] * 0.55, color[2] * 0.55, 1.0)
    nt.links.new(noise.outputs["Fac"], mix.inputs["Factor"])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    return m


SKIN_GROUPS = ("Head", "neck", "hand", "index", "middle", "ring", "pinky", "thumb")


def _weights(m, groups):
    """Per-vertex summed weight of every group whose name starts with one of `groups` (twist bones included)."""
    gi = {g.index for g in m.vertex_groups if g.name.startswith(groups)}
    return [sum(g.weight for g in v.groups if g.group in gi) for v in m.data.vertices]


def dress(meshes, look):
    coat = _cloth(f"Coat_{len(bpy.data.materials)}", look["coat"])
    trou = _cloth(f"Trousers_{len(bpy.data.materials)}", look["trousers"], 0.25)
    boot = material(f"Boots_{len(bpy.data.materials)}", look["boots"], rough=0.6)
    hairm = material(f"Hair_{len(bpy.data.materials)}", look.get("hair_color", (0.12, 0.08, 0.05)), rough=0.8)
    for m in meshes:
        if m.name.startswith(("Eyebrows", "Hair")):
            m.data.materials.clear()
            m.data.materials.append(hairm)
            continue
        if m.name.startswith("Eyes"):
            continue
        skin = m.material_slots[0].material if m.material_slots and m.material_slots[0].material else material("Skin", (0.62, 0.42, 0.30))
        if look.get("pale") and skin.use_nodes:
            b = skin.node_tree.nodes.get("Principled BSDF")
            link = next((l for l in skin.node_tree.links if b and l.to_socket is b.inputs["Base Color"]), None)
            if link:
                hs = skin.node_tree.nodes.new("ShaderNodeHueSaturation")
                hs.inputs["Saturation"].default_value = 0.35
                hs.inputs["Value"].default_value = 1.15
                src = link.from_socket
                skin.node_tree.links.remove(link)
                skin.node_tree.links.new(src, hs.inputs["Color"])
                skin.node_tree.links.new(hs.outputs["Color"], b.inputs["Base Color"])
        m.data.materials.clear()
        for mat in (skin, coat, trou, boot):
            m.data.materials.append(mat)
        ws, wc, wt, wb = _weights(m, SKIN_GROUPS), _weights(m, COAT_GROUPS), _weights(m, TROUSER_GROUPS), _weights(m, BOOT_GROUPS)
        for p in m.data.polygons:
            n = len(p.vertices)
            cls = max((sum(ws[i] for i in p.vertices) / n, 0), (sum(wc[i] for i in p.vertices) / n, 1),
                      (sum(wt[i] for i in p.vertices) / n, 2), (sum(wb[i] for i in p.vertices) / n, 3))
            p.material_index = cls[1]


def _attach_hair(arm, name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=HAIR_DIR + name + ".gltf")
    new = [o for o in bpy.data.objects if o not in before]
    keep = [o for o in new if o.type == "MESH" and any(md.type == "ARMATURE" for md in o.modifiers)]
    drop = [o for o in new if o not in keep]
    for o in keep:
        for md in o.modifiers:
            if md.type == "ARMATURE":
                md.object = arm
        o.parent = arm
    for o in drop:
        bpy.data.objects.remove(o, do_unlink=True)
    return keep


def _import_body(sex, look):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=BODY_GLTF[sex])
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == "ARMATURE")
    meshes = [o for o in new if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers)
              and not o.name.startswith("Eyebrows")]
    drop = [o for o in new if o.type == "MESH" and o not in meshes]
    for o in drop:
        bpy.data.objects.remove(o, do_unlink=True)
    if "Walk_Loop" not in bpy.data.actions:                                 # the clips live in the animation library glb
        b2 = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=CHAR_GLB)
        for o in [o for o in bpy.data.objects if o not in b2]:
            bpy.data.objects.remove(o, do_unlink=True)
    meshes += _attach_hair(arm, look["hair"]) + _attach_hair(arm, "Eyebrows_Regular")
    if look.get("beard"):
        meshes += _attach_hair(arm, "Hair_Beard")
    dress(meshes, look)
    return arm, meshes


def person(look="robber", clip="Idle_Loop", at=(0.0, 0.0), facing_deg=180.0, travel=None, phase=0, freeze_at=None,
           sex="male", scale=1.0):
    """A dressed, textured cast member on the shared rig. Same contract as character()."""
    lk = LOOKS[look]
    arm, meshes = _import_body(sex, lk)
    return _rig_setup(arm, meshes, clip, at, facing_deg, travel, phase, freeze_at, scale)
