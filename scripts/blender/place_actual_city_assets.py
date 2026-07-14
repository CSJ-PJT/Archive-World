"""Place existing processed master GLBs into the existing Archive City layout.

This is a scene-assembly operation only: it imports existing master GLBs, keeps
the prior whitebox in a hidden debug collection, and saves the .blend.  It does
not export or modify GLBs, LODs, manifests, or source assets.
"""
import argparse
import json
import math
import os
import sys

import bpy
from mathutils import Vector


def parse_args():
    values = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--layout', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--repo', required=True)
    return parser.parse_args(values)


# Incoming candidates are deliberately not imported here. These substitutions
# point only to the 45 processed master assets.
SUBSTITUTES = {
    'security-gate-road-lane-v1': 'building-archiveos2-a614889b',
    'cold-storage-loading-dock-v1': 'building-archive-2-2fe57f23',
    'container-yard-modular-v1': 'building-1-d57f1be7',
    'power-substation-compact-v1': 'building-7-d09a344b',
    'communications-tower-compact-v1': 'building-8-9034e896',
    'vehicle-forklift-industrial-v1': 'vehicle-asset-535bcba9',
    'vehicle-agv-platform-v1': 'vehicle-2-0ff0d303',
    'vehicle-inspection-drone-v1': 'vehicle-3-234d82b4',
}


def move_to_collection(obj, collection):
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def mesh_bounds(objects):
    points = []
    for obj in objects:
        if obj.type == 'MESH':
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        return Vector((0, 0, 0)), Vector((1, 1, 1))
    low = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    high = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return low, high


def target_footprint(item):
    district = item['district']
    if district == 'archiveos': return 28 if 'control' in item['instanceId'] else 20
    if district == 'market': return 24
    if district == 'nexus': return 28
    if district == 'logistics': return 34
    if district == 'ledger': return 26
    if district == 'vehicle': return 7
    return 13


def import_asset(path, item, asset_id, collection):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    imported = [obj for obj in bpy.data.objects if obj not in before]
    for obj in imported:
        move_to_collection(obj, collection)
        obj['district'] = item['district']; obj['instanceId'] = item['instanceId']; obj['assetId'] = asset_id
    roots = [obj for obj in imported if obj.parent not in imported]
    low, high = mesh_bounds(imported)
    span = high - low
    footprint = max(span.x, span.y, .001)
    scale = target_footprint(item) / footprint
    root = bpy.data.objects.new('Instance_' + item['instanceId'], None)
    collection.objects.link(root)
    for obj in roots:
        obj.parent = root
    x, _, z = item['position']
    root.location = (x, z, -low.z * scale)
    root.scale = (scale, scale, scale)
    root.rotation_euler[2] = item['rotation'][1]
    root['district'] = item['district']; root['instanceId'] = item['instanceId']; root['assetId'] = asset_id
    return root


def import_road(path, start, end, collection):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    imported = [obj for obj in bpy.data.objects if obj not in before]
    for obj in imported:
        move_to_collection(obj, collection); obj['district'] = 'infrastructure'; obj['instanceId'] = 'actual-road'
    roots = [obj for obj in imported if obj.parent not in imported]
    low, high = mesh_bounds(imported); span = high - low
    delta = Vector((end[0]-start[0], end[2]-start[2], 0)); length = max(delta.length, 1)
    center = ((start[0]+end[0])/2, (start[2]+end[2])/2)
    root = bpy.data.objects.new('Road_' + str(round(center[0])) + '_' + str(round(center[1])), None); collection.objects.link(root)
    for obj in roots: obj.parent = root
    # GLB road modules are stretched only as scene instances; source geometry remains untouched.
    root.scale = (10 / max(span.x, .01), length / max(span.y, .01), 10 / max(span.z, .01))
    root.location = (center[0], center[1], -low.z * root.scale.z)
    root.rotation_euler[2] = math.atan2(-(end[0]-start[0]), end[2]-start[2])
    root['district'] = 'infrastructure'; root['instanceId'] = 'actual-road'


def make_ground(collection, low, high):
    bpy.ops.mesh.primitive_plane_add(size=2, location=((low.x+high.x)/2, (low.y+high.y)/2, -.02))
    ground = bpy.context.object; ground.name = 'CityGround_RenderSurface'; ground.scale = ((high.x-low.x+50)/2, (high.y-low.y+50)/2, 1)
    ground.data.materials.append(bpy.data.materials.new('CityGroundMaterial'))
    material = ground.data.materials[0]; material.diffuse_color = (.24,.28,.29,1); material.use_nodes = True
    material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.24,.28,.29,1)
    move_to_collection(ground, collection); ground['district'] = 'infrastructure'; ground['instanceId'] = 'ground'


