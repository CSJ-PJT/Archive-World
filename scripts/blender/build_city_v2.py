"""Deterministically build Archive City v2 as linked district libraries.
No source GLB is modified. Repeated props use collection instances, never copied meshes.
"""
import bpy, json, os, sys, math
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
repo=Path(args[args.index('--repo')+1]).resolve() if '--repo' in args else Path.cwd()
library=json.loads((repo/'assets/runtime/v2/asset-library.json').read_text(encoding='utf8'))['assets']
paths={a['assetId']:repo/a['runtimePath'] for a in library}
texture_root=repo/'assets/runtime/v2/textures'; texture_root.mkdir(parents=True,exist_ok=True)
districts=['archiveos','market','nexus','logistics','ledger','residential','infrastructure']

# district, instance id, asset, x, z, target footprint, rotation radians, state
P=[
('archiveos','control-tower','building-archiveos-2e8c32fa',0,0,32,0,'hub'),('archiveos','ai-center','building-archive-15186c21',28,8,25,.2,'hub'),('archiveos','security-center','building-archiveos2-a614889b',-28,-10,24,-.3,'hub'),
('market','commerce-hub','building-market-9badf3fa',-128,-10,32,0,'commercial'),('market','order-center','building-market-181c8568',-102,18,30,.3,'commercial'),('market','retail-tower','building-1-d57f1be7',-145,24,18,0,'commercial'),('market','delivery-van','vehicle-asset-535bcba9',-116,-28,8,0,'parking'),
('nexus','smart-factory','building-nexus-5b2737a0',-25,128,40,0,'production'),('nexus','process-a','building-a-2-0e6498d0',-58,113,28,.2,'production'),('nexus','process-b','building-b-0da0b3c5',8,112,28,-.2,'production'),('nexus','maintenance','building-c-f2297019',-10,158,30,0,'production'),('nexus','agv','vehicle-agv-platform-v1',-45,144,7,0,'loading'),
('logistics','distribution','building-archive-logistics-4cd90681',125,20,44,0,'dock'),('logistics','truck-terminal','building-archive-1-ea52880d',155,44,34,.2,'dock'),('logistics','cold-storage','building-archive-2-2fe57f23',96,52,32,0,'dock'),('logistics','container-yard','container-yard-modular-v1',150,-20,30,0,'yard'),('logistics','dock-module','cold-storage-loading-dock-v1',100,-10,22,0,'dock'),('logistics','forklift','vehicle-forklift-industrial-v1',128,-4,7,0,'loading'),('logistics','truck-drive','vehicle-1-a74d9cb9',72,17,11,.4,'driving'),('logistics','truck-dock','vehicle-2-49e64913',116,5,11,0,'dock'),
('ledger','settlement','building-ledger-181c8568',12,-130,34,0,'settlement'),('ledger','audit','building-ledger2-ea294a50',-23,-148,24,.2,'office'),('ledger','finance-a','building-2-cfee9093',42,-145,20,0,'office'),('ledger','finance-b','building-7-d09a344b',60,-118,18,0,'office'),('ledger','office-car','vehicle-asset-535bcba9',20,-105,7,0,'parking'),
('residential','apartment-a','building-3-3d248d87',-148,118,20,0,'residential'),('residential','apartment-b','building-4-874697a4',-120,118,22,0,'residential'),('residential','apartment-c','building-5-8ec67334',-148,148,20,0,'residential'),('residential','apartment-d','building-6-c55667d3',-120,148,20,0,'residential'),('residential','apartment-e','building-3-3d248d87',-92,118,19,0,'residential'),('residential','apartment-f','building-5-8ec67334',-92,148,19,0,'residential'),('residential','resident-car-a','vehicle-asset-535bcba9',-132,95,7,0,'parking'),('residential','resident-car-b','vehicle-3-234d82b4',-106,95,7,0,'parking'),
('infrastructure','power','power-substation-compact-v1',45,76,20,0,'utility'),('infrastructure','comms','communications-tower-compact-v1',18,83,18,0,'utility'),('infrastructure','gate','security-gate-road-lane-v1',76,62,20,0,'gate'),('infrastructure','barrier','roadside-safety-barrier-v1',60,92,24,0,'safety'),('infrastructure','streetlight-a','streetlight-traffic-signal-v1',-20,60,8,0,'street'),('infrastructure','streetlight-b','streetlight-traffic-signal-v1',38,-52,8,0,'street'),
]
N=[('central',0,40),('market',-78,32),('marketWest',-140,5),('nexus',-25,82),('nexusNorth',-30,145),('logistics',72,35),('logisticsEast',145,36),('ledger',10,-72),('ledgerSouth',15,-142),('residential',-105,80),('residentialNorth',-120,140),('utility',40,75)]
E=[('central','market','arterial',4,'both','primary','archiveos'),('market','marketWest','service',2,'both','local','market'),('central','nexus','arterial',4,'both','primary','archiveos'),('nexus','nexusNorth','industrial',4,'both','freight','nexus'),('central','logistics','arterial',4,'both','freight','logistics'),('logistics','logisticsEast','industrial',4,'both','freight','logistics'),('central','ledger','arterial',4,'both','primary','ledger'),('ledger','ledgerSouth','urban',4,'both','urban','ledger'),('market','residential','urban',2,'both','local','residential'),('residential','residentialNorth','residential',2,'both','slow','residential'),('nexus','residentialNorth','service',2,'both','local','residential'),('nexus','utility','service',2,'both','industrial','infrastructure'),('utility','logistics','service',2,'both','industrial','infrastructure'),('central','utility','arterial',4,'both','primary','infrastructure'),('market','ledger','arterial',4,'both','primary','market'),('logistics','ledger','arterial',4,'both','primary','logistics')]

