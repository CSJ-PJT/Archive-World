"""External-only Urban Grammar V1.1 planning scenes; all massing is PLACEHOLDER."""
import argparse,json,os,sys
import bpy
from mathutils import Vector
def args():
 v=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);return p.parse_args(v)
STREET=['local-road','collector-road','sidewalk','crosswalk','curb','tree-pit','streetlight','bench','bollard','bus-stop','bicycle-rack','parking-bay','loading-bay','planter','plaza-paving','playground','community-path','apartment-gate','recycling-station','school-zone','taxi-stand','water-feature','security-bollard']
def box(name,loc,dims,color):
 bpy.ops.mesh.primitive_cube_add(location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);o.data.materials.append(m);return o
def plan(kind):
 if kind=='residential':
  b=[('tower-a',(-75,-45),78),('tower-b',(-20,-25),92),('tower-c',(40,-35),84),('tower-d',(85,30),72),('midrise-a',(-95,55),42),('midrise-b',(0,72),38),('retail',(95,-85),15),('community',(-5,-92),14),('security',(-142,-110),7)]
  return block_data('residential',[350,280],b,{'blockAreaM2':98000,'buildingCoverageRatio':0.27,'openSpaceRatio':0.46,'pedestrianPathM':1840,'vehiclePathM':1120,'treeCount':128,'publicFrontageRatio':0.28,'uniqueBuildingCount':9,'maxSameAssetPerCamera':2},['courtyard','pocket-park','playground','small-plaza','bus-stop'])
 b=[('landmark-twin-a',(-55,15),190),('landmark-twin-b',(28,28),156),('office-a',(-125,-75),68),('office-b',(120,-60),60),('office-c',(125,80),54),('office-d',(-125,95),50),('operations-annex',(0,105),28),('retail-podium-a',(-42,-80),18),('retail-podium-b',(58,-82),18),('service-building',(155,110),14)]
 return block_data('archiveos',[420,320],b,{'blockAreaM2':134400,'buildingCoverageRatio':0.31,'plazaRatio':0.19,'activeFrontageRatio':0.33,'pedestrianPathM':2210,'serviceRouteM':740,'treeCount':146,'seatingCount':72,'lightingCount':58,'uniqueBuildingCount':10,'maxSameAssetPerCamera':2,'skylineHeightDistribution':[190,156,68,60,54,50,28,18,18,14]},['central-plaza','water-feature','shaded-walk','retail-frontage','taxi-stand'])

def block_data(district,meters,buildings,metrics,spaces):
 """A graph is explicit so route continuity is independently testable."""
 w,h=meters
 nodes=[
  {'id':'north-gate','xy':[0,h/2-12],'kind':'gate'}, {'id':'south-gate','xy':[0,-h/2+12],'kind':'gate'},
  {'id':'west-gate','xy':[-w/2+12,0],'kind':'gate'}, {'id':'east-gate','xy':[w/2-12,0],'kind':'gate'},
  {'id':'center','xy':[0,0],'kind':'plaza'}, {'id':'service','xy':[w*.34,h*.30],'kind':'service'},
  {'id':'fire','xy':[-w*.32,-h*.26],'kind':'fire-access'}]
 def edge(a,b,mode,public=True): return {'from':a,'to':b,'mode':mode,'public':public}
 edges=[edge('north-gate','center','pedestrian'),edge('south-gate','center','pedestrian'),edge('west-gate','center','pedestrian'),edge('east-gate','center','pedestrian'),edge('north-gate','east-gate','vehicle'),edge('east-gate','south-gate','vehicle'),edge('south-gate','west-gate','vehicle'),edge('west-gate','north-gate','vehicle'),edge('service','east-gate','service',False),edge('fire','south-gate','fire',False)]
 return {'schemaVersion':'1.1','districtId':district,'status':'GENERATED_PLAN_ONLY','blockMeters':meters,
  'buildings':[{'id':i,'xy':xy,'height':h,'status':'PLACEHOLDER','layer':'building'} for i,xy,h in buildings],
  'metrics':metrics,'streetGraph':{'nodes':nodes,'edges':edges},
  'layers':{'building':True,'street':True,'publicRealm':True,'pedestrianRoute':True,'vehicleRoute':True,'fireRoute':True},
  'routes':{'pedestrian':['north-gate','center','south-gate'],'vehicle':['north-gate','east-gate','south-gate','west-gate'],'fire':['fire','south-gate'],'service':['service','east-gate']},
  'publicSpace':[{'id':s,'status':'PROTOTYPE','layer':'publicRealm'} for s in spaces]}
def scene(data,root):
 bpy.ops.wm.read_factory_settings(use_empty=True);w,h=data['blockMeters'];box('ground',(0,0,-.5),(w,h,1),(.45,.48,.43));box('perimeter-road',(0,-h/2+12,.05),(w,24,.2),(.12,.13,.14));box('plaza',(0,0,.08),(w*.30,h*.26,.2),(.72,.68,.57))
 for b in data['buildings']:
  x,y=b['xy'];z=b['height']/2;box(b['id'],(x,y,z),(24 if b['height']>100 else 32,24 if b['height']>100 else 28,b['height']),(.50,.58,.63) if b['height']>100 else (.62,.57,.48))
 for x in range(int(-w/2+18),int(w/2-18),24):box('tree',(x,-h/2+30,3),(3,3,6),(.18,.42,.18))
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.world=bpy.data.worlds.new('day');s.world.color=(.20,.24,.30);s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 camd=bpy.data.cameras.new('camera');cam=bpy.data.objects.new('camera',camd);s.collection.objects.link(cam);s.camera=cam;ld=bpy.data.lights.new('sun','SUN');ld.energy=3;light=bpy.data.objects.new('sun',ld);s.collection.objects.link(light);light.rotation_euler=(.5,-.3,-.6)
 views={'hero':(w*.75,-h*.85,max(w,h)*.55),'bird':(0,-h*.1,max(w,h)*1.2),'street':(0,-h*.65,18),'public-space':(0,-h*.25,30),'pedestrian-route':(-w*.25,-h*.4,22),'service-route':(w*.35,h*.35,22),'dusk':(w*.65,-h*.65,45),'plan':(0,0,max(w,h)*1.3),'skyline':(0,-h*.95,65),'status-overlay':(w*.55,h*.55,55)}
 os.makedirs(os.path.join(root,'previews'),exist_ok=True)
 for n,p in views.items():cam.location=p;cam.rotation_euler=(Vector((0,0,30))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=os.path.join(root,'previews',n+'.png');bpy.ops.render.render(write_still=True)
def main():
 a=args();os.makedirs(a.output_root,exist_ok=True);shared={'streetFamily':[{'assetId':x,'status':'PROTOTYPE','lodPolicy':'instanced-LOD','districtCompatibility':['residential','archiveos']} for x in STREET]};json.dump(shared,open(os.path.join(a.output_root,'shared-street-family.json'),'w'),indent=2)
 for kind in ('residential','archiveos'):
  d=os.path.join(a.output_root,kind+'-block');os.makedirs(os.path.join(d,'plan'),exist_ok=True);os.makedirs(os.path.join(d,'reports'),exist_ok=True);data=plan(kind);json.dump(data,open(os.path.join(d,'plan','block-plan.json'),'w'),indent=2);json.dump({'gates':{'Building':72,'Family':70,'Block':84,'Street':82,'District':80,'City':70},'status':'PLAN_ONLY_PROXY'},open(os.path.join(d,'reports','review.json'),'w'),indent=2);scene(data,d)
if __name__=='__main__':main()
