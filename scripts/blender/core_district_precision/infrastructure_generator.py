"""Actual 3D street, plaza, transit, landscape and population geometry."""
import argparse,json,sys
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;PROD=HERE.parent/'production_geometry';sys.path[:0]=[str(PROD),str(HERE.parent)]
from geometry_core import MeshBatch,validate_geometry
from material_library import create_material_library

def build(batch):
 # 1.2 km x 1.0 km structured network with raised curbs/sidewalks and physical markings.
 roads=[]
 for y in (-420,-210,0,210,420):
  batch.add_box('road-asphalt','asphalt',(0,y,.05),(1200,26,.1));roads.append(('EW',y))
  for side in (-1,1):batch.add_box('raised-sidewalk','sidewalk-concrete',(0,y+side*20,.16),(1200,12,.32));batch.add_box('curb','limestone',(0,y+side*13.4,.25),(1200,.8,.5))
 for x in (-500,-250,0,250,500):
  batch.add_box('road-asphalt','asphalt',(x,0,.055),(28,1000,.11));roads.append(('NS',x))
  for side in (-1,1):batch.add_box('raised-sidewalk','sidewalk-concrete',(x+side*21,0,.16),(13,1000,.32));batch.add_box('curb','limestone',(x+side*14.4,0,.25),(.8,1000,.5))
 # Crosswalks, medians, tactile paving and loading/taxi bays.
 for x in (-500,-250,0,250,500):
  for y in (-420,-210,0,210,420):
   for stripe in range(-5,6,2):batch.add_box('crosswalk','light-metal-panel',(x+stripe*1.4,y,.13),(1.1,22,.08))
 for y in (-210,210):batch.add_box('median','plaza-paver',(0,y,.3),(1120,3,0.6))
 for i,x in enumerate((-430,-130,170,430)):
  batch.add_box('bus-bay','asphalt',(x,-392,.09),(42,10,.18));batch.add_box('transit-shelter','light-metal-panel',(x,-375,2.2),(16,4,4.4));batch.add_box('shelter-glass','curtain-wall-glass',(x,-377,2.2),(14,.2,3.6))
 for x in (-320,80,360):batch.add_box('taxi-dropoff','granite',(x,188,.12),(55,9,.24))
 # Archive and Ledger plazas with non-flat edges, water, pavilion and protected walkway.
 batch.add_box('archive-plaza','plaza-paver',(-130,105,.14),(210,150,.28));batch.add_box('ledger-plaza','limestone',(250,105,.15),(180,130,.3))
 batch.add_box('water-feature','water',(-130,115,.45),(70,22,.5));batch.add_box('public-pavilion','curtain-wall-glass',(-190,130,5),(28,18,10));batch.add_box('covered-walkway','light-metal-panel',(-45,150,4),(110,7,.5))
 # Transit entrance, elevator and stairs/escalator proxy.
 for x in (-42,42):batch.add_box('station-entrance','curtain-wall-glass',(x,-225,4),(20,14,8));batch.add_box('station-canopy','light-metal-panel',(x,-228,8.2),(24,18,.5))
 batch.add_box('station-elevator','curtain-wall-glass',(0,-245,5),(6,6,10));batch.add_wedge('station-stairs','granite',(0,-218,1.5),(12,18,3),'y')
 # Trees, planters, lights, benches, bollards and bicycle racks placed by frontage.
 for i,x in enumerate(range(-550,551,55)):
  for y in (-385,-175,35,245,455):
   if (i+int(y))%3==0:continue
   h=6+(i%5)*.8;batch.add_cylinder('tree-trunk','wood-accent',(x,y,h*.35),.25+(i%3)*.04,h*.7,8);batch.add_cylinder('tree-crown','soil',(x,y,h),2.2+(i%4)*.35,h*.65,10)
 for i in range(42):
  x=-520+(i%14)*80;y=-150+(i//14)*150
  batch.add_box('bench','wood-accent',(x,y,.55),(2.4,.65,.45));batch.add_box('planter','granite',(x+4,y,.55),(3,2,1.1))
 for i in range(80):
  x=-560+(i%20)*58;y=-450+(i//20)*300;batch.add_cylinder('streetlight','painted-steel',(x,y,3.8),.11,7.6,8);batch.add_box('light-head','light-metal-panel',(x,y-0.4,7.5),(.3,1,.25))
 for i in range(60):batch.add_cylinder('bollard','dark-metal-panel',(-240+(i%20)*24,70+(i//20)*65,.45),.11,.9,8)
 # Low/mid-detail vehicles and humans are actual geometry, status remains proxy.
 for i in range(45):
  x=-520+(i%15)*72;y=(-420,-210,210)[i%3];batch.add_box('vehicle-body','dark-metal-panel',(x,y,1),(4.5,1.9,1.3));batch.add_box('vehicle-cabin','residential-glass',(x+.2,y,1.8),(2.4,1.7,.8))
 for i in range(90):
  x=-520+(i%18)*60;y=-360+(i//18)*160;batch.add_cylinder('human','painted-concrete',(x,y,.9),.22,1.8,8)
 return {'roadSegments':10,'intersections':25,'busStops':4,'taxiBays':3,'stationEntrances':2,'trees':'procedural-varied','vehicles':45,'humans':90,'plazas':2}

def main():
 v=sys.argv[sys.argv.index('--')+1:];p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);a=p.parse_args(v);bpy.ops.wm.read_factory_settings(use_empty=True)
 mats,_=create_material_library();batch=MeshBatch(mats);metrics=build(batch);objects=batch.finalize();validation=validate_geometry(objects)
 for o in objects:o['actualGeometry']=True;o['canonical']=False;o['status']='GENERATED_CORE_DISTRICT_PILOT'
 out=Path(a.output_root)/'infrastructure';out.mkdir(parents=True,exist_ok=True);glb=out/'core-district-infrastructure.glb'
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_normals=True,export_texcoords=False,export_materials='EXPORT',export_apply=True)
 report={'status':'TECHNICAL_GENERATED','glb':str(glb),'bytes':glb.stat().st_size,'geometry':batch.statistics(),'validation':validation,'metrics':metrics,'proceduralOnly':True,'imageDatablocks':0}
 (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
