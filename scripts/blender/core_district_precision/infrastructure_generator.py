"""Actual 3D street, plaza, transit, landscape and population geometry."""
import argparse,json,math,sys
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;PROD=HERE.parent/'production_geometry';sys.path[:0]=[str(PROD),str(HERE.parent)]
from geometry_core import MeshBatch,validate_geometry
from material_library import create_material_library


def add_ellipsoid(batch, role, material, center, radii, segments=12, rings=7):
 cx,cy,cz=center;rx,ry,rz=radii;vertices=[]
 for ring in range(rings+1):
  phi=math.pi*ring/rings
  for segment in range(segments):
   theta=2*math.pi*segment/segments
   vertices.append((cx+rx*math.sin(phi)*math.cos(theta),
                    cy+ry*math.sin(phi)*math.sin(theta),cz+rz*math.cos(phi)))
 faces=[]
 for ring in range(rings):
  for segment in range(segments):
   nxt=(segment+1)%segments;a=ring*segments+segment;b=ring*segments+nxt
   c=(ring+1)*segments+nxt;d=(ring+1)*segments+segment
   faces.extend(((a,b,c),(a,c,d)))
 batch._append(role,material,vertices,faces)


def add_tree(batch,x,y,index):
 h=7.2+(index%5)*.72
 batch.add_cylinder('tree-trunk','wood-accent',(x,y,h*.36),.22+(index%3)*.035,h*.72,10)
 batch.add_cylinder('tree-upper-trunk','wood-accent',(x,y,h*.73),.13+(index%2)*.025,h*.42,10)
 for lobe in range(4+(index%3)):
  angle=(lobe*2.399)+(index%7)*.31;radius=1.0+(lobe%3)*.72
  add_ellipsoid(batch,'tree-crown-lobe','soil',
                (x+math.cos(angle)*radius,y+math.sin(angle)*radius,
                 h+.35*(lobe%2)),
                (1.65+.22*((index+lobe)%3),1.40+.18*(lobe%2),1.28+.20*((index+lobe)%2)))


def add_human(batch,x,y,index):
 outfit=('dark-metal-panel','painted-concrete','light-metal-panel')[index%3]
 batch.add_box('human-torso',outfit,(x,y,1.12),(.44,.28,.82))
 add_ellipsoid(batch,'human-head','painted-concrete',(x,y,1.73),(.20,.19,.23),10,5)
 stride=.16 if index%4==0 else .05
 for side in (-1,1):
  batch.add_box('human-leg','dark-metal-panel',(x+side*.12,y+side*stride,.42),(.14,.16,.72))
  batch.add_box('human-arm',outfit,(x+side*.31,y-side*stride,1.08),(.12,.14,.70))


def add_vehicle(batch,x,y,index,axis='x'):
 body=(4.5,1.9,1.3) if axis=='x' else (1.9,4.5,1.3)
 cabin=(2.4,1.7,.8) if axis=='x' else (1.7,2.4,.8)
 batch.add_box('vehicle-body','dark-metal-panel',(x,y,1),body)
 batch.add_box('vehicle-cabin','residential-glass',(x,y,1.8),cabin)
 for along in (-1.45,1.45):
  for across in (-.94,.94):
   wx,wy=(x+along,y+across) if axis=='x' else (x+across,y+along)
   batch.add_box('vehicle-wheel','dark-metal-panel',(wx,wy,.55),(.62,.18,.62) if axis=='x' else (.18,.62,.62))
 light=(.08,1.2,.32) if axis=='x' else (1.2,.08,.32)
 lx,ly=(x+2.28,y) if axis=='x' else (x,y+2.28)
 batch.add_box('vehicle-light','light-metal-panel',(lx,ly,.98),light)


def add_activity_cluster(batch, center, count, seed, role):
 """Compose a foreground/midground activity room around a real destination."""
 cx,cy=center
 layouts=((0,0),(-2.2,.8),(2.1,-.6),(-4.3,-1.1),(4.4,1.0),
          (-6.4,.4),(6.2,-.7),(-1.0,2.5),(1.4,-2.4),(-7.8,-1.9),(7.6,2.0))
 for index,(dx,dy) in enumerate(layouts[:count]):
  add_human(batch,cx+dx,cy+dy,seed+index)
 return {'role':role,'count':count,'destination':[cx,cy]}

