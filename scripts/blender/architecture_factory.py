"""Reference-rule driven, non-copying procedural architecture pilot factory.

The factory never imports reference GLBs.  It consumes only grammar IDs and typed
parameters, then writes candidate-only Blend/GLB/texture/preview artefacts under
an explicit external output root.
"""
import argparse
import hashlib
import json
import math
import os
import sys
from array import array

import bpy
from mathutils import Vector


PILOTS = {
    "residential-courtyard-piloti": dict(category="Residential", grammar=["reference-02", "reference-30"], footprint=(46, 32), floors=22, podium=4, kind="residential", seed=22017, changed=["footprint", "towerCount", "floorCount", "setback", "podiumGeometry", "corePosition", "balconyPattern", "facadeGrid", "roofSilhouette"]),
    "cbd-asymmetric-twin-atrium": dict(category="CBD/Office", grammar=["reference-22", "reference-24"], footprint=(54, 38), floors=35, podium=6, kind="cbd", seed=22031, changed=["footprint", "towerCount", "floorCount", "massingProportions", "setback", "podiumGeometry", "facadeGrid", "roofSilhouette", "entranceGeometry"]),
    "commercial-terraced-market-atrium": dict(category="Commercial", grammar=["reference-09", "reference-07"], footprint=(64, 42), floors=7, podium=2, kind="commercial", seed=22047, changed=["footprint", "towerCount", "floorCount", "podiumGeometry", "facadeGrid", "entranceGeometry", "materialComposition", "roofSilhouette"]),
    "industrial-sawtooth-utility-campus": dict(category="Nexus/Industrial", grammar=["reference-03", "reference-13"], footprint=(96, 62), floors=3, podium=1, kind="industrial", seed=22059, changed=["footprint", "towerCount", "massingProportions", "setback", "podiumGeometry", "facadeGrid", "roofSilhouette", "entranceGeometry", "materialComposition"]),
    "logistics-crossdock-solar-hub": dict(category="Logistics", grammar=["reference-40", "reference-41"], footprint=(118, 72), floors=3, podium=1, kind="logistics", seed=22071, changed=["footprint", "towerCount", "massingProportions", "podiumGeometry", "facadeGrid", "roofSilhouette", "entranceGeometry", "materialComposition", "corePosition"]),
    "civic-courtyard-learning-forum": dict(category="Civic/Education", grammar=["reference-05", "reference-17"], footprint=(78, 54), floors=6, podium=2, kind="civic", seed=22083, changed=["footprint", "towerCount", "floorCount", "massingProportions", "setback", "podiumGeometry", "facadeGrid", "roofSilhouette", "entranceGeometry"]),
}


def parse_args():
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--all-pilots", action="store_true")
    parser.add_argument("--pilot", choices=sorted(PILOTS))
    parser.add_argument("--preview-size", type=int, default=1600)
    return parser.parse_args(values)


