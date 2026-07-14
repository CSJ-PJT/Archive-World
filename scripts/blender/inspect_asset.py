import bpy
import json
import os
import sys
from mathutils import Vector


def args_after_separator():
    return sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


args = args_after_separator()
if not args:
    raise SystemExit('Usage: blender -b --python inspect_asset.py -- <asset.glb>')

source = args[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
minimum = [min(point[index] for point in points) for index in range(3)] if points else None
maximum = [max(point[index] for point in points) for index in range(3)] if points else None
result = {
    'source': source,
    'meshObjects': len(objects),
    'objectNames': [obj.name for obj in objects],
    'bounds': {'min': minimum, 'max': maximum} if points else None,
    'dimensions': [maximum[index] - minimum[index] for index in range(3)] if points else None,
    'materials': sorted({slot.material.name for obj in objects for slot in obj.material_slots if slot.material}),
    'unitSystem': bpy.context.scene.unit_settings.system,
    'scaleLength': bpy.context.scene.unit_settings.scale_length,
}
print('ARCHIVE_WORLD_INSPECT=' + json.dumps(result, ensure_ascii=False))
