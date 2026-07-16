"""Render the V3 metropolitan geography studies without saving the master Blend."""
import bpy, sys
from pathlib import Path
from mathutils import Vector
SCRIPT_DIR=Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path: sys.path.append(str(SCRIPT_DIR))
from world_output import resolve_output_root

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
repo=Path(args[args.index('--repo')+1]).resolve() if '--repo' in args else Path.cwd()
output_root=resolve_output_root(args)
output=output_root.v3_previews; output.mkdir(parents=True,exist_ok=True)

def realtime_render_engine(scene):
    engine_property=scene.render.bl_rna.properties['engine']
    supported={item.identifier for item in engine_property.enum_items}
    for engine in ('BLENDER_EEVEE_NEXT','BLENDER_EEVEE'):
        if engine in supported:
            return engine
    raise RuntimeError('No supported EEVEE render engine is available: '+', '.join(sorted(supported)))

def render(name, target, location, lens=48):
    data=bpy.data.cameras.get('MetropolitanCamera') or bpy.data.cameras.new('MetropolitanCamera')
    camera=bpy.data.objects.get('MetropolitanCamera') or bpy.data.objects.new('MetropolitanCamera',data)
    if camera.name not in bpy.context.scene.objects: bpy.context.scene.collection.objects.link(camera)
    data.type='PERSP'; data.lens=lens; data.clip_start=.1; data.clip_end=30000
    camera.location=location
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.scene.camera=camera
    bpy.context.scene.render.filepath=str(output/name)
    bpy.ops.render.render(write_still=True)

bpy.context.scene.render.engine=realtime_render_engine(bpy.context.scene)
bpy.context.scene.render.resolution_x=1600
bpy.context.scene.render.resolution_y=1000
bpy.context.scene.render.resolution_percentage=100

# Each target is a real geography coordinate from the V3 layout.  The views
# retain the linked city so coastline, river, roads and neighbouring districts
# remain visible instead of appearing as isolated asset turntables.
render('west-sea-port-overview.png',(-3400,420,0),(-6100,-4200,3850),50)
render('han-river-bridges-overview.png',(150,0,0),(-2600,-3900,3450),52)
render('north-east-mountains-overview.png',(2500,2850,260),(500,-900,4550),55)
render('south-plains-overview.png',(400,-3950,0),(2900,-6600,3550),52)
print(f'V3_METROPOLITAN_VIEWS={output}')