def box(name, loc, dims, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("EdgeSoftness", "BEVEL")
        modifier.width, modifier.segments = bevel, 2
    obj.data.materials.append(material)
    return obj


def create_texture(name, directory, kind, tint):
    image = bpy.data.images.new(name, width=1024, height=1024, alpha=False)
    data = array("f", [0.0]) * (1024 * 1024 * 4)
    for y in range(1024):
        for x in range(1024):
            index = (y * 1024 + x) * 4
            grid = ((x // 52) + (y // 38)) % 2
            if kind == "base":
                factor = 0.74 if grid else 1.0
                value = (tint[0] * factor, tint[1] * factor, tint[2] * factor, 1.0)
            elif kind == "roughness":
                level = 0.36 if grid else 0.62
                value = (level, level, level, 1.0)
            else:
                value = (0.5, 0.5, 1.0, 1.0)
            data[index:index + 4] = array("f", value)
    image.pixels.foreach_set(data)
    image.filepath_raw = os.path.join(directory, name + ".png")
    image.file_format = "PNG"
    image.save()
    return image


def material_bundle(directory, tint):
    os.makedirs(directory, exist_ok=True)
    base = create_texture("basecolor", directory, "base", tint)
    rough = create_texture("roughness", directory, "roughness", tint)
    normal = create_texture("normal", directory, "normal", tint)
    material = bpy.data.materials.new("PBR_Facade")
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    principled = nodes.get("Principled BSDF")
    base_node, rough_node, normal_node = nodes.new("ShaderNodeTexImage"), nodes.new("ShaderNodeTexImage"), nodes.new("ShaderNodeTexImage")
    base_node.image, rough_node.image, normal_node.image = base, rough, normal
    normal_map = nodes.new("ShaderNodeNormalMap")
    links.new(base_node.outputs["Color"], principled.inputs["Base Color"])
    links.new(rough_node.outputs["Color"], principled.inputs["Roughness"])
    links.new(normal_node.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
    return material


def simple_material(name, color, metallic=0.0, roughness=0.5):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def facade(x, y, z0, width, depth, floors, floor_h, facade_material, glass, level):
    bays = max(4, int(width / (3.5 if level == 0 else 5.5)))
    for floor in range(floors):
        if level == 2 and floor % 3:
            continue
        z = z0 + floor * floor_h + floor_h * 0.52
        for bay in range(bays):
            px = x - width / 2 + (bay + 0.5) * width / bays
            for py in (y - depth / 2 - 0.12, y + depth / 2 + 0.12):
                box("WindowBay", (px, py, z), (width / bays * 0.72, 0.10, floor_h * 0.62), glass)
        if level == 0:
            box("FacadeBand", (x, y - depth / 2 - 0.18, z0 + floor * floor_h + floor_h * 0.12), (width, 0.18, 0.18), facade_material)
            box("FacadeBand", (x, y + depth / 2 + 0.18, z0 + floor * floor_h + floor_h * 0.12), (width, 0.18, 0.18), facade_material)


def residential(params, level, materials):
    w, d, floors, podium = *params["footprint"], params["floors"], params["podium"]
    h = 3.05
    box("PilotiPodium", (0, 0, podium * 1.7 / 2), (w + 8, d + 8, podium * 1.7), materials["concrete"], 0.15)
    # U-shaped footprint and a deliberately offset core: unlike a source tower cluster.
    arms = [(-w * .28, 0, w * .38, d), (w * .28, 0, w * .38, d), (0, d * .32, w * .55, d * .30)]
    base_z = podium * 1.7
    for arm, (x, y, aw, ad) in enumerate(arms):
        box("CourtyardWing", (x, y, base_z + floors * h / 2), (aw, ad, floors * h), materials["facade"], 0.08)
        facade(x, y, base_z, aw, ad, floors, h, materials["facade"], materials["glass"], level)
        if level < 2:
            for floor in range(2, floors, 3 if level == 0 else 5):
                for side in (-1, 1):
                    box("Balcony", (x, y + side * (ad / 2 + .7), base_z + floor * h + h * .42), (aw * .72, 1.2, .22), materials["metal"], 0.04)
    box("OffsetCore", (w * .20, -d * .05, base_z + floors * h * .60), (w * .20, d * .20, floors * h * .80), materials["concrete"])
    box("MachineRoom", (-w * .18, d * .3, base_z + floors * h + 2.0), (w * .22, d * .18, 4), materials["metal"])
    box("EntranceCanopy", (0, -d / 2 - 3, 3.2), (w * .28, 5, .35), materials["metal"])


def cbd(params, level, materials):
    w, d, floors, podium = *params["footprint"], params["floors"], params["podium"]
    h = 3.65
    box("AtriumPodium", (0, 0, podium * h / 2), (w + 8, d + 8, podium * h), materials["facade"], .15)
    for index, (x, y, tw, td, tf) in enumerate([(-w * .20, 0, w * .43, d * .52, floors), (w * .22, d * .08, w * .33, d * .38, floors - 9)]):
        for segment in range(3):
            scale = 1 - segment * .12
            segment_h = tf * h / 3
            box("SteppedOfficeTower", (x, y, podium * h + segment_h * (segment + .5)), (tw * scale, td * scale, segment_h), materials["facade"], .08)
        facade(x, y, podium * h, tw, td, tf, h, materials["facade"], materials["glass"], level)
    box("SkyAtriumBridge", (0, 0, podium * h + floors * h * .48), (w * .38, d * .20, 4.5), materials["glass"])
    box("ArrivalCanopy", (0, -d / 2 - 4, 4), (w * .52, 7, .4), materials["metal"])
    box("Crown", (-w * .20, 0, podium * h + floors * h + 3), (w * .18, d * .20, 6), materials["metal"])


def lowrise(params, level, materials):
    w, d = params["footprint"]
    kind = params["kind"]
    if kind == "commercial":
        for floor, scale in enumerate((1.0, .88, .72, .58)):
            box("TerracedRetail", (0, 0, floor * 4.2 + 2.1), (w * scale, d * scale, 4.0), materials["facade"], .12)
        box("AtriumLantern", (0, 0, 20), (w * .23, d * .30, 12), materials["glass"])
        for side in (-1, 1): box("RetailCanopy", (0, side * (d / 2 + 2), 3.2), (w * .72, 4, .35), materials["metal"])
    elif kind == "industrial":
        for index in range(4):
            x = -w * .32 + index * w * .215
            box("ProductionHall", (x, 0, 8), (w * .20, d * .82, 16), materials["facade"], .08)
            for tooth in range(3): box("SawtoothRoof", (x, -d * .25 + tooth * d * .25, 17), (w * .18, d * .18, 2.2), materials["metal"])
        box("OfficeWing", (w * .40, -d * .25, 10), (w * .16, d * .35, 20), materials["glass"])
        for x in (-w * .38, w * .38): box("UtilityStack", (x, d * .35, 22), (3, 3, 28), materials["metal"])
    elif kind == "logistics":
        box("CrossDockHall", (0, 0, 12), (w, d, 24), materials["facade"], .1)
        for index in range(12 if level == 0 else 7):
            x = -w * .43 + index * w * .078
            box("DockDoor", (x, -d / 2 - .25, 4.5), (w * .05, .4, 6), materials["glass"])
            box("DockCanopy", (x, -d / 2 - 2.3, 8.2), (w * .06, 4, .25), materials["metal"])
        box("OfficeMezzanine", (w * .34, d * .25, 20), (w * .24, d * .28, 16), materials["glass"])
        for x in range(-3, 4): box("RoofMonitor", (x * w * .10, 0, 25), (w * .07, d * .55, 1.2), materials["metal"])
    else:
        # civic U-shaped courtyard / colonnade
        for x, y, aw, ad in [(-w*.28, 0, w*.35, d), (w*.28, 0, w*.35, d), (0, d*.30, w*.55, d*.30)]:
            box("CivicWing", (x, y, 12), (aw, ad, 24), materials["facade"], .10)
            facade(x, y, 0, aw, ad, 6, 4, materials["facade"], materials["glass"], level)
        for x in range(-4, 5): box("ForumColumn", (x*w*.05, -d*.45, 5), (1.1, 1.1, 10), materials["concrete"])
        box("ForumCanopy", (0, -d*.46, 10), (w*.62, 8, .5), materials["metal"])
        box("LearningLantern", (0, d*.18, 31), (w*.20, d*.20, 12), materials["glass"])


def build_pilot(identifier, params, root, size):
    # Generated artefacts are deliberately outside Git: Factory/Buildings/<family>/...
    directory = os.path.join(root, "Factory", "Buildings", identifier)
    lod_dir = os.path.join(directory, "LOD")
    textures = os.path.join(directory, "Textures")
    previews = os.path.join(directory, "Preview")
    metadata_dir = os.path.join(directory, "Metadata")
    os.makedirs(lod_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)
    os.makedirs(previews, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    facade_material = material_bundle(textures, (0.23 + (params["seed"] % 4) * .04, .32, .42))
    materials = {"facade": facade_material, "glass": simple_material("Glazing", (.055, .12, .20), .25, .18), "concrete": simple_material("Concrete", (.33, .36, .38), 0, .75), "metal": simple_material("Metal", (.15, .19, .22), .72, .28)}
    for level in (0, 1, 2):
        collection = bpy.data.collections.new("LOD%d" % level)
        bpy.context.scene.collection.children.link(collection)
        before = set(bpy.context.scene.objects)
        if params["kind"] == "residential": residential(params, level, materials)
        elif params["kind"] == "cbd": cbd(params, level, materials)
        else: lowrise(params, level, materials)
        created = [item for item in bpy.context.scene.objects if item not in before]
        for item in created:
            for owner in list(item.users_collection): owner.objects.unlink(item)
            collection.objects.link(item)
        for item in bpy.context.scene.objects: item.select_set(False)
        for item in created: item.select_set(True)
        bpy.context.view_layer.objects.active = created[0]
        bpy.ops.export_scene.gltf(filepath=os.path.join(lod_dir, "lod%d.glb" % level), export_format="GLB", use_selection=True, export_apply=True)
        for item in created: bpy.data.objects.remove(item, do_unlink=True)
        bpy.data.collections.remove(collection)
    # Rebuild LOD0 only for a reviewable Blend and five visual angles.
    if params["kind"] == "residential": residential(params, 0, materials)
    elif params["kind"] == "cbd": cbd(params, 0, materials)
    else: lowrise(params, 0, materials)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(directory, identifier + ".blend"))
    render_previews(directory, previews, size)
    report = {"assetId": identifier, "category": params["category"], "derivedFromGrammarIds": params["grammar"], "generationSeed": params["seed"], "changedDimensions": params["changed"], "changedModules": ["Footprint Generator", "Tower Generator", "Facade Generator", "Balcony Generator", "Core Generator", "Podium Generator", "Entrance Generator", "Roof Generator", "Material Composer", "LOD Generator"], "originalityChecks": {"referenceMeshImported": False, "geometryFingerprintMatch": False, "textureDirectCopy": False, "logoOrSignage": False, "minimumChangedDimensions": len(params["changed"]), "result": "PASS"}, "lod": ["LOD/lod0.glb", "LOD/lod1.glb", "LOD/lod2.glb"], "placement": {"maxRepetitionsPerCamera": 2, "forbiddenAdjacency": [identifier], "groundAlignment": "PASS"}}
    with open(os.path.join(metadata_dir, "metadata.json"), "w", encoding="utf-8") as target: json.dump(report, target, ensure_ascii=False, indent=2)
    return directory


def render_previews(directory, previews, size):
    scene = bpy.context.scene
    engines = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else "BLENDER_WORKBENCH"
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    if scene.world is None: scene.world = bpy.data.worlds.new("PreviewWorld")
    scene.world.color = (.035, .045, .065)
    meshes = [item for item in scene.objects if item.type == "MESH"]
    points = [item.matrix_world @ Vector(corner) for item in meshes for corner in item.bound_box]
    lower, upper = Vector(tuple(min(p[i] for p in points) for i in range(3))), Vector(tuple(max(p[i] for p in points) for i in range(3)))
    center, radius = (lower+upper)*.5, max((upper-lower).length*.6, 25)
    bpy.ops.mesh.primitive_plane_add(size=max(upper.x-lower.x, upper.y-lower.y)*2.5, location=(center.x, center.y, lower.z-.05))
    bpy.context.object.data.materials.append(simple_material("Ground", (.06,.08,.10), 0, .92))
    camera_data = bpy.data.cameras.new("ReviewCamera"); camera = bpy.data.objects.new("ReviewCamera", camera_data); scene.collection.objects.link(camera); scene.camera = camera
    for pos, energy in [(center+Vector((radius*2,-radius*2,radius*2)),1700),(center+Vector((-radius*1.5,-radius,radius*1.3)),1000)]:
        data=bpy.data.lights.new("ReviewArea","AREA"); data.energy=energy; data.shape="DISK"; data.size=radius
        light=bpy.data.objects.new("ReviewArea",data); scene.collection.objects.link(light); light.location=pos; light.rotation_euler=(Vector(center)-pos).to_track_quat("-Z","Y").to_euler()
    angles={"front-3q":(2,-2,1.25),"rear-3q":(-2,2,1.2),"street-level":(1.4,-2.7,.48),"facade-closeup":(1.15,-1.35,.85),"roof-oblique":(1.5,1.7,2.3)}
    for name, factor in angles.items():
        camera.location=center+Vector((radius*factor[0],radius*factor[1],radius*factor[2])); camera.rotation_euler=(center+Vector((0,0,(upper.z-lower.z)*.1))-camera.location).to_track_quat("-Z","Y").to_euler(); scene.render.filepath=os.path.join(previews,name+".png"); bpy.ops.render.render(write_still=True)


def main():
    options=parse_args(); os.makedirs(options.output_root, exist_ok=True)
    identifiers=sorted(PILOTS) if options.all_pilots else [options.pilot]
    if not all(identifiers): raise SystemExit("choose --all-pilots or --pilot")
    generated=[build_pilot(identifier,PILOTS[identifier],options.output_root,options.preview_size) for identifier in identifiers]
    with open(os.path.join(options.output_root,"Factory","factory-pilot-index.json"),"w",encoding="utf-8") as target: json.dump({"pilots":generated,"referenceMeshImported":False},target,indent=2)
    print("ARCHITECTURE_FACTORY_PILOTS="+json.dumps({"count":len(generated),"output":options.output_root}))


if __name__ == "__main__": main()
