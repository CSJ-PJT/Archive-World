"""Create original, modular Archive-World infrastructure candidates.

These assets are generated only into the configured Incoming Models directory.
They intentionally do not touch immutable Meshy sources or any manifest.
"""
import bpy
import math
import os
import sys
from mathutils import Vector

ROAD_WIDTH = 1.7013869881629944
ROAD_THICKNESS = 0.2274320051074028
ROAD_LENGTH = 1.8997430205345154


def cli_args():
    return sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0


def material(name, color, metallic=0.0, roughness=0.5):
    value = bpy.data.materials.new(name)
    value.diffuse_color = (*color, 1.0)
    value.use_nodes = True
    bsdf = value.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return value


def box(name, location, dimensions, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new('EdgeBevel', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 2
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def cylinder(name, location, radius, depth, mat, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def mesh_object(name, vertices, faces, mat):
    data = bpy.data.meshes.new(name + 'Mesh')
    data.from_pydata(vertices, [], faces)
    data.materials.append(mat)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return obj


def empty(name, location, direction):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = 'ARROWS'
    obj.empty_display_size = 0.16
    obj.location = location
    obj['archiveWorldRole'] = 'roadConnector'
    obj['forward'] = direction
    bpy.context.collection.objects.link(obj)


def export_glb(out_dir, filename):
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, filename)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        export_materials='EXPORT',
        export_apply=True,
        export_extras=True,
        export_yup=True,
    )
    print('ARCHIVE_WORLD_CREATED=' + filepath)


def create_curve(out_dir):
    clean_scene()
    asphalt = material('Asphalt', (0.055, 0.06, 0.07), roughness=0.86)
    marking = material('LaneMarking', (0.96, 0.72, 0.08), roughness=0.5)
    curb = material('Curb', (0.42, 0.45, 0.48), roughness=0.75)
    segments = 32
    inner, outer = 0.1493, 1.8507
    shift = Vector((-0.5, 0.0, 0.5))
    top, bottom = 0.0, -ROAD_THICKNESS
    vertices, faces = [], []
    for index in range(segments + 1):
        angle = -math.pi / 2 + (math.pi / 2) * index / segments
        for y in (top, bottom):
            for radius in (inner, outer):
                vertices.append((radius * math.cos(angle) + shift.x, y, radius * math.sin(angle) + shift.z))
    for index in range(segments):
        a = index * 4; b = (index + 1) * 4
        faces.extend([
            (a, a + 1, b + 1, b),             # top road surface
            (a + 2, b + 2, b + 3, a + 3),     # bottom surface
            (a, b, b + 2, a + 2),             # inner edge
            (a + 1, a + 3, b + 3, b + 1),     # outer edge
        ])
    faces.extend([(0, 2, 3, 1), (segments * 4, segments * 4 + 1, segments * 4 + 3, segments * 4 + 2)])
    mesh_object('RoadCurve90', vertices, faces, asphalt)
    # Curved yellow center marking, placed very slightly above the asphalt to avoid z-fighting.
    stripe_radius = (inner + outer) * 0.5
    stripe_width = 0.07
    stripe_vertices, stripe_faces = [], []
    for index in range(segments + 1):
        angle = -math.pi / 2 + (math.pi / 2) * index / segments
        for radius in (stripe_radius - stripe_width / 2, stripe_radius + stripe_width / 2):
            stripe_vertices.append((radius * math.cos(angle) + shift.x, 0.003, radius * math.sin(angle) + shift.z))
    for index in range(segments):
        a = index * 2; stripe_faces.append((a, a + 1, a + 3, a + 2))
    mesh_object('CenterMarking', stripe_vertices, stripe_faces, marking)
    # Low outside curbs provide a readable, compatible edge without changing connector widths.
    for radius in (inner, outer):
        for index in range(segments):
            angle = -math.pi / 2 + (math.pi / 2) * (index + 0.5) / segments
            length = radius * (math.pi / 2) / segments + 0.02
            item = box('Curb', (radius * math.cos(angle) + shift.x, 0.035, radius * math.sin(angle) + shift.z), (0.055, 0.07, length), curb, 0.01)
            item.rotation_euler[1] = -angle
    empty('Connector_A', (-0.5, 0.0, -0.5), [0.0, 0.0, -1.0])
    empty('Connector_B', (0.5, 0.0, 0.5), [1.0, 0.0, 0.0])
    export_glb(out_dir, 'road-curved-modular-90-v2.glb')


def create_ramp(out_dir):
    clean_scene()
    asphalt = material('Asphalt', (0.055, 0.06, 0.07), roughness=0.86)
    marking = material('LaneMarking', (0.96, 0.72, 0.08), roughness=0.5)
    rise = 0.65; half_w = ROAD_WIDTH / 2; half_l = ROAD_LENGTH / 2; bottom = -ROAD_THICKNESS
    vertices = [(-half_w, bottom, -half_l), (half_w, bottom, -half_l), (half_w, bottom + rise, half_l), (-half_w, bottom + rise, half_l),
                (-half_w, 0, -half_l), (half_w, 0, -half_l), (half_w, rise, half_l), (-half_w, rise, half_l)]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh_object('RoadRamp', vertices, faces, asphalt)
    stripe = box('CenterMarking', (0, rise / 2 + 0.004, 0), (0.07, 0.01, ROAD_LENGTH * 0.85), marking)
    stripe.rotation_euler[0] = math.atan2(rise, ROAD_LENGTH)
    empty('Connector_Low', (0, 0, -half_l), [0.0, 0.0, -1.0])
    empty('Connector_High', (0, rise, half_l), [0.0, 0.0, 1.0])
    export_glb(out_dir, 'road-elevated-ramp-straight-v1.glb')


def create_barrier(out_dir):
    clean_scene()
    steel = material('GalvanizedSteel', (0.32, 0.36, 0.39), metallic=0.72, roughness=0.34)
    yellow = material('SafetyYellow', (0.98, 0.58, 0.02), metallic=0.05, roughness=0.42)
    for x in (-0.8, 0.0, 0.8):
        cylinder('BarrierPost', (x, 0.36, 0), 0.055, 0.72, steel)
        box('Reflector', (x, 0.50, 0.055), (0.13, 0.12, 0.025), yellow, 0.01)
    box('GuardRail', (0, 0.62, 0), (ROAD_LENGTH, 0.12, 0.08), steel, 0.025)
    box('GuardRailLower', (0, 0.34, 0), (ROAD_LENGTH, 0.09, 0.07), steel, 0.02)
    export_glb(out_dir, 'roadside-safety-barrier-v1.glb')


def create_signal(out_dir):
    clean_scene()
    pole = material('SignalPole', (0.08, 0.09, 0.1), metallic=0.75, roughness=0.32)
    red = material('SignalRed', (0.92, 0.03, 0.02), metallic=0.15, roughness=0.25)
    amber = material('SignalAmber', (1.0, 0.52, 0.02), metallic=0.15, roughness=0.25)
    green = material('SignalGreen', (0.02, 0.72, 0.17), metallic=0.15, roughness=0.25)
    lamp = material('LampGlass', (0.75, 0.82, 0.85), metallic=0.15, roughness=0.15)
    cylinder('SignalBase', (0, 0.06, 0), 0.24, 0.12, pole)
    cylinder('SignalPole', (0, 1.55, 0), 0.075, 3.0, pole)
    box('SignalArm', (0.72, 2.85, 0), (1.5, 0.09, 0.09), pole, 0.02)
    box('SignalHousing', (1.42, 2.5, 0), (0.32, 0.74, 0.28), pole, 0.04)
    for y, mat in ((2.72, red), (2.50, amber), (2.28, green)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.085, location=(1.42, y, -0.145))
        bpy.context.object.name = 'SignalLamp'
        bpy.context.object.data.materials.append(mat)
    cylinder('StreetLightPole', (-0.62, 2.05, 0), 0.055, 4.1, pole)
    box('StreetLightArm', (-0.36, 3.93, 0), (0.58, 0.06, 0.06), pole, 0.01)
    box('StreetLightHead', (-0.06, 3.86, 0), (0.23, 0.08, 0.16), lamp, 0.025)
    export_glb(out_dir, 'streetlight-traffic-signal-v1.glb')


def create_security_gate(out_dir):
    clean_scene()
    dark = material('GateSteel', (0.09, 0.11, 0.13), metallic=0.75, roughness=0.3)
    orange = material('SafetyOrange', (0.98, 0.24, 0.03), roughness=0.42)
    light = material('BarrierWhite', (0.9, 0.91, 0.92), roughness=0.38)
    for x in (-ROAD_WIDTH / 2 - 0.12, ROAD_WIDTH / 2 + 0.12):
        box('GateColumn', (x, 1.25, 0), (0.18, 2.5, 0.24), dark, 0.03)
    box('GateBeam', (0, 2.45, 0), (ROAD_WIDTH + 0.4, 0.18, 0.24), dark, 0.03)
    box('BarrierBase', (-ROAD_WIDTH / 2 + 0.1, 0.21, 0.18), (0.34, 0.42, 0.42), dark, 0.02)
    arm = box('BarrierArm', (0.15, 0.56, 0.18), (ROAD_WIDTH * 0.76, 0.08, 0.08), light, 0.01)
    arm.rotation_euler[1] = -0.35
    box('BarrierStripe', (0.26, 0.56, 0.225), (ROAD_WIDTH * 0.58, 0.09, 0.015), orange)
    export_glb(out_dir, 'security-gate-road-lane-v1.glb')


def create_substation(out_dir):
    clean_scene()
    metal = material('SubstationSteel', (0.28, 0.31, 0.34), metallic=0.8, roughness=0.3)
    ceramic = material('Insulator', (0.72, 0.77, 0.8), roughness=0.38)
    warning = material('WarningYellow', (0.96, 0.68, 0.03), roughness=0.45)
    box('ConcretePad', (0, 0.08, 0), (2.7, 0.16, 2.2), ceramic, 0.03)
    box('Transformer', (0, 0.72, 0), (1.15, 1.12, 0.82), metal, 0.06)
    for x in (-0.95, 0.95):
        for z in (-0.65, 0.65):
            cylinder('FencePost', (x, 0.55, z), 0.035, 1.1, metal)
    for x in (-0.42, 0.0, 0.42):
        cylinder('Bushing', (x, 1.47, 0), 0.09, 0.34, ceramic)
    box('WarningPanel', (0, 0.85, -0.421), (0.42, 0.32, 0.02), warning, 0.01)
    export_glb(out_dir, 'power-substation-compact-v1.glb')


def create_communications_tower(out_dir):
    clean_scene()
    steel = material('TowerSteel', (0.24, 0.28, 0.31), metallic=0.82, roughness=0.3)
    panel = material('AntennaPanel', (0.74, 0.78, 0.8), metallic=0.55, roughness=0.26)
    warning = material('TowerSafetyOrange', (0.95, 0.2, 0.03), roughness=0.45)
    box('Foundation', (0, 0.1, 0), (1.5, 0.2, 1.5), steel, 0.04)
    for height in (0.8, 1.8, 2.8, 3.8):
        cylinder('TowerMast', (0, height, 0), 0.085, 1.0, steel, 12)
        if height < 3.8:
            for angle in (0, math.pi / 2, math.pi, math.pi * 1.5):
                brace = box('TowerBrace', (0.26 * math.cos(angle), height + 0.3, 0.26 * math.sin(angle)), (0.05, 0.7, 0.05), steel)
                brace.rotation_euler[2] = angle + 0.55
    for angle in (0, math.pi * 0.5):
        panel_obj = box('AntennaPanel', (0.42 * math.cos(angle), 3.9, 0.42 * math.sin(angle)), (0.08, 0.48, 0.28), panel, 0.02)
        panel_obj.rotation_euler[1] = angle
    cylinder('Beacon', (0, 4.45, 0), 0.10, 0.18, warning, 16)
    export_glb(out_dir, 'communications-tower-compact-v1.glb')


def create_container_yard(out_dir):
    clean_scene()
    concrete = material('Concrete', (0.34, 0.36, 0.38), roughness=0.82)
    blue = material('ContainerBlue', (0.04, 0.20, 0.46), metallic=0.25, roughness=0.48)
    red = material('ContainerRed', (0.55, 0.06, 0.03), metallic=0.22, roughness=0.5)
    yellow = material('ContainerYellow', (0.82, 0.48, 0.03), metallic=0.18, roughness=0.5)
    box('YardPad', (0, 0.08, 0), (4.8, 0.16, 3.6), concrete, 0.04)
    mats = (blue, red, yellow, blue, red, yellow)
    positions = [(-1.35, 0.35, -0.8), (0, 0.35, -0.8), (1.35, 0.35, -0.8), (-0.68, 0.35, 0.8), (0.68, 0.35, 0.8), (0.68, 1.0, 0.8)]
    for index, ((x, y, z), mat) in enumerate(zip(positions, mats)):
        box('CargoContainer', (x, y, z), (1.16, 0.58, 0.52), mat, 0.035)
        box('ContainerDoor', (x, y, z - 0.266), (0.76, 0.42, 0.015), concrete, 0.006)
    export_glb(out_dir, 'container-yard-modular-v1.glb')


def create_cold_storage(out_dir):
    clean_scene()
    wall = material('ColdStorageWall', (0.79, 0.86, 0.9), metallic=0.08, roughness=0.48)
    roof = material('ColdStorageRoof', (0.23, 0.34, 0.42), metallic=0.25, roughness=0.44)
    door = material('DockDoor', (0.1, 0.13, 0.16), metallic=0.65, roughness=0.34)
    pad = material('Concrete', (0.34, 0.36, 0.38), roughness=0.82)
    box('LoadingPad', (0, 0.08, 0.35), (4.3, 0.16, 3.0), pad, 0.04)
    box('ColdStorageBuilding', (0, 1.25, -0.35), (3.7, 2.4, 2.0), wall, 0.05)
    box('Roof', (0, 2.55, -0.35), (3.95, 0.22, 2.25), roof, 0.05)
    for x in (-1.05, 0, 1.05):
        box('LoadingDockDoor', (x, 1.05, 0.67), (0.76, 1.35, 0.05), door, 0.02)
        box('DockBumper', (x, 0.36, 0.78), (0.92, 0.18, 0.18), roof, 0.02)
    export_glb(out_dir, 'cold-storage-loading-dock-v1.glb')


def create_forklift(out_dir):
    clean_scene()
    yellow = material('ForkliftYellow', (0.98, 0.56, 0.02), metallic=0.22, roughness=0.4)
    dark = material('ForkliftTire', (0.025, 0.03, 0.035), roughness=0.8)
    steel = material('ForkliftSteel', (0.20, 0.24, 0.27), metallic=0.85, roughness=0.28)
    box('ForkliftChassis', (0, 0.32, 0), (1.25, 0.35, 1.65), yellow, 0.06)
    box('ForkliftCounterweight', (0, 0.68, 0.52), (1.05, 0.72, 0.58), yellow, 0.08)
    box('ForkliftSeat', (0, 0.88, 0.18), (0.42, 0.12, 0.38), dark, 0.02)
    for x in (-0.5, 0.5):
        for z in (-0.53, 0.55):
            tire = cylinder('ForkliftWheel', (x, 0.24, z), 0.25, 0.18, dark, 16)
            tire.rotation_euler[0] = math.pi * 0.5
    for x in (-0.36, 0.36):
        box('MastRail', (x, 1.55, -0.78), (0.08, 2.5, 0.08), steel, 0.01)
        box('Fork', (x, 0.18, -1.25), (0.09, 0.06, 0.85), steel, 0.01)
    box('MastCrossbar', (0, 2.55, -0.78), (0.86, 0.08, 0.08), steel, 0.01)
    export_glb(out_dir, 'vehicle-forklift-industrial-v1.glb')


def create_agv(out_dir):
    clean_scene()
    body = material('AGVBody', (0.12, 0.22, 0.32), metallic=0.5, roughness=0.3)
    tire = material('AGVTire', (0.025, 0.03, 0.035), roughness=0.8)
    light = material('AGVLight', (0.1, 0.78, 0.95), metallic=0.15, roughness=0.2)
    box('AGVChassis', (0, 0.22, 0), (1.25, 0.32, 1.55), body, 0.12)
    box('AGVTopModule', (0, 0.47, 0), (0.84, 0.22, 0.78), body, 0.08)
    cylinder('Lidar', (0, 0.66, 0.24), 0.11, 0.12, light, 16)
    for x in (-0.5, 0.5):
        for z in (-0.5, 0.5):
            wheel = cylinder('AGVWheel', (x, 0.15, z), 0.16, 0.13, tire, 16)
            wheel.rotation_euler[0] = math.pi * 0.5
    box('StatusLight', (0, 0.49, -0.79), (0.46, 0.08, 0.03), light, 0.01)
    export_glb(out_dir, 'vehicle-agv-platform-v1.glb')


def create_drone(out_dir):
    clean_scene()
    body = material('DroneBody', (0.15, 0.18, 0.21), metallic=0.55, roughness=0.28)
    rotor = material('Rotor', (0.05, 0.06, 0.07), metallic=0.35, roughness=0.32)
    light = material('DroneLight', (0.92, 0.12, 0.05), metallic=0.15, roughness=0.18)
    cylinder('DroneBody', (0, 0, 0), 0.28, 0.24, body, 20)
    for x, z in ((-0.48, -0.48), (-0.48, 0.48), (0.48, -0.48), (0.48, 0.48)):
        arm = box('DroneArm', (x * 0.5, 0, z * 0.5), (0.07, 0.07, 0.72), body, 0.02)
        arm.rotation_euler[1] = math.atan2(x, z)
        cylinder('RotorHub', (x, 0.05, z), 0.12, 0.06, rotor, 16)
        box('RotorBlade', (x, 0.09, z), (0.58, 0.02, 0.06), rotor, 0.02)
        box('NavigationLight', (x, -0.03, z), (0.08, 0.04, 0.08), light, 0.01)
    export_glb(out_dir, 'vehicle-inspection-drone-v1.glb')


def create_truck_parking(out_dir):
    clean_scene()
    asphalt = material('ParkingAsphalt', (0.07, 0.08, 0.09), roughness=0.9)
    paint = material('ParkingPaint', (0.92, 0.92, 0.9), roughness=0.5)
    curb = material('ParkingCurb', (0.43, 0.45, 0.47), roughness=0.75)
    box('TruckYardPad', (0, -0.07, 0), (ROAD_WIDTH * 3, 0.14, ROAD_LENGTH * 3), asphalt, 0.03)
    for x in (-ROAD_WIDTH * 0.5, ROAD_WIDTH * 0.5):
        box('ParkingLine', (x, 0.004, 0), (0.055, 0.01, ROAD_LENGTH * 2.8), paint)
    for z in (-ROAD_LENGTH, 0, ROAD_LENGTH):
        box('BayStop', (0, 0.055, z + ROAD_LENGTH * 0.34), (ROAD_WIDTH * 2.4, 0.11, 0.12), curb, 0.02)
    export_glb(out_dir, 'truck-yard-parking-module-v1.glb')


arguments = cli_args()
out_dir = arguments[0] if arguments and not arguments[0].startswith('--') else os.environ.get('MESHY_INCOMING_MODELS_ROOT')
if not out_dir:
    raise RuntimeError('Pass an output directory or configure MESHY_INCOMING_MODELS_ROOT.')
selected = arguments[arguments.index('--only') + 1] if '--only' in arguments else 'all'
builders = {
    'curve': create_curve,
    'ramp': create_ramp,
    'barrier': create_barrier,
    'signal': create_signal,
    'gate': create_security_gate,
    'substation': create_substation,
    'communications': create_communications_tower,
    'container-yard': create_container_yard,
    'cold-storage': create_cold_storage,
    'forklift': create_forklift,
    'agv': create_agv,
    'drone': create_drone,
    'truck-yard': create_truck_parking,
}
if selected == 'all':
    for builder in builders.values():
        builder(out_dir)
elif selected in builders:
    builders[selected](out_dir)
else:
    raise SystemExit('Unknown --only value: ' + selected)