def build(batch):
 # 1.2 km x 1.0 km structured network with raised curbs/sidewalks and physical markings.
 roads=[]
 for y in (-500,-250,250,500):
  batch.add_box('road-asphalt','asphalt',(0,y,.05),(1200,26,.1));roads.append(('EW',y))
  for side in (-1,1):batch.add_box('raised-sidewalk','sidewalk-concrete',(0,y+side*20,.16),(1200,12,.32));batch.add_box('curb','limestone',(0,y+side*13.4,.25),(1200,.8,.5))
  for x in range(-570,571,30):batch.add_box('lane-marking-dash','light-metal-panel',(x,y,.125),(13,.16,.035))
 for x in (-600,-360,-120,120,360,600):
  batch.add_box('road-asphalt','asphalt',(x,0,.055),(28,1000,.11));roads.append(('NS',x))
  for side in (-1,1):batch.add_box('raised-sidewalk','sidewalk-concrete',(x+side*21,0,.16),(13,1000,.32));batch.add_box('curb','limestone',(x+side*14.4,0,.25),(.8,1000,.5))
  for y in range(-465,466,30):batch.add_box('lane-marking-dash','light-metal-panel',(x,y,.13),(.16,13,.035))
 # Raised parcel fields remove the unfinished dark void between streets.  Each
 # cell gets a paved building apron plus a smaller planted courtyard, while
 # service lanes and the public road hierarchy stay exposed.
 parcel_count=0
 for px in (-480,-240,0,240,480):
  for py in (-375,-125,125,375):
   material='plaza-paver' if (parcel_count+int(px))%3 else 'sidewalk-concrete'
   batch.add_box('block-parcel-surface',material,(px,py,.11),(196,205,.22))
   court_x=px+(22 if parcel_count%2 else -24)
   court_y=py+(18 if parcel_count%3 else -16)
   batch.add_box('block-courtyard-groundcover','soil',(court_x,court_y,.25),(42,26,.26))
   batch.add_box('block-courtyard-edge','granite',(court_x,court_y,.36),(45,29,.18))
   batch.add_box('block-courtyard-groundcover','soil',(court_x,court_y,.48),(41,25,.16))
   for seat in (-1,1):batch.add_box('block-courtyard-bench','wood-accent',(court_x+seat*13,court_y,.70),(5.2,.8,.34))
   parcel_count+=1
 # Crosswalks, medians, tactile paving and loading/taxi bays.
 for x in (-600,-360,-120,120,360,600):
  for y in (-500,-250,250,500):
   for stripe in range(-5,6,2):batch.add_box('crosswalk','light-metal-panel',(x+stripe*1.4,y,.13),(1.1,22,.08))
 for y in (-250,250):batch.add_box('median','plaza-paver',(0,y,.3),(1120,3,0.6))
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
   add_tree(batch,x,y,i+abs(int(y)))
 for i in range(42):
  x=-520+(i%14)*80;y=-150+(i//14)*150
  batch.add_box('bench','wood-accent',(x,y,.55),(2.4,.65,.45));batch.add_box('planter','granite',(x+4,y,.55),(3,2,1.1))
 for i in range(80):
  x=-560+(i%20)*58;y=-450+(i//20)*300;batch.add_cylinder('streetlight','painted-steel',(x,y,3.8),.11,7.6,8);batch.add_box('light-head','light-metal-panel',(x,y-0.4,7.5),(.3,1,.25))
 for i in range(60):batch.add_cylinder('bollard','dark-metal-panel',(-240+(i%20)*24,70+(i//20)*65,.45),.11,.9,8)
 for i in range(18):
  x=-220+(i%6)*82;y=78+(i//6)*58;batch.add_box('bicycle-rack','painted-steel',(x,y,.55),(1.8,.18,1.1));batch.add_box('grouped-seating','wood-accent',(x+5,y,.55),(3.2,1.1,.5))
 for x,y in ((-195,165),(215,150),(-40,-190)):
  batch.add_box('wayfinding-blank','light-metal-panel',(x,y,1.6),(1.2,.35,3.2));batch.add_box('kiosk-proxy','curtain-wall-glass',(x+8,y,2.4),(5,4,4.8))
 # Traffic occupies the authored carriageways.  Earlier revisions placed cars
 # on obsolete grid rows, which made them read as scattered props on parcels.
 vehicle_index=0
 for road_y in (-500,-250,250,500):
  for lane in (-1,1):
   for slot in range(5):
    add_vehicle(batch,-430+slot*190,road_y+lane*5.2,vehicle_index,'x');vehicle_index+=1
 for road_x in (-360,360):
  for slot in range(2):
   add_vehicle(batch,road_x+(-5.2 if slot else 5.2),-120+slot*260,vehicle_index,'y');vehicle_index+=1
 add_vehicle(batch,600-5.2,120,vehicle_index,'y');vehicle_index+=1
 # Human life is composed around destinations rather than uniformly scattered.
 activity_specs=(
  ((-150,155),11,100,'archive-plaza-arrival'),
  ((-80,118),10,120,'archive-pavilion-use'),
  ((225,155),11,140,'ledger-lunch'),
  ((295,125),10,160,'ledger-dropoff'),
  ((-42,-205),11,180,'transit-west-entry'),
  ((42,-205),11,200,'transit-east-entry'),
  ((-360,-270),8,220,'boulevard-crossing'),
  ((360,270),8,240,'office-arrival'),
  ((-120,270),5,260,'bus-waiting'),
  ((120,-270),5,280,'bicycle-transfer'),
 )
 activity=[]
 for center,count,seed,role in activity_specs:activity.append(add_activity_cluster(batch,center,count,seed,role))
 return {'roadSegments':10,'intersections':24,'busStops':4,'taxiBays':3,'stationEntrances':2,'trees':'multi-lobe-procedural-varied','vehicles':vehicle_index,'humans':90,'activityClusters':activity,'plazas':2,'parcelFields':parcel_count,'streamRoadConflict':False,'laneMarkingRuns':10,'midDetailPopulation':True,'activityPlacement':'PROGRAMMED_BY_DESTINATION'}

def main():
 v=sys.argv[sys.argv.index('--')+1:];p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);a=p.parse_args(v);bpy.ops.wm.read_factory_settings(use_empty=True)
 mats,_=create_material_library();batch=MeshBatch(mats);metrics=build(batch);objects=batch.finalize();validation=validate_geometry(objects)
 for o in objects:o['actualGeometry']=True;o['canonical']=False;o['status']='GENERATED_CORE_DISTRICT_PILOT'
 out=Path(a.output_root)/'infrastructure';out.mkdir(parents=True,exist_ok=True);glb=out/'core-district-infrastructure.glb'
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_normals=True,export_texcoords=False,export_materials='EXPORT',export_apply=True)
 report={'status':'TECHNICAL_GENERATED','glb':str(glb),'bytes':glb.stat().st_size,'geometry':batch.statistics(),'validation':validation,'metrics':metrics,'proceduralOnly':True,'imageDatablocks':0}
 (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
