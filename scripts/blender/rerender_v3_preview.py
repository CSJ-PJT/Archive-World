"""Render one existing v3 scene after applying the city-scale camera clip range.

It only updates the PNG passed by --output; the opened Blend is never saved.
"""
import bpy, sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
output=Path(args[args.index('--output')+1]).resolve()
camera=bpy.context.scene.camera
if camera is None: raise RuntimeError('scene has no active camera')
roots=[obj for obj in bpy.context.scene.objects if obj.name.startswith(('Instance_','RoadModule_'))]
if roots:
    min_x,max_x=min(obj.location.x for obj in roots),max(obj.location.x for obj in roots)
    min_y,max_y=min(obj.location.y for obj in roots),max(obj.location.y for obj in roots)
    center=Vector(((min_x+max_x)/2,(min_y+max_y)/2,0))
    span=max(max_x-min_x,max_y-min_y,180)*1.45
    camera.data.type='PERSP'; camera.data.lens=46; camera.location=center+Vector((span*1.08,-span*1.08,span*.78)); camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
else:
    # City Overview prioritizes readable district clusters; the full 10km extent
    # remains available in the orthographic Bird's-eye and Topography renders.
    center=Vector((0,0,0)); camera.data.type='PERSP'; camera.data.lens=56; camera.location=(4300,-5000,4300); camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.clip_start=.1; camera.data.clip_end=30000
bpy.context.scene.render.engine='BLENDER_EEVEE_NEXT'; bpy.context.scene.render.resolution_x=1600; bpy.context.scene.render.resolution_y=1000; bpy.context.scene.render.resolution_percentage=100
output.parent.mkdir(parents=True,exist_ok=True); bpy.context.scene.render.filepath=str(output); bpy.ops.render.render(write_still=True)
print(f'V3_PREVIEW={output}')
