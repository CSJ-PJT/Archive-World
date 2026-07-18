"""Image-free calibrated architectural review studio for Blender 5.2.

The scene is intentionally external-output only. It creates calibration cards,
ground contact, key/fill/rim lighting and a small facade/entrance test assembly.
"""
import argparse
import json
import os
import sys

import bpy
from mathutils import Vector


def args():
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--size", type=int, default=768)
    return parser.parse_args(values)


def mat(name, color, roughness, metallic=0.0):
    value = bpy.data.materials.new(name)
    value.use_nodes = True
    bsdf = value.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return value


def cube(name, location, dimensions, material):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj


def light(name, location, energy, size, target):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    options = args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    concrete = mat("painted-concrete", (0.47, 0.49, 0.47), 0.72)
    stone = mat("light-stone", (0.70, 0.65, 0.56), 0.58)
    metal = mat("anodized-aluminum", (0.24, 0.29, 0.31), 0.30, 0.65)
    glass = mat("low-reflective-glass", (0.10, 0.24, 0.31), 0.18)
    dark = mat("dark-calibration", (0.04, 0.04, 0.04), 0.55)
    white = mat("white-calibration", (0.80, 0.80, 0.80), 0.60)
    ground = mat("neutral-ground", (0.37, 0.39, 0.38), 0.78)
    cube("ground", (0, 0, -0.2), (36, 28, 0.4), ground)
    cube("facade-solid", (0, 2.2, 6), (14, 0.7, 12), concrete)
    for x in (-5.25, -3.15, -1.05, 1.05, 3.15, 5.25):
        cube("recessed-window", (x, 1.78, 7), (1.45, 0.28, 7.8), glass)
        cube("mullion", (x + 0.84, 1.55, 7), (0.14, 0.32, 8.3), metal)
    cube("entrance-glazing", (0, 1.45, 2.3), (5.0, 0.35, 4.2), glass)
    cube("entrance-canopy", (0, -0.2, 4.7), (7.0, 3.0, 0.25), metal)
    cube("stone-podium", (0, 2.0, 1.2), (16, 2.4, 2.4), stone)
    for x, material in ((-8, concrete), (-4, white), (0, dark), (4, glass), (8, metal)):
        cube("calibration-sample", (x, -5.5, 1.5), (2.5, 1.0, 3.0), material)
    cube("human-scale", (-10, -1.5, 0.875), (0.45, 0.35, 1.75), dark)
    cube("sedan-scale", (9, -3, 0.75), (4.5, 1.8, 1.5), metal)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = options.size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.look = "AgX - Medium High Contrast"
    world = bpy.data.worlds.new("neutral-daylight")
    world.color = (0.44, 0.50, 0.58)
    scene.world = world
    target = Vector((0, 1.5, 5))
    light("key", (13, -15, 17), 1900, 7, target)
    light("fill", (-12, -8, 9), 850, 8, target)
    light("rim", (2, 10, 15), 1200, 6, target)
    camera_data = bpy.data.cameras.new("review-camera")
    camera = bpy.data.objects.new("review-camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.location = (18, -22, 12)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    output = os.path.join(options.output_root, "render-studio")
    os.makedirs(output, exist_ok=True)
    scene.render.filepath = os.path.join(output, "daylight-calibration.png")
    bpy.ops.render.render(write_still=True)
    report = {
        "mode": "DAYLIGHT_REVIEW", "engine": scene.render.engine, "viewTransform": scene.view_settings.look,
        "resolution": [options.size, options.size], "lights": ["key", "fill", "rim"],
        "calibration": ["18-percent-gray-proxy", "white", "dark", "glass", "metal", "human-1.75m", "sedan-4.5m"],
        "imageTextureNodes": 0, "externalImageReferences": 0, "output": "external-generated-only",
    }
    with open(os.path.join(output, "report.json"), "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)


if __name__ == "__main__":
    main()