def purge():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for x in list(bpy.data.meshes):
        if x.users==0: bpy.data.meshes.remove(x)

def collection_bounds(col):
    pts=[]
    for o in col.all_objects:
        if o.type=='MESH':
            for v in o.bound_box: pts.append(o.matrix_world@Vector(v))
    if not pts:return Vector((0,0,0)),Vector((1,1,1))
    return Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))),Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))

def asset_collection(asset_id):
    col=bpy.data.collections.new('Asset_'+asset_id); before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(paths[asset_id])); imported=[o for o in bpy.data.objects if o not in before]
    for o in imported:
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
    lo,hi=collection_bounds(col); center=(lo+hi)/2
    for o in imported:
        if o.parent is None: o.location-=Vector((center.x,center.y,lo.z))
    return col

def add_instance(district, sources, item):
    _,iid,asset,x,z,foot,rot,state=item
    if asset not in sources: sources[asset]=asset_collection(asset)
    low,high=collection_bounds(sources[asset]); span=max(high.x-low.x,high.y-low.y,.01)
    o=bpy.data.objects.new('Instance_'+iid,None); district.objects.link(o); o.instance_type='COLLECTION'; o.instance_collection=sources[asset]
    o.location=(x,z,0); o.scale=(foot/span,)*3; o.rotation_euler[2]=rot
    o['instanceId']=iid;o['assetId']=asset;o['district']=district['district'];o['state']=state;o['instanceMode']='COLLECTION_INSTANCE'

