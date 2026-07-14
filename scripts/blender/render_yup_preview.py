import argparse
import os
import sys
import bpy
from mathutils import Vector


def args():
    values = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--size', type=int, default=768)
    return parser.parse_args(values)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


options = args()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=options.input)
points = [obj.matrix_world @ Vector(corner) for obj in bpy.context.scene.objects if obj.type == 'MESH' for corner in obj.bound_box]
if not points:
    raise RuntimeError('Cannot render asset without meshes')
minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
center = (minimum + maximum) * 0.5
radius = max((maximum - minimum).length * 0.5, 0.25)
camera_data = bpy.data.cameras.new('PreviewCamera')
camera = bpy.data.objects.new('PreviewCamera', camera_data)
bpy.context.collection.objects.link(camera)
camera.location = center + Vector((radius * 2.0, radius * 3.4, radius * 2.0))
camera.data.lens = 52
look_at(camera, center)
bpy.context.scene.camera = camera
for location, energy, size in [
    (center + Vector((radius * 2.8, radius * 3.6, radius * 1.5)), 1100, radius * 2.0),
    (center + Vector((-radius * 2.5, radius * 1.8, radius * 2.4)), 650, radius * 1.8),
]:
    data = bpy.data.lights.new('PreviewLight', 'AREA')
    data.energy, data.shape, data.size = energy, 'DISK', size
    light = bpy.data.objects.new('PreviewLight', data)
    bpy.context.collection.objects.link(light)
    light.location = location
    look_at(light, center)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = options.size
scene.render.resolution_y = options.size
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.film_transparent = False
if scene.world is None:
    scene.world = bpy.data.worlds.new('PreviewWorld')
scene.world.color = (0.92, 0.92, 0.92)
scene.render.filepath = options.output
bpy.ops.render.render(write_still=True)
print('Preview written to ' + options.output)
