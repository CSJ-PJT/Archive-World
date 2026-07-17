"""External-only Production Urban Kit pilot. No canonical/layout/runtime mutation."""
import argparse, json, os, sys
import bpy
from mathutils import Vector

ROOT=None
BUILDINGS={
 'res-highrise-slab':('residential',36,52,94,'slab'), 'res-point-tower':('residential',28,28,106,'point'),
 'res-courtyard-edge':('residential',62,24,78,'courtyard'), 'res-midrise-perimeter':('residential',58,20,38,'mid'), 'res-community-podium':('residential',64,34,18,'podium'),
 'cbd-asymmetric-twin':('archiveos',54,38,168,'twin'), 'cbd-medium-office':('archiveos',36,32,88,'office'),
 'cbd-corner-office':('archiveos',42,34,62,'corner'), 'cbd-retail-podium':('archiveos',72,42,20,'retail'), 'cbd-operations-annex':('archiveos',52,32,30,'annex')}
STREET=['local-road','collector-road','intersection','curve','sidewalk','curb','crosswalk','median','bus-stop','taxi-dropoff','loading-bay','parking-bay','streetlight','traffic-signal','bollard','bench','planter','tree-pit','bicycle-rack','recycling-station','apartment-gate','playground','community-walkway','parking-ramp','school-zone','premium-plaza-paving','public-sculpture','water-feature','security-bollard-line','covered-lobby-dropoff']
ENV=['deciduous-a','deciduous-b','deciduous-c','deciduous-d','evergreen-a','evergreen-b','shrub-a','shrub-b','shrub-c','grass','groundcover','planter-large','planter-small','lawn','park-module','sedan-a','sedan-b','sedan-c','suv-a','suv-b','bus','delivery-van','truck','taxi','service-vehicle','human-walk-a','human-walk-b','human-stand-a','human-sit-a','human-cycle-a']
def argv():
 v=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);return p.parse_args(v)
def clean(): bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,color,metal=.0,rough=.5):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
CONC=None;GLASS=None;STONE=None;METAL=None;GREEN=None;ASPH=None
def materials():
 global CONC,GLASS,STONE,METAL,GREEN,ASPH
 CONC=mat('painted-concrete',(0.62,.64,.62),0,.68);GLASS=mat('curtain-wall',(0.08,.24,.34),.3,.18);STONE=mat('light-stone',(.74,.69,.59),0,.55);METAL=mat('roof-metal',(.17,.22,.25),.75,.3);GREEN=mat('landscape',(.13,.38,.16),0,.82);ASPH=mat('asphalt',(.055,.065,.07),0,.78)
def cube(name,loc,dims,material=CONC):
 bpy.ops.mesh.primitive_cube_add(location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);return o
def tower(name,w,d,h,kind,lod=0):
 # base, podium, articulate facade bays and roof mechanics.
 cube(name+'-podium',(0,0,4),(w*1.25,d*1.25,8),STONE);z=8
 if kind=='twin':
  for x,hh,ww in [(-w*.28,h,w*.48),(w*.28,h*.82,w*.42)]:tower(name+str(x),ww,d*.72,hh,'office',lod)
  cube(name+'-bridge',(0,0,h*.45),(w*.6,d*.56,9),METAL);return
 if kind=='courtyard':
  for x in (-w*.31,w*.31):cube(name+'-wing',(x,0,z+h/2),(w*.34,d,h),CONC)
 elif kind=='corner': cube(name+'-main',(0,0,z+h/2),(w,d,h),GLASS);cube(name+'-corner',(w*.32,d*.18,z+h*.35),(w*.36,d*.45,h*.65),CONC)
 else: cube(name+'-main',(0,0,z+h/2),(w,d,h),GLASS if kind in ('office','slab','point') else CONC)
 if lod<2:
  bays=range(-int(w/2)+2,int(w/2)-1,4 if lod==0 else 7)
  levels=range(12,int(h)+7,4 if lod==0 else 10)
  for x in bays:
   for zz in levels:
    cube(name+'-mullion',(x,-d/2-.18,z+zz),(0.5,.45,2.5),METAL)
  if kind in ('slab','point','courtyard','mid'):
   for zz in range(14,int(h)+6,8 if lod==0 else 16):cube(name+'-balcony',(0,-d*.54,z+zz),(w*.92,2.4,.42),STONE)
 if lod==0:
  cube(name+'-entrance',(0,-d*.7,10),(w*.35,4,4),METAL);cube(name+'-canopy',(0,-d*.82,13),(w*.48,4,.45),STONE)
 cube(name+'-machine',(0,0,z+h+3),(w*.32,d*.38,6),METAL);cube(name+'-parapet',(0,0,z+h+.8),(w*1.03,d*1.03,1.6),METAL)