def actual_bounds(collection):
    return mesh_bounds([obj for obj in collection.objects if obj.type == 'MESH'])


def camera_for(name, collection, district=None):
    objects = [obj for obj in collection.objects if obj.type == 'MESH' and (district is None or obj.get('district') == district)]
    low, high = mesh_bounds(objects); center = (low+high)/2; span = max((high-low).x, (high-low).y, (high-low).z)
    distance = max(55, span * 1.28)
    data = bpy.data.cameras.new(name); camera = bpy.data.objects.new(name, data); bpy.context.collection.objects.link(camera)
    camera.location = center + Vector((distance, distance, distance*.78)); camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler(); data.lens = 32
    camera['district'] = district or 'city'; camera['distance'] = round(distance, 2); camera['fovDegrees'] = round(math.degrees(data.angle), 2)
    return camera


args = parse_args()
with open(args.layout, encoding='utf-8') as handle: layout = json.load(handle)
with open(args.manifest, encoding='utf-8') as handle: manifest = json.load(handle)
source_file = bpy.data.filepath
if not source_file: raise RuntimeError('Load archive-city-v1.blend before placing assets.')
asset_paths = {asset['assetId']: os.path.join(args.repo, asset['master']) for asset in manifest['assets'] if asset.get('master')}

debug = bpy.data.collections.get('Whitebox_Debug') or bpy.data.collections.new('Whitebox_Debug')
if debug.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(debug)
for obj in list(bpy.context.scene.objects):
    if obj.name.startswith('Camera_') or obj.name in {'DaylightSun', 'SkyFill'}: continue
    move_to_collection(obj, debug); obj.hide_render = True
debug.hide_render = True

actual = bpy.data.collections.get('Actual_GLBS') or bpy.data.collections.new('Actual_GLBS')
if actual.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(actual)
for obj in list(actual.objects): bpy.data.objects.remove(obj, do_unlink=True)

for item in layout['instances']:
    resolved = SUBSTITUTES.get(item['assetId'], item['assetId'])
    path = asset_paths.get(resolved)
    if not path or not os.path.isfile(path):
        print('SKIPPED_NO_MASTER=' + item['instanceId']); continue
    import_asset(path, item, resolved, actual)

road_path = asset_paths['road-meshy-ai-divided-highway-0713093526-texture-b5202be0']
nodes = {node['id']: node['position'] for node in layout['roadGraph']['nodes']}
for left, right in layout['roadGraph']['edges']:
    import_road(road_path, nodes[left], nodes[right], actual)

low, high = actual_bounds(actual); make_ground(actual, low, high)
world = bpy.data.worlds.get('ActualAssetDaylight') or bpy.data.worlds.new('ActualAssetDaylight'); world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.18,.27,.32,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = .55; bpy.context.scene.world = world
for obj in list(bpy.data.objects):
    if obj.name.startswith('ActualCamera') or obj.name.startswith('ActualSun') or obj.name.startswith('ActualFill'): bpy.data.objects.remove(obj, do_unlink=True)
sun_data = bpy.data.lights.new('ActualSun','SUN'); sun_data.energy=3.0; sun=bpy.data.objects.new('ActualSun',sun_data); bpy.context.collection.objects.link(sun); sun.rotation_euler=(math.radians(28),math.radians(-16),math.radians(34))
fill_data = bpy.data.lights.new('ActualFill','AREA'); fill_data.energy=7000; fill_data.size=110; fill=bpy.data.objects.new('ActualFill',fill_data); bpy.context.collection.objects.link(fill); fill.location=(100,70,160); fill.rotation_euler=(Vector((0,0,0))-fill.location).to_track_quat('-Z','Y').to_euler()
for district in ('archiveos','market','nexus','logistics','ledger'): camera_for('ActualCamera_'+district, actual, district)
city_camera = camera_for('ActualCamera_city', actual); bpy.context.scene.camera = city_camera
bpy.context.scene.render.engine='BLENDER_EEVEE_NEXT'; bpy.context.scene.render.resolution_x=1600; bpy.context.scene.render.resolution_y=1000; bpy.context.scene.render.resolution_percentage=100
low, high = actual_bounds(actual); print('ACTUAL_CITY_BOUNDS='+str(tuple(round(v,2) for v in low))+'..'+str(tuple(round(v,2) for v in high)))
print('ACTUAL_CITY_CAMERA_DISTANCE='+str(city_camera['distance'])+' FOV='+str(city_camera['fovDegrees']))
bpy.ops.wm.save_as_mainfile(filepath=source_file)
print('ARCHIVE_WORLD_ACTUAL_GLBS_PLACED='+source_file)
