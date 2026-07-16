"""Render reproducible bird's-eye and topology views from the linked v3 master."""
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

def camera(name,location,scale):
    data=bpy.data.cameras.get(name) or bpy.data.cameras.new(name); obj=bpy.data.objects.get(name) or bpy.data.objects.new(name,data)
    if obj.name not in bpy.context.scene.objects:bpy.context.scene.collection.objects.link(obj)
    data.type='ORTHO'; data.ortho_scale=scale; data.clip_start=.1; data.clip_end=30000; obj.location=location; obj.rotation_euler=(Vector((0,0,0))-obj.location).to_track_quat('-Z','Y').to_euler(); return obj

bpy.context.scene.render.engine=realtime_render_engine(bpy.context.scene); bpy.context.scene.render.resolution_x=1600; bpy.context.scene.render.resolution_y=1000; bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.camera=camera('ArchiveCityV3BirdsEye',(0,-600,9400),11200); bpy.context.scene.render.filepath=str(output/'birds-eye-view.png'); bpy.ops.render.render(write_still=True)

# Topography isolates linked Infrastructure without editing or saving the master scene.
hidden=[]
for obj in bpy.context.scene.objects:
    if obj.name.startswith('LinkedDistrict_') and obj.name!='LinkedDistrict_infrastructure':
        hidden.append((obj,obj.hide_render)); obj.hide_render=True
bpy.context.scene.camera=camera('ArchiveCityV3Topography',(0,-300,9600),11200); bpy.context.scene.render.filepath=str(output/'topography-overview.png'); bpy.ops.render.render(write_still=True)
for obj,value in hidden: obj.hide_render=value
print(f'V3_GEOGRAPHY_VIEWS={output}')
