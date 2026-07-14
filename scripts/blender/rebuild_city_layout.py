"""Rebuild only the Archive City layout inside an already existing .blend.

No GLB, LOD, manifest, or source asset is written by this script.  It creates
scene-local placement proxies, roads, cameras, ground, and daylight, then saves
the loaded blend back to its original path.
"""
import argparse
import json
import math
import sys

import bpy
from mathutils import Vector


def arguments():
    values = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--layout', required=True)
    return parser.parse_args(values)


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def mat(name, rgb, metal=.15, rough=.55, emission=0):
    value = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    value.use_nodes = True
    node = value.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*rgb, 1)
    node.inputs['Metallic'].default_value = metal
    node.inputs['Roughness'].default_value = rough
    node.inputs['Emission Color'].default_value = (*rgb, 1)
    node.inputs['Emission Strength'].default_value = emission
    return value


def tag(obj, district, instance):
    obj['district'] = district
    obj['instanceId'] = instance
    return obj


def box(name, loc, dims, material, district='infrastructure', instance='scene', rot=0):
    # Layout is Y-up; Blender authoring space is Z-up.
    bpy.ops.mesh.primitive_cube_add(location=(loc[0], loc[2], loc[1]), rotation=(0, 0, rot))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (dims[0], dims[2], dims[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return tag(obj, district, instance)


def cyl(name, loc, radius, depth, material, district, instance):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth, location=(loc[0], loc[2], loc[1]))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return tag(obj, district, instance)


def add_structure(item, m):
    x, _, z = item['position']; district = item['district']; ident = item['instanceId']
    def b(name, dx, dy, dz, sx, sy, sz, material): return box(name, (x+dx, dy, z+dz), (sx, sy, sz), material, district, ident)
    def c(name, dx, dy, dz, radius, height, material): return cyl(name, (x+dx, dy, z+dz), radius, height, material, district, ident)
    if district == 'archiveos':
        if 'control' in ident:
            b('ControlTowerPodium', 0, 2.5, 0, 26, 5, 26, m['dark']); b('ControlTower', 0, 29, 0, 14, 52, 14, m['glass']); b('ControlCrown', 0, 56, 0, 17, 2, 17, m['cyan'])
            for dx in (-6.7, 6.7): b('ControlFin', dx, 29, 0, .4, 51, 15, m['cyan'])
        elif 'ai' in ident:
            b('DataPodium', 0, 3, 0, 24, 6, 18, m['dark']); b('DataCenter', 0, 15, 0, 17, 20, 14, m['archiveos']); b('DataLightBand', 0, 18, 7.1, 15, .4, .25, m['cyan'])
        else:
            b('SecurityCenter', 0, 5, 0, 24, 10, 16, m['archiveos']); b('SecurityFacade', 0, 6, 8.1, 17, 5, .3, m['glass'])
    elif district == 'market':
        if 'commerce' in ident:
            b('CommercePodium', 0, 3, 0, 28, 6, 24, m['dark']); b('CommerceTower', 0, 20, 0, 17, 34, 15, m['market']); b('CommerceCrown', 0, 38, 0, 13, 2, 11, m['violet'])
        elif 'orders' in ident:
            b('OrderCenter', 0, 10, 0, 26, 20, 18, m['market']); b('OrderRoof', 0, 21, 0, 19, 2, 13, m['glass'])
        else:
            b('MarketFulfillment', 0, 6, 0, 28, 12, 20, m['dark']); b('MarketPlazaCanopy', 12, 3, 0, 7, .5, 13, m['glass'])
    elif district == 'nexus':
        b('IndustrialHall', 0, 7, 0, 30, 14, 24, m['nexus'])
        if 'smart' in ident or 'materials' in ident:
            for dx in (-9, 0, 9): c('ProcessTower', dx, 20, -5, 1.8, 26, m['steel'])
        if 'materials' in ident:
            for dx in (-7, 2, 10): c('StorageTank', dx, 3.5, 7, 3.2, 7, m['steel'])
        for dx in (-10, -3, 4, 11): b('PipeRackPost', dx, 6, 12, .35, 12, .35, m['steel'])
        for y in (6, 9): b('PipeRackRun', 0, y, 12, 24, .35, .35, m['amber'])
    elif district == 'logistics':
        if 'containers' in ident:
            b('ContainerApron', 0, .2, 0, 34, .4, 28, m['concrete'])
            for row in range(-2, 3):
                for col in range(-2, 3): b('Container', col*5, 1.4, row*4, 4.4, 2.6, 3.4, m['logistics'] if (row+col)%2 else m['blue'])
        else:
            w, d = (36, 26) if 'distribution' in ident else ((30, 20) if 'terminal' in ident else (28, 20))
            b('Warehouse', 0, 6, 0, w, 12, d, m['logistics']); b('WarehouseRoof', 0, 12.4, 0, w*.92, .8, d*.9, m['white'])
            for dx in range(-int(w/2)+3, int(w/2), 5): b('DockDoor', dx, 2.4, d/2+.15, 3.2, 4.4, .25, m['dark'])
    elif district == 'ledger':
        height = 42 if 'settlement' in ident else (33 if 'finance' in ident else 25)
        b('LedgerPodium', 0, 3, 0, 23, 6, 20, m['dark']); b('LedgerTower', 0, 6+height/2, 0, 14, height, 12, m['ledger']); b('LedgerCrown', 0, height+7, 0, 11, 2, 9, m['gold'])
    elif district == 'vehicle':
        b('VehicleBody', 0, 1, 0, 3.2, 1.4, 6.4, m['vehicle']); b('VehicleCab', 0, 2, .9, 2.5, 1.4, 2.1, m['glass'])
        for dx in (-1.25, 1.25):
            for dz in (-2, 2): c('Wheel', dx, .55, dz, .55, .36, m['dark'])
    else:
        b('UtilityPad', 0, .2, 0, 14, .4, 14, m['concrete']); c('CommsOrPower', 0, 5, 0, 2, 10, m['steel'])


def road(a, b, m):
    start, end = Vector(a), Vector(b); delta = end - start; length = delta.length
    center = (start + end) / 2
    obj = box('ArterialRoad', (center.x, .12, center.z), (11, .24, length+7), m['road'], 'infrastructure', 'road-network')
    obj.rotation_euler[2] = math.atan2(-delta.x, delta.z)
    for fraction in (-.28, 0, .28):
        mark = box('LaneDash', (center.x, .27, center.z), (.22, .04, max(3, length*.12)), m['lane'], 'infrastructure', 'road-network')
        mark.rotation_euler[2] = obj.rotation_euler[2]; mark.location += Vector((delta.x, delta.z, delta.y)).normalized() * (fraction * length)


def bounds(district=None):
    points = []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or (district and obj.get('district') != district): continue
        points += [obj.matrix_world @ Vector(point) for point in obj.bound_box]
    low = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    high = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return (low + high)/2, max((high-low).x, (high-low).y, (high-low).z)


def camera(name, district=None):
    target, span = bounds(district); distance = max(58, span * 1.55)
    data = bpy.data.cameras.new(name); obj = bpy.data.objects.new(name, data); bpy.context.collection.objects.link(obj)
    obj.location = target + Vector((distance, distance, distance*.82)); obj.rotation_euler = (target-obj.location).to_track_quat('-Z','Y').to_euler(); data.lens = 38
    obj['district'] = district or 'city'; obj['distance'] = round(distance, 2); obj['fovDegrees'] = round(math.degrees(data.angle), 2)
    return obj


args = arguments()
with open(args.layout, encoding='utf-8') as handle: layout = json.load(handle)
source_file = bpy.data.filepath
if not source_file: raise RuntimeError('An existing .blend must be loaded before rebuilding its layout.')
clear_scene()
m = {
    'archiveos': mat('ArchiveOS', (.08,.30,.42), .4), 'cyan': mat('Cyan', (.06,.70,.78), .3, .35, .25),
    'market': mat('Market', (.31,.18,.44), .3), 'violet': mat('Violet', (.48,.18,.68), .2, .4, .2),
    'nexus': mat('Nexus', (.19,.35,.27), .45), 'logistics': mat('Logistics', (.42,.34,.26), .25),
    'ledger': mat('Ledger', (.14,.25,.39), .5), 'gold': mat('Gold', (.70,.48,.13), .5, .35, .18),
    'glass': mat('Glass', (.13,.56,.66), .55, .24, .1), 'steel': mat('Steel', (.34,.39,.41), .65),
    'amber': mat('Amber', (.78,.34,.05), .25, .4, .25), 'vehicle': mat('Vehicle', (.05,.52,.61), .3),
    'dark': mat('Dark', (.035,.055,.07), .2), 'white': mat('White', (.72,.77,.76), .15), 'blue': mat('ContainerBlue', (.12,.30,.48), .25),
    'concrete': mat('Concrete', (.28,.32,.32), .05), 'road': mat('Road', (.045,.055,.06), .05), 'lane': mat('Lane', (.92,.64,.13), .1),
}
all_low = Vector((min(v['min'][0] for v in layout['districtBounds'].values()), 0, min(v['min'][2] for v in layout['districtBounds'].values())))
all_high = Vector((max(v['max'][0] for v in layout['districtBounds'].values()), 0, max(v['max'][2] for v in layout['districtBounds'].values())))
center = (all_low + all_high) / 2; size = all_high - all_low
box('CityGround', (center.x, -.25, center.z), (size.x+44, .5, size.z+44), m['concrete'], 'infrastructure', 'ground')
for district, area in layout['districtBounds'].items():
    low, high = Vector(area['min']), Vector(area['max']); midpoint = (low+high)/2
    box('DistrictPad_'+district, (midpoint.x, -.02, midpoint.z), (high.x-low.x, .08, high.z-low.z), m['concrete'], district, 'district-pad')
for item in layout['instances']: add_structure(item, m)
nodes = {node['id']: node['position'] for node in layout['roadGraph']['nodes']}
for left, right in layout['roadGraph']['edges']: road(nodes[left], nodes[right], m)
for node in nodes.values(): cyl('RoadIntersection', (node[0], .14, node[2]), 7.2, .25, m['road'], 'infrastructure', 'road-network')

world = bpy.data.worlds.new('ArchiveDaylight'); world.use_nodes = True; world.node_tree.nodes['Background'].inputs['Color'].default_value = (.12,.22,.28,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = .42; bpy.context.scene.world = world
sun_data = bpy.data.lights.new('DaylightSun','SUN'); sun_data.energy = 2.8; sun = bpy.data.objects.new('DaylightSun',sun_data); bpy.context.collection.objects.link(sun); sun.rotation_euler=(math.radians(28),math.radians(-18),math.radians(32))
fill_data = bpy.data.lights.new('SkyFill','AREA'); fill_data.energy = 5200; fill_data.size=95; fill=bpy.data.objects.new('SkyFill',fill_data); bpy.context.collection.objects.link(fill); fill.location=(80,70,150); fill.rotation_euler=(Vector((0,0,0))-fill.location).to_track_quat('-Z','Y').to_euler()
for district in ('archiveos','market','nexus','logistics','ledger'): camera('Camera_'+district, district)
city_camera = camera('Camera_city')
bpy.context.scene.camera = city_camera
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'; bpy.context.scene.render.resolution_x=1600; bpy.context.scene.render.resolution_y=1000; bpy.context.scene.render.resolution_percentage=100
city_center, city_span = bounds(); print('CITY_BOUNDS_CENTER='+str(tuple(round(v,2) for v in city_center))+' SPAN='+str(round(city_span,2)))
for district in ('archiveos','market','nexus','logistics','ledger'): print('CAMERA_'+district.upper()+'_DISTANCE='+str(bpy.data.objects['Camera_'+district]['distance']))
print('CAMERA_CITY_DISTANCE='+str(city_camera['distance'])+' FOV='+str(city_camera['fovDegrees']))
bpy.ops.wm.save_as_mainfile(filepath=source_file)
print('ARCHIVE_WORLD_LAYOUT_REBUILT='+source_file)
