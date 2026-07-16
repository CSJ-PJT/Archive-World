"""Generate and inspect 20 non-canonical Residential Batch 1 GLB candidates.

The script is deliberately isolated from Archive City's canonical V2/V3
manifests and layout.  All mutable GLB, preview, metadata, render and sandbox
artifacts are written below WorldOutput only.  Candidate records are suitable
for human review, never automatic canonical promotion.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
import subprocess
import struct
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))
from world_output import resolve_output_root

ARGS = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
REPO = Path(ARGS[ARGS.index("--repo") + 1]).resolve() if "--repo" in ARGS else Path.cwd()
OUTPUT = resolve_output_root(ARGS)
CONFIG = json.loads((REPO / "scripts/blender/residential_batch1_candidates.json").read_text(encoding="utf8"))
FLOOR_HEIGHT = 3.0


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def mat(name: str, color: tuple[float, float, float, float], metallic: float = 0.0, roughness: float = 0.6):
    value = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    value.use_nodes = True
    bsdf = value.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return value


CONCRETE = mat("RB1 Concrete", (0.31, 0.35, 0.36, 1), 0.02, 0.73)
GLASS = mat("RB1 Glass", (0.08, 0.24, 0.34, 1), 0.35, 0.22)
BALCONY = mat("RB1 Balcony", (0.54, 0.57, 0.56, 1), 0.08, 0.48)
ROOF = mat("RB1 Roof", (0.11, 0.16, 0.18, 1), 0.45, 0.36)
GREEN = mat("RB1 Green", (0.14, 0.36, 0.17, 1), 0.0, 0.8)
PAVING = mat("RB1 Paving", (0.18, 0.22, 0.23, 1), 0.04, 0.72)
ACCENT = mat("RB1 Accent", (0.63, 0.46, 0.24, 1), 0.18, 0.42)


def box(name: str, loc: tuple[float, float, float], dims: tuple[float, float, float], material, rotation: float = 0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=(0, 0, rotation))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj


def cylinder(name: str, loc: tuple[float, float, float], radius: float, depth: float, material, vertices: int = 12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def tower(name: str, x: float, y: float, width: float, depth: float, floors: int, balcony_axis: str = "front") -> list:
    height = floors * FLOOR_HEIGHT
    created = [box(name + "-mass", (x, y, height / 2), (width, depth, height), GLASS)]
    for floor in range(3, floors, 3):
        z = floor * FLOOR_HEIGHT
        if balcony_axis == "front":
            created.append(box(name + "-balcony-" + str(floor), (x, y - depth / 2 - 0.42, z), (width + 1.5, 0.8, 0.62), BALCONY))
        elif balcony_axis == "side":
            created.append(box(name + "-balcony-" + str(floor), (x + width / 2 + 0.42, y, z), (0.8, depth + 1.5, 0.62), BALCONY))
        else:
            created.append(box(name + "-belt-" + str(floor), (x, y, z), (width + 0.6, depth + 0.6, 0.48), BALCONY))
    created.append(box(name + "-roof", (x, y, height + 0.8), (width + 2, depth + 2, 1.6), ROOF))
    return created


def podium(name: str, width: float, depth: float, height: float = 5.0) -> list:
    items = [box(name + "-podium", (0, 0, height / 2), (width, depth, height), CONCRETE)]
    items.append(box(name + "-entry", (0, -depth / 2 - 0.36, 1.7), (width * 0.48, 0.7, 2.7), ACCENT))
    return items


def radial_bar(name: str, angle: float, distance: float, width: float, depth: float, floors: int) -> list:
    x, y = math.cos(angle) * distance, math.sin(angle) * distance
    height = floors * FLOOR_HEIGHT
    obj = box(name + "-wing", (x, y, height / 2), (width, depth, height), GLASS, angle)
    return [obj, box(name + "-wing-roof", (x, y, height + 0.7), (width + 1.5, depth + 1.5, 1.4), ROOF, angle)]


def build(candidate: dict) -> list:
    width, depth = candidate["footprint"]
    floors, form, ident = candidate["floors"], candidate["form"], candidate["assetId"]
    made: list = []
    if form == "courtyard":
        made += podium(ident, width, depth, 5)
        made += tower(ident + "-north", 0, depth * 0.23, width * 0.48, depth * 0.22, floors)
        made += tower(ident + "-west", -width * 0.29, -depth * 0.12, width * 0.18, depth * 0.44, floors - 5, "side")
        made += tower(ident + "-east", width * 0.29, -depth * 0.12, width * 0.18, depth * 0.44, floors - 8, "side")
        made.append(box(ident + "-court", (0, -depth * 0.09, 5.08), (width * 0.46, depth * 0.34, 0.16), GREEN))
    elif form == "slab_a":
        made += podium(ident, width * 1.1, depth * 1.1, 4)
        made += tower(ident, 0, 0, width * 0.66, depth * 0.70, floors)
        made.append(box(ident + "-offset-core", (width * 0.18, depth * 0.16, floors * FLOOR_HEIGHT * 0.55), (width * 0.18, depth * 0.20, floors * FLOOR_HEIGHT * 1.1), CONCRETE))
        made.append(box(ident + "-canopy", (0, -depth * 0.58, 5.0), (width * 0.64, 5.0, 1.1), ROOF))
    elif form == "slab_b":
        made += podium(ident, width, depth, 5)
        made += tower(ident + "-west", -width * 0.19, 0, width * 0.34, depth * 0.60, floors, "side")
        made += tower(ident + "-east", width * 0.19, 0, width * 0.34, depth * 0.60, floors - 4, "front")
        made.append(box(ident + "-lift-core", (0, depth * 0.12, floors * FLOOR_HEIGHT * 0.52), (width * 0.16, depth * 0.24, floors * FLOOR_HEIGHT * 1.04), CONCRETE))
    elif form == "point_a":
        made += podium(ident, width, depth, 5)
        made += tower(ident + "-core", 0, 0, width * 0.28, depth * 0.28, floors, "belt")
        for angle in (0, math.pi / 2, math.pi, math.pi * 1.5):
            made += radial_bar(ident + "-wing-" + str(round(angle, 2)), angle, width * 0.16, width * 0.46, depth * 0.20, floors - 5)
        made.append(box(ident + "-crown", (0, 0, floors * FLOOR_HEIGHT + 3), (width * 0.34, depth * 0.34, 4), ACCENT))
    elif form == "point_b":
        made += podium(ident, width, depth, 4)
        made += tower(ident + "-core", 0, 0, width * 0.24, depth * 0.24, floors - 2, "belt")
        for index, angle in enumerate((0, math.tau / 3, math.tau * 2 / 3)):
            made += radial_bar(ident + "-triwing-" + str(index), angle, width * 0.20, width * 0.52, depth * 0.22, floors - 6 - index * 2)
        for x, y in ((-width * 0.32, -depth * 0.26), (width * 0.32, -depth * 0.26)):
            made.append(cylinder(ident + "-piloti", (x, y, 3), 1.6, 6, CONCRETE))
    elif form == "stepped":
        made += podium(ident, width, depth, 5)
        levels = [(width * 0.78, depth * 0.70, floors // 3), (width * 0.62, depth * 0.58, floors // 3), (width * 0.45, depth * 0.46, floors - (floors // 3) * 2)]
        z = 5
        for index, (w, d, count) in enumerate(levels):
            h = count * FLOOR_HEIGHT
            made.append(box(ident + "-step-" + str(index), (index * 3.5, 0, z + h / 2), (w, d, h), GLASS))
            made.append(box(ident + "-terrace-" + str(index), (index * 3.5 - 2, 0, z + h + 0.5), (w + 2, d + 2, 1), GREEN))
            z += h
    elif form == "pair":
        made += podium(ident, width, depth, 6)
        made += tower(ident + "-tall", -width * 0.23, 0, width * 0.30, depth * 0.54, floors)
        made += tower(ident + "-short", width * 0.23, depth * 0.04, width * 0.30, depth * 0.48, floors - 9, "side")
        made.append(box(ident + "-shared-roof", (0, 0, 7), (width * 0.78, depth * 0.70, 1.2), GREEN))
    elif form == "arc":
        made += podium(ident, width, depth, 4)
        for index, angle in enumerate((-0.92, -0.62, -0.31, 0, 0.31, 0.62, 0.92)):
            radius = width * 0.34
            x, y = math.sin(angle) * radius, math.cos(angle) * radius * 0.48
            local_floors = floors - abs(index - 3) * 2
            made += tower(ident + "-arc-" + str(index), x, y, width * 0.12, depth * 0.32, local_floors, "belt")
        made.append(box(ident + "-park", (0, -depth * 0.14, 4.1), (width * 0.48, depth * 0.28, 0.16), GREEN))
    elif form == "bridge":
        made += podium(ident, width, depth, 6)
        made += tower(ident + "-left", -width * 0.24, 0, width * 0.26, depth * 0.55, floors)
        made += tower(ident + "-right", width * 0.24, 0, width * 0.26, depth * 0.55, floors - 5)
        bridge_z = (floors - 9) * FLOOR_HEIGHT
        made.append(box(ident + "-sky-garden", (0, 0, bridge_z), (width * 0.34, depth * 0.30, 5), GREEN))
        made.append(box(ident + "-bridge-glass", (0, -depth * 0.18, bridge_z), (width * 0.36, 0.8, 5.6), GLASS))
    elif form == "terrace":
        made += podium(ident, width, depth, 5)
        for index, count in enumerate((floors // 4, floors // 4, floors // 4, floors - (floors // 4) * 3)):
            h = count * FLOOR_HEIGHT
            z0 = 5 + sum((floors // 4 if j < 3 else floors - (floors // 4) * 3) * FLOOR_HEIGHT for j in range(index))
            w = width * (0.82 - index * 0.13)
            d = depth * (0.78 - index * 0.11)
            made.append(box(ident + "-terrace-mass-" + str(index), (-index * 3, 0, z0 + h / 2), (w, d, h), GLASS))
            made.append(box(ident + "-terrace-green-" + str(index), (-index * 3 + w * 0.18, 0, z0 + h + 0.4), (w * 0.45, d * 0.55, 0.7), GREEN))
    elif form == "mid_courtyard":
        made += podium(ident, width, depth, 2.5)
        for index, (x, y, w, d) in enumerate(((0, depth * .31, width * .76, depth * .17), (0, -depth * .31, width * .76, depth * .17), (-width * .37, 0, width * .17, depth * .55), (width * .37, 0, width * .17, depth * .55))):
            made += tower(ident + "-wing-" + str(index), x, y, w, d, floors - (index % 2), "belt")
        made.append(box(ident + "-court", (0, 0, 2.62), (width * .48, depth * .42, .18), GREEN))
    elif form == "mid_bar":
        made += podium(ident, width, depth, 3.2)
        made += tower(ident, 0, 0, width * .88, depth * .66, floors, "front")
        made.append(box(ident + "-stair-a", (-width * .31, depth * .38, floors * FLOOR_HEIGHT * .35), (width * .12, depth * .14, floors * FLOOR_HEIGHT * .7), CONCRETE))
        made.append(box(ident + "-stair-b", (width * .31, depth * .38, floors * FLOOR_HEIGHT * .30), (width * .12, depth * .14, floors * FLOOR_HEIGHT * .6), CONCRETE))
    elif form == "mid_zigzag":
        made += podium(ident, width, depth, 3.5)
        for index, x in enumerate((-width * .24, 0, width * .24)):
            made += tower(ident + "-zig-" + str(index), x, (index % 2 - .5) * depth * .18, width * .30, depth * .54, floors - index, "side")
        made.append(box(ident + "-zig-roof", (0, 0, floors * FLOOR_HEIGHT + 1), (width * .66, depth * .28, 1), ROOF, .15))
    elif form == "mid_l":
        made += podium(ident, width, depth, 3.5)
        made += tower(ident + "-long", -width * .10, depth * .18, width * .72, depth * .25, floors, "front")
        made += tower(ident + "-short", width * .23, -depth * .12, width * .23, depth * .63, floors - 2, "side")
        made.append(box(ident + "-community", (-width * .20, -depth * .18, 5.5), (width * .28, depth * .25, 4), ACCENT))
    elif form == "mid_shopbase":
        made += podium(ident, width, depth, 8)
        made.append(box(ident + "-arcade", (0, -depth * .52, 3), (width * .82, 3.5, 3.5), ACCENT))
        made += tower(ident + "-housing", 0, depth * .06, width * .62, depth * .55, floors - 3, "front")
        made.append(box(ident + "-canopy", (0, -depth * .62, 7.7), (width * .96, 7, 1.2), ROOF))
    elif form == "villa_a":
        made += podium(ident, width, depth, 1.2)
        for index, (x, y, local_floors) in enumerate(((-width * .22, 0, floors), (width * .06, depth * .12, floors + 1), (width * .27, -depth * .12, floors + 2))):
            made += tower(ident + "-villa-" + str(index), x, y, width * .23, depth * .40, local_floors, "side")
            made.append(box(ident + "-stair-" + str(index), (x - width * .13, y - depth * .27, 1.5), (width * .08, depth * .14, 3), CONCRETE))
    elif form == "villa_b":
        made += podium(ident, width, depth, 1.4)
        for index, (x, y) in enumerate(((0, depth * .28), (0, -depth * .28), (-width * .32, 0), (width * .32, 0))):
            made += tower(ident + "-court-villa-" + str(index), x, y, width * .26, depth * .18 if index < 2 else depth * .48, floors, "belt")
        made.append(box(ident + "-inner-garden", (0, 0, 1.52), (width * .42, depth * .36, .16), GREEN))
    elif form == "town_row":
        made += podium(ident, width, depth, 1.0)
        for index in range(5):
            x = -width * .34 + index * width * .17
            local_floors = floors + (index % 3 == 1)
            made += tower(ident + "-home-" + str(index), x, 0, width * .145, depth * .66, local_floors, "front")
            made.append(box(ident + "-porch-" + str(index), (x, -depth * .39, 1.2), (width * .12, depth * .12, 1.1), ACCENT))
    elif form == "town_corner":
        made += podium(ident, width, depth, 1.0)
        for index, (x, y, w, d) in enumerate(((-width * .15, depth * .19, width * .52, depth * .26), (width * .21, -depth * .11, width * .24, depth * .52), (-width * .29, -depth * .21, width * .22, depth * .20))):
            made += tower(ident + "-corner-" + str(index), x, y, w, d, floors + (index == 1), "belt")
        made.append(box(ident + "-garage-court", (-width * .18, -depth * .12, 1.12), (width * .22, depth * .22, .24), PAVING))
    elif form == "civic_living":
        made += podium(ident, width, depth, 6)
        made += tower(ident + "-clinic-wing", -width * .14, depth * .16, width * .52, depth * .25, floors - 1, "front")
        made += tower(ident + "-living-wing", width * .23, -depth * .10, width * .22, depth * .62, floors, "side")
        made.append(box(ident + "-clinic-entry", (-width * .18, -depth * .42, 3), (width * .34, 2, 4), ACCENT))
        made.append(box(ident + "-roof-garden", (0, 0, 6.4), (width * .45, depth * .38, .7), GREEN))
    else:
        raise ValueError("unknown form: " + form)
    return made


def bounds(objects: list) -> dict:
    points = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        points.extend(obj.matrix_world @ Vector(point) for point in obj.bound_box)
    low = [min(point[index] for point in points) for index in range(3)]
    high = [max(point[index] for point in points) for index in range(3)]
    return {"min": [round(value, 4) for value in low], "max": [round(value, 4) for value in high], "dimensions": [round(high[index] - low[index], 4) for index in range(3)]}


def statistics(objects: list) -> tuple[int, int]:
    triangles, materials = 0, set()
    for obj in objects:
        if obj.type != "MESH":
            continue
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
        materials.update(slot.material.name for slot in obj.material_slots if slot.material)
    return triangles, len(materials)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def glb_error(path: Path) -> str | None:
    bytes_ = path.read_bytes()
    if len(bytes_) < 20:
        return "file-too-small"
    magic, version, declared_length = struct.unpack("<4sII", bytes_[:12])
    if magic != b"glTF" or version != 2 or declared_length != len(bytes_):
        return "invalid-header"
    json_length, json_type = struct.unpack("<II", bytes_[12:20])
    if json_type != 0x4E4F534A or 20 + json_length > len(bytes_):
        return "invalid-json-chunk"
    try:
        payload = json.loads(bytes_[20 : 20 + json_length].decode("utf8"))
    except Exception:
        return "invalid-json"
    return None if payload.get("meshes") else "no-meshes"


def configure_render(width: int, height: int, samples: int = 16) -> None:
    scene = bpy.context.scene
    available = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in available else "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = samples
    scene.world.color = (0.018, 0.028, 0.04)


def aim(camera, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def add_camera_and_lights(target: Vector, extent: float, context: bool):
    distance = extent * (2.05 if context else 1.62)
    camera_data = bpy.data.cameras.new("RB1 Camera")
    camera = bpy.data.objects.new("RB1 Camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = target + Vector((distance * .78, -distance, distance * (.62 if context else .75)))
    aim(camera, target + Vector((0, 0, extent * .14)))
    bpy.context.scene.camera = camera
    for name, loc, energy, size in (("Key", (extent, -extent, extent * 1.5), 1500, extent), ("Fill", (-extent, -extent * .5, extent), 900, extent * .8)):
        light_data = bpy.data.lights.new(name, "AREA")
        light_data.energy, light_data.shape, light_data.size = energy, "DISK", size
        light = bpy.data.objects.new(name, light_data)
        bpy.context.collection.objects.link(light)
        light.location = loc
        aim(light, target)
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 1.8
    sun = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(28), math.radians(-18), math.radians(-28))


def render_previews(candidate: dict, model_objects: list, target_dir: Path, model_bounds: dict) -> list[str]:
    target_dir.mkdir(parents=True, exist_ok=True)
    extent = max(model_bounds["dimensions"])
    centre = Vector(((model_bounds["min"][0] + model_bounds["max"][0]) / 2, (model_bounds["min"][1] + model_bounds["max"][1]) / 2, model_bounds["dimensions"][2] / 2))
    configure_render(800, 600)
    add_camera_and_lights(centre, extent, False)
    asset_path = target_dir / (candidate["assetId"] + "-asset.png")
    bpy.context.scene.render.filepath = str(asset_path)
    bpy.ops.render.render(write_still=True)
    box("context-ground", (centre.x, centre.y, -0.18), (extent * 3.2, extent * 3.2, 0.25), PAVING)
    box("context-road-x", (centre.x, centre.y - extent * .75, 0.01), (extent * 3.0, extent * .26, 0.08), ROOF)
    box("context-road-y", (centre.x + extent * .76, centre.y, 0.02), (extent * .25, extent * 3.0, 0.08), ROOF)
    for index, (x, y) in enumerate(((-.72, -.35), (.68, -.42), (-.45, .68), (.58, .62))):
        cylinder("context-tree-" + str(index), (centre.x + x * extent, centre.y + y * extent, extent * .12), extent * .045, extent * .24, GREEN, 10)
    bpy.context.scene.camera.location = centre + Vector((extent * 1.85, -extent * 2.2, extent * 1.05))
    aim(bpy.context.scene.camera, centre + Vector((0, 0, extent * .16)))
    context_path = target_dir / (candidate["assetId"] + "-context.png")
    bpy.context.scene.render.filepath = str(context_path)
    bpy.ops.render.render(write_still=True)
    return [str(asset_path), str(context_path)]


def memory_mb() -> float | None:
    if os.name != "nt":
        return None
    try:
        value = subprocess.check_output(
            ["powershell.exe", "-NoProfile", "-Command", f"(Get-Process -Id {os.getpid()}).WorkingSet64"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return round(int(value) / 1024 / 1024, 2)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def sandbox(paths: list[Path], report_path: Path) -> dict:
    clear_scene()
    configure_render(1280, 720, 12)
    start_memory = memory_mb()
    start = time.perf_counter()
    imported = []
    for path in paths:
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(path))
        objects = [obj for obj in set(bpy.context.scene.objects) - before if obj.type == "MESH"]
        imported.append(objects)
        for obj in objects:
            obj.hide_render = True
    import_seconds = time.perf_counter() - start
    instance_start = time.perf_counter()
    for index in range(60):
        source = imported[index % len(imported)]
        col, row = index % 10, index // 10
        offset = Vector(((col - 4.5) * 16, (row - 2.5) * 17, 0))
        for obj in source:
            copy = obj.copy()
            copy.data = obj.data
            bpy.context.collection.objects.link(copy)
            copy.hide_render = False
            copy.location = Vector(obj.location) * .10 + offset
            copy.scale = Vector(obj.scale) * .10
    instance_seconds = time.perf_counter() - instance_start
    box("sandbox-ground", (0, 0, -0.22), (175, 125, .25), PAVING)
    target = Vector((0, 0, 8))
    add_camera_and_lights(target, 58, True)
    render_start = time.perf_counter()
    bpy.context.scene.render.filepath = str(report_path.with_suffix(".png"))
    bpy.ops.render.render(write_still=True)
    render_seconds = time.perf_counter() - render_start
    result = {
        "schema": "archive-world.residential-sandbox/v1",
        "candidatesLoaded": len(paths),
        "instances": 60,
        "loadSeconds": round(import_seconds, 4),
        "instancingSeconds": round(instance_seconds, 4),
        "eeveeFrameSeconds": round(render_seconds, 4),
        "eeveeFrameEquivalentFps": round(1 / render_seconds, 2) if render_seconds else None,
        "workingSetMbBefore": start_memory,
        "workingSetMbAfter": memory_mb(),
        "note": "Headless EEVEE frame-equivalent benchmark; not an interactive Viewer FPS claim.",
    }
    report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    return result


def contact_sheet(paths: list[Path], target: Path) -> None:
    clear_scene()
    configure_render(2000, 1400, 12)
    for index, path in enumerate(paths):
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(path))
        objects = [obj for obj in set(bpy.context.scene.objects) - before if obj.type == "MESH"]
        col, row = index % 5, index // 5
        offset = Vector(((col - 2) * 31, (1.5 - row) * 31, 0))
        for obj in objects:
            obj.location = Vector(obj.location) * .18 + offset
            obj.scale = Vector(obj.scale) * .18
    box("contact-ground", (0, 0, -0.22), (180, 150, .25), PAVING)
    add_camera_and_lights(Vector((0, 0, 10)), 110, True)
    bpy.context.scene.render.filepath = str(target)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    runtime = OUTPUT.v3_runtime / "candidates" / "residential-batch-1"
    previews = OUTPUT.v3_previews / "candidates" / "residential-batch-1"
    metadata = OUTPUT.v3_metadata / "candidates"
    runtime.mkdir(parents=True, exist_ok=True)
    previews.mkdir(parents=True, exist_ok=True)
    metadata.mkdir(parents=True, exist_ok=True)
    results, glbs, errors = [], [], []
    for candidate in CONFIG["candidates"]:
        clear_scene()
        objects = build(candidate)
        measured_bounds = bounds(objects)
        triangles, material_count = statistics(objects)
        target = runtime / (candidate["assetId"] + ".glb")
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
        bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB", use_selection=True, export_apply=True)
        header_error = glb_error(target)
        if header_error:
            errors.append({"assetId": candidate["assetId"], "error": header_error})
        preview_paths = render_previews(candidate, objects, previews, measured_bounds)
        glbs.append(target)
        fingerprint = ":".join((candidate["form"], str(triangles), "x".join(str(round(value, 1)) for value in measured_bounds["dimensions"]), str(material_count)))
        results.append({
            "schema": "archive-world.residential-candidate-result/v1",
            **candidate,
            "candidateOnly": True,
            "canonicalStatus": "not-approved",
            "runtimePath": OUTPUT.logical(target),
            "previewPaths": [OUTPUT.logical(Path(path)) for path in preview_paths],
            "sha256": sha256(target),
            "bytes": target.stat().st_size,
            "bounds": measured_bounds,
            "triangleCount": triangles,
            "materialCount": material_count,
            "textureCount": 0,
            "groundAligned": measured_bounds["min"][2] >= -0.001 and measured_bounds["min"][2] <= 0.001,
            "geometryFingerprint": fingerprint,
            "nearDuplicate": False,
            "canonicalRecommendation": "review-recommended",
        })
    contact_target = OUTPUT.reports / "residential-batch1-contact-sheet.png"
    contact_sheet(glbs, contact_target)
    sandbox_report = OUTPUT.reports / "residential-batch1-sandbox.json"
    sandbox_result = sandbox(glbs, sandbox_report)
    manifest = {
        "schema": "archive-world.residential-batch1-manifest/v1",
        "candidateOnly": True,
        "canonicalStatus": "not-approved",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "blenderVersion": bpy.app.version_string,
        "configSchema": CONFIG["schema"],
        "validator": {"structuralGlbErrors": len(errors), "errors": errors},
        "contactSheet": OUTPUT.logical(contact_target),
        "sandbox": OUTPUT.logical(sandbox_report),
        "assets": results,
    }
    manifest_path = metadata / "residential-batch1-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "assets": len(results), "manifest": str(manifest_path), "contactSheet": str(contact_target), "sandbox": sandbox_result, "errors": errors}))
    if errors or len(results) != 20 or not all(item["groundAligned"] for item in results):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
