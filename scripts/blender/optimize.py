import argparse
import sys
import bpy

def arguments():
    values = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    return parser.parse_args(values)

args = arguments()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args.input)

for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.validate(clean_customdata=False)
    obj.select_set(False)

bpy.ops.export_scene.gltf(filepath=args.output, export_format='GLB', export_apply=True, export_animations=True)
print('Optimized GLB written to ' + args.output)
