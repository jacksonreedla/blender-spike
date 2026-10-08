# --- PS1 pass: exec'd by the runner after the shot when MVP_PS1=1 ---------------------------
# Low internal resolution with hard pixels, every mesh decimated to a small budget and flat
# shaded, every texture shrunk and sampled without filtering. The dither/quantise step is ffmpeg.
PS1_W, PS1_H = 320, 569
PS1_SAMPLES = int(os.environ.get("MVP_PS1_SAMPLES", "6"))
PS1_TEX = int(os.environ.get("MVP_PS1_TEX", "64"))
PS1_TRIS = int(os.environ.get("MVP_PS1_TRIS", "900"))


def ps1_pass(sc):
    sc.render.resolution_x, sc.render.resolution_y = PS1_W, PS1_H
    sc.render.resolution_percentage = 100
    sc.eevee.taa_render_samples = PS1_SAMPLES
    sc.render.filter_size = 0.0                       # no pixel filter: crisp texels
    sc.view_settings.view_transform = "Standard"      # PS1 had no filmic curve
    sc.view_settings.look = "None"
    sc.eevee.volumetric_tile_size = "16"
    sc.eevee.volumetric_samples = 24
    done_img = set()
    for o in list(sc.objects):
        if o.type != "MESH" or not o.data.polygons:
            continue
        n = len(o.data.polygons)
        budget = 4000 if n > 60000 else PS1_TRIS
        if n > budget * 1.2:
            m = o.modifiers.new("ps1_decimate", "DECIMATE")
            m.ratio = budget / n
            m.use_collapse_triangulate = True
        for p in o.data.polygons:
            p.use_smooth = False
        for slot in o.material_slots:
            mat = slot.material
            if not mat or not mat.use_nodes:
                continue
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    node.interpolation = "Closest"
                    img = node.image
                    lim = 128 if img.name.startswith("T_") else PS1_TEX      # faces keep 128 px, the set 64
                    if img.name not in done_img and img.size[0] > lim:
                        img.scale(lim, lim)
                        done_img.add(img.name)
                elif node.type == "BSDF_PRINCIPLED":
                    node.inputs["Specular IOR Level"].default_value = 0.15
    return sc
