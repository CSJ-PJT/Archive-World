import argparse
import os
import sys
import bpy
from mathutils import Vector

def arguments():
    values = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--size', type=int, required=True)
    parser.add_argument('--transparent', default='true')
    return parser.parse_args(values)

def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

args = arguments()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args.input)

points = []
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        points.extend([obj.matrix_world @ Vector(corner) for corner in obj.bound_box])
if not points:
    raise RuntimeError('Cannot render an asset with no mesh bounds.')
minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
center = (minimum + maximum) / 2
radius = max((maximum - minimum).length / 2, 0.1)

camera_data = bpy.data.cameras.new('ArchiveWorldCamera')
camera = bpy.data.objects.new('ArchiveWorldCamera', camera_data)
bpy.context.collection.objects.link(camera)
camera.location = center + Vector((radius * 2.2, -radius * 2.2, radius * 1.5))
camera.data.lens = 50
look_at(camera, center)
bpy.context.scene.camera = camera

for location, energy, size in [
    (center + Vector((radius * 3, -radius * 2, radius * 4)), 1200, radius * 2),
    (center + Vector((-radius * 3, -radius, radius * 2)), 700, radius * 2)
]:
    light_data = bpy.data.lights.new('ArchiveWorldLight', type='AREA')
    light_data.energy = energy
    light_data.shape = 'DISK'
    light_data.size = size
    light = bpy.data.objects.new('ArchiveWorldLight', light_data)
    bpy.context.collection.objects.link(light)
    light.location = location
    look_at(light, center)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = args.size
scene.render.resolution_y = args.size
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'WEBP' if os.path.splitext(args.output)[1].lower() == '.webp' else 'PNG'
scene.render.film_transparent = args.transparent.lower() == 'true'
scene.render.filepath = args.output
scene.render.image_settings.color_mode = 'RGBA' if scene.render.film_transparent else 'RGB'
bpy.ops.render.render(write_still=True)
print('Preview written to ' + args.output)
