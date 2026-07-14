"""Render fixed Archive City v1 camera views from an existing .blend only.

This script never saves the loaded blend and never exports geometry.  It creates
temporary cameras, writes PNGs, then removes those temporary cameras.
"""
import argparse
import os
import shutil
import sys

import bpy
from mathutils import Vector


def parse_args():
    values = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--city-preview', required=True)
    return parser.parse_args(values)


def district_for(obj):
    current = obj
    while current:
        if 'district' in current:
            return current['district']
        current = current.parent
    return None


def bounds_for(district=None):
    points = []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or obj.hide_render or (district and district_for(obj) != district):
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        return Vector((0, 0, 0)), 50.0
    minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return (minimum + maximum) / 2, max((maximum - minimum).x, (maximum - minimum).y, (maximum - minimum).z)


def render_view(name, path, district=None):
    target, span = bounds_for(district)
    distance = max(span * 1.45, 42.0)
    position = target + Vector((distance, distance * .86, distance))
    camera_data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.lens = 30
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)


args = parse_args()
os.makedirs(args.output_dir, exist_ok=True)
os.makedirs(os.path.dirname(args.city_preview), exist_ok=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Temporary render lighting only; the loaded .blend is not saved.
world = scene.world
if world and world.use_nodes:
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = .8
sun_data = bpy.data.lights.new('RenderSun', 'SUN'); sun_data.energy = 4.2
sun = bpy.data.objects.new('RenderSun', sun_data); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (.55, -.35, .4)
fill_data = bpy.data.lights.new('RenderFill', 'AREA'); fill_data.energy = 12000; fill_data.shape = 'DISK'; fill_data.size = 100
fill = bpy.data.objects.new('RenderFill', fill_data); bpy.context.collection.objects.link(fill)
center, city_span = bounds_for(); fill.location = center + Vector((city_span, city_span * 1.2, city_span * .6)); fill.rotation_euler = (center - fill.location).to_track_quat('-Z', 'Y').to_euler()

views = {
    'archiveos-overview.png': 'archiveos',
    'market-overview.png': 'market',
    'nexus-overview.png': 'nexus',
    'logistics-overview.png': 'logistics',
    'ledger-overview.png': 'ledger',
    'city-overview.png': None,
}
for filename, district in views.items():
    render_view('Render_' + filename, os.path.join(args.output_dir, filename), district)

shutil.copyfile(os.path.join(args.output_dir, 'city-overview.png'), args.city_preview)
bpy.data.objects.remove(sun, do_unlink=True)
bpy.data.objects.remove(fill, do_unlink=True)
print('ARCHIVE_WORLD_RENDERED=7')
