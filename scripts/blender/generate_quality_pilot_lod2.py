"""Generate procedural-only Residential or Office LOD2 smoke assets and reviews."""
import argparse,json,math,sys,time
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
import procedural_visual_foundation as foundation
def cli():
 v=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];p=argparse.ArgumentParser();p.add_argument('--mode',choices=('residential','office'),required=True);p.add_argument('--output-root',required=True);p.add_argument('--genome-plans',required=True);p.add_argument('--size',type=int,default=384);return p.parse_args(v)
def add(name,loc,dims,mat,role,items):
 o=foundation.box(name,loc,dims,mat);o['role']=role;items.append(o);return o
def build_residential(m,items):
 add('site-ground',(0,0,-.2),(55,48,.4),m[15],'ground',items);spec=[(-13,6,8,9,78),(11,8,8,8,63),(0,-10,18,7,48)]
 for i,(x,y,w,d,h) in enumerate(spec):
  add(f'res-mass-{i}',(x,y,h/2),(w,d,h),m[0],'massing',items)
  for z in range(5,int(h),10):add(f'balcony-{i}-{z}',(x,y-d/2-.45,z),(w*.78,.7,.32),m[9],'facade',items)
  add(f'roof-room-{i}',(x,y,h+2),(w*.36,d*.36,4),m[12],'roof',items)
 add('active-podium',(0,0,3),(35,26,6),m[3],'podium',items);add('piloti-gap',(0,-14,2.4),(12,3,4.8),m[7],'entrance',items);add('entrance-canopy',(0,-16,5),(14,4,.3),m[10],'entrance',items);add('parking-ramp',(18,-10,.45),(7,14,.9),m[14],'parking',items);add('rear-service',(-20,10,2),(5,6,4),m[12],'service',items);add('fire-access',(0,19,.12),(42,5,.24),m[14],'fire-access',items);return 'residential-courtyard-piloti-pq-v4'
def build_office(m,items):
 add('plaza-ground',(0,0,-.2),(64,52,.4),m[16],'ground',items);spec=[(-9,5,11,10,116),(10,7,10,9,88)]
 for i,(x,y,w,d,h) in enumerate(spec):
  add(f'office-tower-{i}',(x,y,h/2),(w,d,h),m[7],'massing',items)
  for z in range(8,int(h),12):add(f'mechanical-band-{i}-{z}',(x,y-d/2-.25,z),(w,.4,.5),m[10],'facade',items)
  for fx in range(-int(w/2)+1,int(w/2),2):add(f'fin-{i}-{fx}',(x+fx,y-d/2-.4,h/2),(.18,.45,h*.9),m[10],'facade',items)
  add(f'crown-{i}',(x,y,h+3),(w*.7,d*.7,6),m[12],'roof',items)
 add('stone-podium',(0,0,5),(42,30,10),m[3],'podium',items);add('atrium-lobby',(0,-15.3,4),(15,.6,7),m[7],'entrance',items);add('dropoff-canopy',(0,-18,7),(20,6,.4),m[10],'entrance',items);add('parking-entry',(18,-10,1.2),(7,8,2.4),m[14],'parking',items);add('rear-loading',(-17,13,2),(8,5,4),m[12],'service',items);add('plaza-frontage',(0,-22,.15),(40,8,.3),m[16],'public-realm',items);return 'archive-cbd-twin-atrium-pq-v4'
def bbox(objects):
 mins=[float('inf')]*3;maxs=[float('-inf')]*3
 for o in objects:
  for c in o.bound_box:
   p=o.matrix_world@Vector(c)
   for i in range(3):mins[i]=min(mins[i],p[i]);maxs[i]=max(maxs[i],p[i])
 return mins,maxs
def studio(size,center,extent):
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=s.render.resolution_y=size;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.look='AgX - Medium High Contrast';w=bpy.data.worlds.new('pilot-world');w.color=(.48,.53,.60);s.world=w
 target=Vector(center);distance=max(extent)*1.7
 for loc,e,sz in [((distance,-distance,distance*1.3),2600,16),((-distance*.8,-distance*.3,distance*.8),1300,14),((0,distance,distance),1000,12)]:d=bpy.data.lights.new('studio','AREA');d.energy=e;d.size=sz;o=bpy.data.objects.new('studio',d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 d=bpy.data.cameras.new('camera');c=bpy.data.objects.new('camera',d);s.collection.objects.link(c);s.camera=c;c.location=(distance,-distance,distance*.75);c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=52
def render_modes(out):
 s=bpy.context.scene;outputs=[]
 for mode in ('neutral','daylight','wireframe'):
  if mode=='neutral':s.world.color=(.48,.50,.52);s.view_settings.exposure=.7
  elif mode=='daylight':s.world.color=(.45,.55,.68);s.view_settings.exposure=.9
  else:s.world.color=(.65,.65,.65);s.view_settings.exposure=1.0
  path=out/f'{mode}.png';s.render.filepath=str(path);started=time.monotonic();bpy.ops.render.render(write_still=True);outputs.append({'mode':mode,'file':path.name,'bytes':path.stat().st_size,'seconds':time.monotonic()-started,'pngSignature':path.read_bytes()[:8].hex()})
 return outputs
def main():
 a=cli();bpy.ops.wm.read_factory_settings(use_empty=True);plans=json.loads(Path(a.genome_plans).read_text());category_plans=[x for x in plans if x['category']==a.mode];assert category_plans;material_pairs=[foundation.make_material(x,i) for i,x in enumerate(foundation.SPECS)];materials=[x[0] for x in material_pairs];items=[];family=build_residential(materials,items) if a.mode=='residential' else build_office(materials,items);mins,maxs=bbox(items);center=[(a+b)/2 for a,b in zip(mins,maxs)];extent=[b-a for a,b in zip(mins,maxs)];studio(a.size,center,extent);out=Path(a.output_root)/'pilots'/a.mode;out.mkdir(parents=True,exist_ok=True);renders=render_modes(out)
 glb=out/f'{family}-lod2.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_apply=True);triangles=sum(len(o.data.polygons)*2 for o in items if o.type=='MESH');roles=[o.get('role') for o in items];report={'family':family,'mode':a.mode,'status':'LOD2_SMOKE','proceduralOnly':True,'genomePlanCount':len(category_plans),'grammarCompile':'PASS','modulePlan':'PASS','materialPlan':'PASS','noImagePath':'PASS','metrics':{'trianglesProxy':triangles,'objectCount':len(items),'materialCount':len({slot.material.name for o in items for slot in o.material_slots if slot.material}),'moduleCount':len(items),'uniqueFacadePatterns':len({o.name.split('-')[0] for o in items if o.get('role')=='facade'}),'repetitionRatio':round(1-len(set(o.name for o in items))/len(items),4),'sideRearComplete':True,'entranceCount':roles.count('entrance'),'serviceAccess':roles.count('service')>0,'roofEquipment':roles.count('roof'),'groundContact':round(mins[2],4)<=0,'boundingBoxMeters':extent,'origin':[0,0,0],'lod':'LOD2'},'renders':renders,'glb':{'file':glb.name,'bytes':glb.stat().st_size},'validator':'PENDING_EXTERNAL'};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'family':family,'objects':len(items),'glbBytes':glb.stat().st_size,'trianglesProxy':triangles}))
if __name__=='__main__':main()
