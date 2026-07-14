"""Build Archive City v1 as an original, lightweight five-district composition.

The city is a procedural world assembly fallback.  It deliberately uses no real
logos, facades, or landmarks; its district language is driven by the Archive
layout and the non-literal visual-direction report.
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
    parser.add_argument('--output-blend', required=True)
    parser.add_argument('--output-glb', required=True)
    parser.add_argument('--preview', required=True)
    parser.add_argument('--screenshots-dir')
    return parser.parse_args(values)


def make_material(name, color, metallic=0.0, roughness=.55, emission=None):
    value = bpy.data.materials.new(name)
    value.diffuse_color = (*color, 1.0)
    value.use_nodes = True
    shader = value.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1.0)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    if emission:
        shader.inputs['Emission Color'].default_value = (*emission, 1.0)
        shader.inputs['Emission Strength'].default_value = 1.25
    return value


def cube(name, location, dimensions, mat, parent=None, rotation=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    if rotation:
        obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def cylinder(name, location, radius, depth, mat, parent=None, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def group_for(item):
    group = bpy.data.objects.new(item['instanceId'], None)
    group['assetId'] = item['assetId']
    group['district'] = item['district']
    group['source'] = 'world-proxy-fallback'
    bpy.context.collection.objects.link(group)
    group.location = item['position']
    group.rotation_euler = item['rotation']
    group.scale = item['scale']
    return group


def tower(group, base, glass, dark, height, width, crown=True, accent=None):
    cube('TowerPodium', (0, 2, 0), (width * 1.35, 4, width * 1.2), dark, group)
    cube('TowerGlassBody', (0, 4 + height / 2, 0), (width, height, width * .78), glass, group)
    for x in (-width * .42, width * .42):
        cube('TowerVerticalFin', (x, 4 + height / 2, 0), (.3, height * .96, width * .9), base, group)
    if crown:
        cube('TowerCrown', (0, height + 7, 0), (width * .72, 2.2, width * .62), base, group)
    if accent:
        cube('TowerSignal', (0, height + 8.4, 0), (width * .28, .3, width * .28), accent, group)


def archiveos_form(group, item, mats):
    ident = item['instanceId']
    if 'control' in ident:
        tower(group, mats['cyan'], mats['glass'], mats['dark'], 42, 12, True, mats['white'])
        cube('ControlCanopy', (0, 3.2, 9), (19, .7, 8), mats['white'], group)
        for x, z in ((-12, -10), (12, -10), (-12, 10)):
            cube('OperationalAnnex', (x, 6, z), (8, 12, 8), mats['archiveos'], group)
    elif 'ai' in ident:
        tower(group, mats['archiveos'], mats['glass'], mats['dark'], 25, 11, True, mats['cyan'])
        cube('DataHall', (-9, 4, 0), (9, 8, 14), mats['dark'], group)
        for x in (-11, -8, -5): cube('DataLight', (x, 7.2, 0), (.35, .2, 10), mats['cyan'], group)
    else:
        cube('SecurityOperationsCenter', (0, 5, 0), (20, 10, 14), mats['archiveos'], group)
        cube('SecurityFacade', (0, 6, 7.2), (14, 5, .3), mats['glass'], group)
        cylinder('SecurityBeacon', (0, 11.3, 0), 1.0, .6, mats['cyan'], group)


def market_form(group, item, mats):
    ident = item['instanceId']
    if 'commerce' in ident:
        tower(group, mats['market'], mats['market_glass'], mats['dark'], 25, 13, True, mats['violet'])
        cube('CommerceAtrium', (0, 4, 10), (22, 8, 10), mats['glass'], group)
    elif 'orders' in ident:
        cube('OrderCenter', (0, 9, 0), (22, 18, 16), mats['market'], group)
        cube('OrderTerrace', (0, 19, 0), (16, 2, 12), mats['market_glass'], group)
        for x in (-8, -4, 0, 4, 8): cube('OrderFacadeFin', (x, 10, 8.2), (.35, 12, .25), mats['violet'], group)
    else:
        cube('FulfillmentPodium', (0, 5, 0), (25, 10, 18), mats['dark'], group)
        cube('FulfillmentOffice', (-5, 14, 0), (12, 10, 12), mats['market'], group)
        cube('PublicPlazaCanopy', (10, 2.5, 0), (7, .4, 12), mats['market_glass'], group)


def logistics_form(group, item, mats):
    ident = item['instanceId']
    if 'containers' in ident:
        cube('ContainerApron', (0, .2, 0), (32, .4, 24), mats['concrete'], group)
        for row in range(-2, 3):
            for col in range(-2, 3):
                shade = mats['logistics'] if (row + col) % 2 else mats['container_blue']
                cube('ContainerStack', (col * 5, 1.3 + (abs(row) % 2) * 1.4, row * 4), (4.4, 2.4 + (abs(row) % 2) * 2.8, 3.4), shade, group)
    elif 'cold' in ident:
        cube('ColdStorageHall', (0, 6, 0), (30, 12, 20), mats['cold'], group)
        for x in (-10, -5, 0, 5, 10): cube('ColdDockDoor', (x, 2.5, 10.15), (3.2, 4.5, .22), mats['dark'], group)
    else:
        width, depth = (34, 24) if 'distribution' in ident else (28, 18)
        cube('WarehouseHall', (0, 5, 0), (width, 10, depth), mats['logistics'], group)
        cube('WarehouseRoof', (0, 10.5, 0), (width * .93, 1, depth * .9), mats['white'], group)
        for x in range(-int(width / 2) + 3, int(width / 2), 5): cube('LoadingDock', (x, 1.8, depth / 2 + .15), (3.4, 3.2, .25), mats['dark'], group)
        cube('YardOffice', (-width * .32, 7.5, -depth * .58), (8, 10, 6), mats['glass'], group)


def nexus_form(group, item, mats):
    ident = item['instanceId']
    if 'smart' in ident:
        cube('SmartFactoryHall', (0, 6, 0), (30, 12, 24), mats['nexus'], group)
        cube('FactoryRoofMonitor', (0, 13, 0), (20, 2, 8), mats['dark'], group)
        for x in (-10, 0, 10): cylinder('ProcessStack', (x, 17, -5), 1.5, 22, mats['steel'], group)
    elif 'materials' in ident:
        cube('MaterialsPlant', (0, 5, 0), (24, 10, 18), mats['nexus'], group)
        for x, z, radius in ((-9, -5, 3), (0, -5, 3.5), (9, -5, 3)):
            cylinder('StorageTank', (x, radius, z), radius, radius * 2, mats['steel'], group)
    elif 'quality' in ident:
        cube('QualityFacility', (0, 6, 0), (22, 12, 17), mats['white'], group)
        cube('QualityWindowBand', (0, 8, 8.6), (18, 3, .22), mats['glass'], group)
    else:
        cube('MaintenanceBay', (0, 4, 0), (24, 8, 18), mats['nexus'], group)
        for x in (-7, 0, 7): cube('MaintenanceDoor', (x, 3.2, 9.1), (4.2, 5.7, .2), mats['dark'], group)
    # A restrained, modular pipe-rack band makes the industrial district legible.
    for x in (-9, -3, 3, 9):
        cube('PipeRackPost', (x, 6, 11), (.35, 12, .35), mats['steel'], group)
    for y in (6, 9): cube('PipeRackRun', (0, y, 11), (21, .35, .35), mats['amber'], group)


def ledger_form(group, item, mats):
    ident = item['instanceId']
    if 'settlement' in ident:
        tower(group, mats['ledger'], mats['ledger_glass'], mats['dark'], 34, 13, True, mats['gold'])
        cube('SettlementAxis', (0, .3, 12), (8, .3, 20), mats['concrete'], group)
    elif 'finance' in ident:
        tower(group, mats['ledger'], mats['ledger_glass'], mats['dark'], 26, 11, True, mats['gold'])
    else:
        cube('AuditCenter', (0, 10, 0), (20, 20, 16), mats['ledger'], group)
        cube('AuditGrid', (0, 11, 8.1), (15, 10, .25), mats['ledger_glass'], group)
        cube('AuditCrown', (0, 21, 0), (13, 2, 10), mats['gold'], group)


def vehicle_form(group, item, mats):
    ident = item['assetId']
    if 'drone' in ident:
        cylinder('DroneBody', (0, 0, 0), .8, .45, mats['vehicle'], group)
        for x, z in ((-1.4, -1.4), (-1.4, 1.4), (1.4, -1.4), (1.4, 1.4)):
            arm = cube('DroneArm', (x / 2, 0, z / 2), (.13, .13, 1.85), mats['dark'], group, rotation=(0, math.atan2(x, z), 0))
            cylinder('DroneRotor', (x, .22, z), .5, .08, mats['dark'], group)
    else:
        cube('VehicleChassis', (0, .9, 0), (3.2, 1.2, 6.2), mats['vehicle'], group)
        cube('VehicleCabin', (0, 1.9, .8), (2.5, 1.35, 2.3), mats['glass'], group)
        for x in (-1.35, 1.35):
            for z in (-2, 2):
                wheel = cylinder('Wheel', (x, .55, z), .62, .38, mats['dark'], group)
                wheel.rotation_euler[2] = math.pi / 2


def infrastructure_form(group, item, mats):
    ident = item['assetId']
    if 'substation' in ident:
        cube('PowerApron', (0, .15, 0), (22, .3, 16), mats['concrete'], group)
        for x in (-6, 0, 6):
            cube('Transformer', (x, 2, 0), (4, 3.7, 5), mats['steel'], group)
            cube('Busbar', (x, 5, 0), (.2, .2, 11), mats['amber'], group)
    elif 'communications' in ident:
        for y, radius in ((4, 2), (10, 1.5), (16, 1.0)):
            cylinder('CommsMast', (0, y, 0), radius, 7, mats['steel'], group)
        cylinder('CommsBeacon', (0, 20, 0), .55, .8, mats['cyan'], group)
    else:
        cube('InfrastructurePad', (0, .11, 0), (10, .22, 10), mats['dark'], group)
        cube('LaneMarking', (0, .24, 0), (.16, .025, 7.2), mats['lane'], group)


def create_form(item, mats):
    group = group_for(item)
    district = item['district']
    if district == 'archiveos': archiveos_form(group, item, mats)
    elif district == 'market': market_form(group, item, mats)
    elif district == 'nexus': nexus_form(group, item, mats)
    elif district == 'logistics': logistics_form(group, item, mats)
    elif district == 'ledger': ledger_form(group, item, mats)
    elif district == 'vehicle': vehicle_form(group, item, mats)
    else: infrastructure_form(group, item, mats)
    return group


def road_link(start, end, mats):
    a, b = Vector(start), Vector(end)
    delta = b - a
    length = max(delta.length, 1)
    center = (a + b) / 2
    road = cube('ArterialRoad', (center.x, .08, center.z), (9.0, .16, length + 4), mats['road'])
    road.rotation_euler[1] = math.atan2(delta.x, delta.z)
    # Short dashed centre line: simple and deliberately not a copied street pattern.
    for factor in (-.28, 0, .28):
        mark = cube('ArterialMark', (0, .18, factor * length), (.18, .03, length * .12), mats['lane'], road)
        mark.location = (0, .18, factor * length)


def add_district_ground(layout, mats):
    for name, bounds in layout['districtBounds'].items():
        low, high = Vector(bounds['min']), Vector(bounds['max'])
        center = (low + high) / 2
        cube('DistrictApron_' + name, (center.x, -.05, center.z), (high.x - low.x, .1, high.z - low.z), mats['district_ground'])
    # Civic square is intentionally clear around the Control Tower.
    cube('ArchiveOS_CivicPlaza', (0, .02, 13), (31, .08, 18), mats['plaza'])
    # Ledger's open southern axis supplies the requested setback/open-space quality.
    cube('Ledger_OpenAxis', (0, .02, -80), (60, .08, 12), mats['plaza'])


def configure_scene():
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    world = bpy.data.worlds.new('ArchiveDaylight')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.045, .09, .12, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = .32
    scene.world = world
    sun_data = bpy.data.lights.new('SoftDaylight', 'SUN')
    sun_data.energy = 2.2
    sun = bpy.data.objects.new('SoftDaylight', sun_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(28), math.radians(-20), math.radians(24))
    for location, energy, size in [((65, 105, 50), 6500, 55), ((-80, 60, -30), 3200, 45)]:
        data = bpy.data.lights.new('CityFill', 'AREA')
        data.energy = energy; data.shape = 'DISK'; data.size = size
        obj = bpy.data.objects.new('CityFill', data); bpy.context.collection.objects.link(obj); obj.location = location
        obj.rotation_euler = (Vector((0, 0, 0)) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def camera_at(name, position, target):
    data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(camera)
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.lens = 48
    return camera


def render(path, position, target):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    camera = camera_at('RenderCamera_' + os.path.basename(path), position, target)
    bpy.context.scene.camera = camera
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)


args = parse_args()
with open(args.layout, encoding='utf-8') as handle:
    layout = json.load(handle)

bpy.ops.wm.read_factory_settings(use_empty=True)
mats = {
    'archiveos': make_material('ArchiveOS_Steel', (.075, .28, .39), .55),
    'cyan': make_material('ArchiveOS_Cyan', (.06, .68, .78), .4, .35, (.03, .28, .34)),
    'market': make_material('Market_Stone', (.34, .19, .45), .3),
    'market_glass': make_material('Market_Glass', (.26, .37, .64), .55, .3, (.08, .06, .2)),
    'violet': make_material('Market_Violet', (.45, .16, .65), .25, .4, (.14, .03, .24)),
    'nexus': make_material('Nexus_Industrial', (.18, .34, .27), .5),
    'logistics': make_material('Logistics_Warehouse', (.42, .33, .24), .25),
    'cold': make_material('ColdStorage_Cladding', (.46, .65, .70), .25),
    'ledger': make_material('Ledger_BlueGray', (.14, .24, .38), .5),
    'ledger_glass': make_material('Ledger_Glass', (.20, .42, .66), .65, .3),
    'gold': make_material('Ledger_Gold', (.7, .48, .12), .5, .35, (.22, .11, .02)),
    'vehicle': make_material('Fleet_Cyan', (.05, .45, .54), .35),
    'white': make_material('Structural_White', (.72, .77, .76), .2),
    'dark': make_material('Structural_Dark', (.045, .06, .075), .2),
    'glass': make_material('Architectural_Glass', (.12, .51, .62), .55, .25, (.02, .12, .16)),
    'steel': make_material('Plant_Steel', (.29, .34, .36), .7),
    'amber': make_material('Utility_Amber', (.73, .33, .05), .35, .35, (.22, .055, .0)),
    'container_blue': make_material('Container_Blue', (.12, .27, .42), .25),
    'concrete': make_material('Concrete', (.29, .32, .31), .05),
    'road': make_material('Asphalt', (.035, .045, .052), .05),
    'lane': make_material('LaneMarking', (.94, .61, .12), .1),
    'plaza': make_material('CivicPlaza', (.23, .30, .32), .12),
    'district_ground': make_material('DistrictGround', (.075, .13, .14), .1),
}
configure_scene()
cube('CityGround', (0, -.18, 0), (240, .3, 240), make_material('Ground', (.028, .06, .075)))
add_district_ground(layout, mats)
for instance in layout['instances']:
    create_form(instance, mats)
nodes = {node['id']: node for node in layout['roadGraph']['nodes']}
for from_id, to_id in layout['roadGraph']['edges']:
    road_link(nodes[from_id]['position'], nodes[to_id]['position'], mats)

render(args.preview, (132, 112, 138), (0, 5, 0))
if args.screenshots_dir:
    viewpoints = {
        'archiveos-overview.png': ((44, 38, 44), (0, 9, 3)),
        'market-overview.png': ((-91, 40, 30), (-56, 7, 0)),
        'nexus-overview.png': ((-44, 36, 98), (0, 8, 53)),
        'logistics-overview.png': ((108, 38, 43), (62, 5, -5)),
        'ledger-overview.png': ((44, 38, -110), (0, 9, -63)),
        'city-overview.png': ((132, 112, 138), (0, 5, 0)),
    }
    for filename, (position, target) in viewpoints.items():
        render(os.path.join(args.screenshots_dir, filename), position, target)

os.makedirs(os.path.dirname(args.output_blend), exist_ok=True)
os.makedirs(os.path.dirname(args.output_glb), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=args.output_blend)
bpy.ops.export_scene.gltf(filepath=args.output_glb, export_format='GLB', export_materials='EXPORT', export_apply=True, export_extras=True)
print('ARCHIVE_WORLD_CITY_BUILT=' + args.output_glb)
