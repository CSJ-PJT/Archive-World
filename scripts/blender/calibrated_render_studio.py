"""Eight-preset, image-free architectural calibration studio for Blender 5.2."""
import argparse, json, os, sys, time
from pathlib import Path
import bpy
from mathutils import Vector

def cli():
    values=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);p.add_argument('--presets',required=True);p.add_argument('--size',type=int,default=320);return p.parse_args(values)
def material(name,color,rough=.6,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
def cube(name,loc,dims,mat,group):
    bpy.ops.mesh.primitive_cube_add(location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;o['calibrationGroup']=group;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
def add_light(name,location,energy,size,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.location=location;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();return o
def build_scene():
    concrete=material('painted-concrete',(.52,.54,.52),.72);stone=material('light-stone',(.72,.67,.58),.58);metal=material('aluminum',(.24,.29,.31),.3,.65);glass=material('glass',(.09,.25,.34),.16);dark=material('dark',(.045,.05,.055),.52);ground=material('ground',(.42,.43,.41),.8)
    cube('ground',(0,0,-.2),(44,36,.4),ground,'common')
    cube('primitive-mass',(0,2,5),(12,9,10),concrete,'primitive-mass');cube('primitive-podium',(0,-2,1.2),(16,6,2.4),stone,'primitive-mass')
    cube('facade-wall',(0,3,6),(16,.7,12),concrete,'facade-test-wall')
    for x in (-6,-3.6,-1.2,1.2,3.6,6): cube('window-bay',(x,2.55,7),(1.7,.25,8),glass,'facade-test-wall');cube('mullion',(x+.95,2.35,7),(.14,.3,8.5),metal,'facade-test-wall')
    cube('entrance-base',(0,3,2),(16,5,4),stone,'entrance-module');cube('entrance-glass',(0,.3,2.4),(6,.35,4.2),glass,'entrance-module');cube('canopy',(0,-1.1,4.8),(9,3,.3),metal,'entrance-module')
    cube('roof-deck',(0,2,.4),(18,14,.8),concrete,'roof-module');cube('machine-room',(0,2,3),(7,5,5),metal,'roof-module');cube('hvac-screen',(6,2,1.8),(4,5,3),dark,'roof-module')
    cube('sidewalk',(0,1,.1),(24,12,.2),concrete,'ground-interface');cube('curb',(0,-5,.35),(24,.5,.7),stone,'ground-interface');cube('planter',(-6,-2,1),(5,2,2),stone,'ground-interface');cube('ramp',(6,-1,.25),(6,8,.5),dark,'ground-interface')
    cube('human-scale',(-10,-5,.875),(.45,.35,1.75),dark,'common');cube('sedan-scale',(8,-6,.75),(4.5,1.8,1.5),metal,'common')
def apply_preset(p,size):
    s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=s.render.resolution_y=size;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.look=p['color']['look'];s.view_settings.exposure=p['exposure'];s.world.color=tuple(p['world']['color'])
    for o in list(bpy.data.objects):
        if o.type=='LIGHT': bpy.data.objects.remove(o,do_unlink=True)
        elif 'calibrationGroup' in o: o.hide_render=o['calibrationGroup'] not in ('common',p['target'])
    target=Vector(tuple(p['camera']['target']));
    for i,l in enumerate(p['lights']):add_light(f"{p['id']}-light-{i}",tuple(l['position']),l['energy'],l['size'],target)
    cam=bpy.data.objects.get('review-camera')
    if not cam:
        d=bpy.data.cameras.new('review-camera');cam=bpy.data.objects.new('review-camera',d);s.collection.objects.link(cam)
    s.camera=cam;cam.data.lens=p['camera']['focalLength'];cam.location=tuple(p['camera']['position']);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
def main():
    a=cli();presets=json.loads(Path(a.presets).read_text(encoding='utf-8'));bpy.ops.wm.read_factory_settings(use_empty=True);world=bpy.data.worlds.new('review-world');bpy.context.scene.world=world;build_scene();out=Path(a.output_root)/'render-studio';out.mkdir(parents=True,exist_ok=True);reports=[]
    for p in presets:
        apply_preset(p,a.size);path=out/f"{p['id']}-{p['target']}.png";bpy.context.scene.render.filepath=str(path);started=time.monotonic();bpy.ops.render.render(write_still=True);reports.append({'id':p['id'],'target':p['target'],'output':path.name,'bytes':path.stat().st_size,'pngSignature':path.read_bytes()[:8].hex(),'expectedLuminance':p['expectedLuminance'],'renderSeconds':time.monotonic()-started})
    result={'presets':len(presets),'targets':sorted({x['target'] for x in reports}),'reports':reports,'externalOutput':True,'absoluteUserPaths':0};(out/'render-studio-raw-report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'presets':len(presets),'targets':len(result['targets'])}))
if __name__=='__main__':main()