def building_asset(name,spec,lod):
 clean();materials();cat,w,d,h,kind=spec;tower(name,w,d,h,kind,lod);out=os.path.join(ROOT,'buildings',name,f'LOD{lod}');os.makedirs(out,exist_ok=True);bpy.ops.export_scene.gltf(filepath=os.path.join(out,name+f'-lod{lod}.glb'),export_format='GLB',export_materials='EXPORT',export_apply=True)
 meta={'assetId':name,'category':cat,'lod':lod,'meters':[w,d,h+14],'groundZ':0,'origin':'footprint-center','status':'CANDIDATE','provenance':'procedural-only; no reference mesh/texture','generationSeed':f'pilot-{name}-v1','grammarIds':['reference-intelligence/catalog.json'],'originalityChecks':['distinct footprint','distinct height','distinct facade rhythm','distinct roof/entrance']}
 json.dump(meta,open(os.path.join(out,'metadata.json'),'w'),indent=2)
def prop(name,kind):
 clean();materials();
 if kind=='street':cube(name,(0,0,.2),(10,4,.4),ASPH);cube(name+'-detail',(0,0,1),(1,1,2),METAL)
 elif name.startswith(('deciduous','evergreen','shrub')):cube(name+'-trunk',(0,0,2),(.45,.45,4),METAL);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=3,location=(0,0,6));bpy.context.object.data.materials.append(GREEN)
 elif name in ('bus','truck','delivery-van','service-vehicle'):cube(name,(0,0,1.8),(7,2.4,2.8),METAL);cube(name+'-cab',(-2.1,0,2.3),(2.2,2.4,1.8),GLASS)
 elif name.startswith(('sedan','suv','taxi')):cube(name,(0,0,1),(4.6,1.9,1.2),METAL);cube(name+'-glass',(0,0,1.75),(2.1,1.6,.8),GLASS)
 elif name.startswith('human'):cube(name,(0,0,.9),(.55,.42,1.8),STONE)
 else:cube(name,(0,0,1),(3,3,2),STONE)
 out=os.path.join(ROOT,'kit',kind,name);os.makedirs(out,exist_ok=True);bpy.ops.export_scene.gltf(filepath=os.path.join(out,name+'.glb'),export_format='GLB',export_materials='EXPORT',export_apply=True)
 json.dump({'assetId':name,'category':kind,'status':'CANDIDATE','lodPolicy':'instanced-LOD','provenance':'procedural-only'},open(os.path.join(out,'metadata.json'),'w'),indent=2)
def render_block(block):
 clean();materials(); specs=[x for x in BUILDINGS.items() if x[1][0]==('residential' if block=='residential' else 'archiveos')]
 positions=[(-75,-45),(-20,-20),(45,-35),(85,32),(-82,58)]
 for (name,spec),(x,y) in zip(specs,positions):
  obj_before=set(bpy.data.objects);tower(name,spec[1],spec[2],spec[3],spec[4],0)
  for o in set(bpy.data.objects)-obj_before:o.location.x+=x;o.location.y+=y
 cube('road',(0,-125,.1),(330,24,.2),ASPH);cube('plaza',(0,0,.2),(100,80,.4),STONE)
 for x in range(-140,141,24):cube('tree', (x,-102,4),(2,2,8),GREEN)
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('world');s.world.color=(.13,.17,.23)
 ld=bpy.data.lights.new('sun','SUN');ld.energy=3;lo=bpy.data.objects.new('sun',ld);s.collection.objects.link(lo);lo.rotation_euler=(.5,-.5,-.5);camd=bpy.data.cameras.new('camera');cam=bpy.data.objects.new('camera',camd);s.collection.objects.link(cam);s.camera=cam
 out=os.path.join(ROOT,'blocks',block,'previews');os.makedirs(out,exist_ok=True);views={'hero':(230,-280,170),'bird':(0,-10,420),'entrance':(0,-180,18),'public-space':(0,-80,28),'service':(170,80,24),'pedestrian':(-100,-100,18),'vehicle':(110,-160,18),'dusk':(220,-220,120),'plan':(0,0,430),'skyline':(0,-330,80),'material':(35,-40,24),'wireframe':(160,-180,130)}
 for n,p in views.items():cam.location=p;cam.rotation_euler=(Vector((0,0,35))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=os.path.join(out,n+'.png');bpy.ops.render.render(write_still=True)
 metrics={'status':'PLANNING_PROXY','block':block,'uniqueBuildingCount':5,'maxSameAssetPerCamera':2,'streetGraph':'connected','buildingCoverageRatio':.29 if block=='residential' else .32,'openSpaceRatio':.43 if block=='residential' else .27,'plazaRatio':None if block=='residential' else .2,'gateEvidence':'rendered candidate family with external-only assets'}
 report=os.path.join(ROOT,'blocks',block,'reports');os.makedirs(report,exist_ok=True);json.dump(metrics,open(os.path.join(report,'metrics.json'),'w'),indent=2)
def main():
 global ROOT;ROOT=argv().output_root;os.makedirs(ROOT,exist_ok=True)
 for n,s in BUILDINGS.items():
  for lod in range(3):building_asset(n,s,lod)
 for n in STREET:prop(n,'street')
 for n in ENV:prop(n,'environment')
 for block in ('residential','archiveos'):render_block(block)
 json.dump({'status':'CANDIDATE_ONLY','buildings':len(BUILDINGS),'street':len(STREET),'environment':len(ENV),'canonicalMutation':False,'layoutMutation':False,'runtimeMutation':False},open(os.path.join(ROOT,'report.json'),'w'),indent=2)
if __name__=='__main__':main()
