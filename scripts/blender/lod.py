import argparse
import os
import sys
import bpy

def arguments():
    values = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--ratios', required=True)
    parser.add_argument('--levels', default='')
    return parser.parse_args(values)

args = arguments()
ratios = [float(value) for value in args.ratios.split(',')]
levels = [int(value) for value in args.levels.split(',') if value] if args.levels else list(range(len(ratios)))
os.makedirs(args.output_dir, exist_ok=True)

for index in levels:
    ratio = ratios[index]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=args.input)
    if ratio < 1:
        for obj in bpy.context.scene.objects:
            if obj.type != 'MESH' or len(obj.data.polygons) < 8:
                continue
            bpy.context.view_layer.objects.active = obj
            modifier = obj.modifiers.new(name='ArchiveWorldLOD', type='DECIMATE')
            modifier.ratio = max(0.02, min(ratio, 1.0))
            modifier.use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    output = os.path.join(args.output_dir, 'lod' + str(index) + '.glb')
    bpy.ops.export_scene.gltf(filepath=output, export_format='GLB', export_apply=True, export_animations=True)
    print('LOD ' + str(index) + ' written to ' + output)