def add_camera_light(collection, name, preview):
    lo,hi=collection_bounds(collection); center=(lo+hi)/2; span=max((hi-lo).x,(hi-lo).y,40); camd=bpy.data.cameras.new('Camera_'+name); cam=bpy.data.objects.new('Camera_'+name,camd); bpy.context.scene.collection.objects.link(cam); cam.location=center+Vector((span*1.25,-span*1.25,span*.95));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=38;bpy.context.scene.camera=cam
    if name=='city':
        center=Vector((0,0,0)); span=420; cam.location=center+Vector((span*.82,-span*.82,span*.72)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    sun=bpy.data.lights.new('Sun_'+name,'SUN');sun.energy=3;so=bpy.data.objects.new('Sun_'+name,sun);bpy.context.scene.collection.objects.link(so);so.rotation_euler=(.55,-.3,.65)
    bpy.context.scene.render.engine='BLENDER_EEVEE_NEXT'; bpy.context.scene.render.resolution_x=1600;bpy.context.scene.render.resolution_y=1000;bpy.context.scene.render.resolution_percentage=100
    if bpy.context.scene.world is None:
        bpy.context.scene.world=bpy.data.worlds.new('ArchiveCityV2World')
    bpy.context.scene.world.color=(.05,.08,.11);bpy.context.scene.render.filepath=str(preview);bpy.ops.render.render(write_still=True)

def build_district(name):
    purge(); district=bpy.data.collections.new('DISTRICT_'+name);district['district']=name;bpy.context.scene.collection.children.link(district);sources={}
    for item in [x for x in P if x[0]==name]:add_instance(district,sources,item)
    if name=='infrastructure':
        nodes={k:Vector((x,z,0)) for k,x,z in N}; road='road-meshy-ai-divided-highway-0713093526-texture-b5202be0'
        for idx,(a,b,*_) in enumerate(E):
            if road not in sources:sources[road]=asset_collection(road)
            lo,hi=collection_bounds(sources[road]);base=max(hi.y-lo.y,.01);start,end=nodes[a],nodes[b];delta=end-start;o=bpy.data.objects.new('Road_'+str(idx),None);district.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=sources[road];o.location=(start+end)/2;o.scale=(9/base,delta.length/base,9/base);o.rotation_euler[2]=math.atan2(-delta.x,delta.y);o['instanceId']='road-'+str(idx);o['assetId']=road;o['district']='infrastructure';o['instanceMode']='COLLECTION_INSTANCE'
    preview=repo/'assets/previews/v2'/f'{name}-overview.png';preview.parent.mkdir(parents=True,exist_ok=True);add_camera_light(district,name,preview)
    scene_file=repo/'scenes/v2'/f'{name}.blend';scene_file.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(scene_file)); bpy.ops.file.unpack_all(method='WRITE_LOCAL'); bpy.ops.wm.save_as_mainfile(filepath=str(scene_file)); bpy.ops.export_scene.gltf(filepath=str(repo/'assets/runtime/v2'/f'{name}.glb'),export_format='GLB',use_selection=False,export_apply=True)
    return {'id':name,'runtimePath':f'assets/runtime/v2/{name}.glb','previewPath':f'assets/previews/v2/{name}-overview.png','blendPath':f'scenes/v2/{name}.blend'}

results=[build_district(d) for d in districts]
# lightweight master: only linked district collections, never packed geometry/images.
bpy.ops.wm.read_factory_settings(use_empty=True); master=bpy.data.collections.new('ARCHIVE_CITY_V2_LINKED');bpy.context.scene.collection.children.link(master)
for d in districts:
    with bpy.data.libraries.load(str(repo/'scenes/v2'/f'{d}.blend'),link=True) as (src,dst): dst.collections=['DISTRICT_'+d]
    linked=dst.collections[0]; o=bpy.data.objects.new('LinkedDistrict_'+d,None);master.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=linked
preview=repo/'assets/previews/v2'/'city-overview.png';add_camera_light(master,'city',preview)
bpy.ops.wm.save_as_mainfile(filepath=str(repo/'scenes/archive-city-v2.blend'))
# Road-network preview reuses master camera and actual linked infrastructure.
bpy.context.scene.render.filepath=str(repo/'assets/previews/v2'/'road-network-overview.png');bpy.ops.render.render(write_still=True)
layout={'version':'2.0.0','districts':districts,'instances':[{'instanceId':i[1],'assetId':i[2],'district':i[0],'position':[i[3],0,i[4]],'rotation':[0,i[6],0],'runtimePath':'assets/runtime/v2/library/'+i[2]+'.glb','state':i[7]} for i in P],'roadTopology':{'nodes':[{'nodeId':a,'position':[x,0,z]} for a,x,z in N],'edges':[{'edgeId':'edge-'+str(i),'from':a,'to':b,'roadType':t,'laneCount':lanes,'direction':direction,'speedClass':speed,'district':district,'vehicleAllowed':True} for i,(a,b,t,lanes,direction,speed,district) in enumerate(E)]}}
(repo/'assets/world/archive-city-v2-layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf8')
(repo/'assets/runtime/v2/archive-city-v2-manifest.json').write_text(json.dumps({'version':'2.0.0','districts':results,'masterBlend':'scenes/archive-city-v2.blend','layout':'assets/world/archive-city-v2-layout.json'},indent=2)+'\n',encoding='utf8')
print('ARCHIVE_CITY_V2='+json.dumps({'districts':len(results),'instances':len(P),'roads':len(E)}))
