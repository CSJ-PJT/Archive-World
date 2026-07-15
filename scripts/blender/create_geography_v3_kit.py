"""Create reproducible, texture-free Geography Edition v3 modules.

This script never changes v2 assets. It writes only runtime/v3 and records the
new procedural modules alongside read-only references to the v2 canonical GLBs.
"""
import bpy, hashlib, json, math, sys
from pathlib import Path

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
repo=Path(args[args.index('--repo')+1]).resolve() if '--repo' in args else Path.cwd()
v2_library=json.loads((repo/'assets/runtime/v2/asset-library.json').read_text(encoding='utf8'))['assets']
runtime=repo/'assets/runtime/v3/library'; runtime.mkdir(parents=True,exist_ok=True)
metadata=repo/'assets/metadata/environment/procedural'; metadata.mkdir(parents=True,exist_ok=True)

def clean():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        if mesh.users==0: bpy.data.meshes.remove(mesh)

def material(name,color,metallic=0.0,roughness=.7,emission=None):
    value=bpy.data.materials.get(name) or bpy.data.materials.new(name); value.use_nodes=True
    node=value.node_tree.nodes.get('Principled BSDF'); node.inputs['Base Color'].default_value=color
    node.inputs['Metallic'].default_value=metallic; node.inputs['Roughness'].default_value=roughness
    if emission:
        node.inputs['Emission Color'].default_value=emission; node.inputs['Emission Strength'].default_value=.35
    return value

TERRAIN=material('ArchiveTerrain_V3',(0.11,.18,.13,1))
GRASS=material('ArchiveGrass_V3',(.08,.27,.12,1))
SOIL=material('ArchivePlainSoil_V3',(.20,.17,.09,1))
WATER=material('ArchiveRiver_V3',(.025,.20,.30,1),.15,.24,(.01,.16,.24,1))
SEA=material('ArchiveSea_V3',(.018,.12,.20,1),.18,.28,(.005,.08,.15,1))
ROCK=material('ArchiveMountain_V3',(.17,.24,.19,1))
ROCK_DARK=material('ArchiveMountainDark_V3',(.09,.14,.11,1))
ASPHALT=material('ArchiveAsphalt_V3',(.045,.055,.065,1),.1,.78)
STEEL=material('ArchiveSteel_V3',(.14,.18,.20,1),.72,.29)
GLASS=material('ArchiveGlass_V3',(.11,.30,.37,1),.35,.25,(.03,.18,.22,1))
CONCRETE=material('ArchiveConcrete_V3',(.30,.34,.33,1))
MARK=material('ArchiveRoadMark_V3',(.78,.80,.76,1))
CBD_PAVE=material('ArchiveCBDPaving_V3',(.20,.24,.25,1),.08,.62)
RES_PAVE=material('ArchiveResidentialPaving_V3',(.28,.31,.29,1),.03,.76)
MARKET_PAVE=material('ArchiveMarketPaving_V3',(.25,.22,.24,1),.04,.68)
INDUSTRIAL_PAVE=material('ArchiveIndustrialPaving_V3',(.19,.20,.18,1),.02,.83)
LOGISTICS_PAVE=material('ArchiveLogisticsYard_V3',(.24,.25,.23,1),.02,.85)
LEDGER_PAVE=material('ArchiveLedgerPaving_V3',(.25,.27,.29,1),.08,.58)
PORT_PAVE=material('ArchivePortConcrete_V3',(.23,.25,.24,1),.08,.80)

def cube(name,loc,dims,mat):
    bpy.ops.mesh.primitive_cube_add(location=loc); obj=bpy.context.object; obj.name=name; obj.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); obj.data.materials.append(mat); return obj
def cyl(name,loc,radius,depth,mat,vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    obj=bpy.context.object; obj.name=name; obj.data.materials.append(mat); return obj
def mesh(name,vertices,faces,mat):
    data=bpy.data.meshes.new(name); data.from_pydata(vertices,[],faces); data.materials.append(mat)
    obj=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(obj); return obj

def river_center(x): return -100 + 230*math.sin(x/1300) + 55*math.sin((x+480)/520)
def ribbon(name,xs,lower,upper,z,mat):
    vertices=[]; faces=[]
    for x in xs: vertices.extend([(x,lower(x),z),(x,upper(x),z)])
    for i in range(len(xs)-1):
        a=i*2; faces.append((a,a+2,a+3,a+1))
    return mesh(name,vertices,faces,mat)

def terrain_curved():
    xs=[-3800+i*200 for i in range(44)]
    ribbon('north-bank-terrain',xs,lambda x:river_center(x)+270,lambda x:5000,-.22,TERRAIN)
    ribbon('south-bank-terrain',xs,lambda x:-5000,lambda x:river_center(x)-270,-.22,TERRAIN)
    # Northern and eastern planted buffers make the mountain foothills continuous.
    cube('north-green-belt',(700,3350,.02),(6500,460,.05),GRASS)
    cube('east-green-belt',(4260,400,.02),(420,7000,.05),GRASS)

def river_curved():
    xs=[-3900+i*160 for i in range(50)]
    ribbon('han-river-curved',xs,lambda x:river_center(x)-270,lambda x:river_center(x)+270,.03,WATER)
    # Quiet channel highlight keeps the bend legible in daylight aerial renders.
    ribbon('river-channel-highlight',xs,lambda x:river_center(x)-18,lambda x:river_center(x)+18,.065,GLASS)

def west_sea():
    cube('west-sea',(-4450,0,-.03),(1100,10000,.06),SEA)
    cube('coastal-breakwater',(-3890,400,.12),(360,1500,.24),STEEL)
    cube('coastal-green-edge',(-3650,-950,.04),(220,2100,.08),GRASS)

def south_plain():
    cube('south-plain-base',(700,-4050,.03),(7000,1450,.06),SOIL)
    for x in range(-2500,3600,600):
        cube('field-strip',(x,-4050,.075),(430,1040,.03),GRASS if (x//600)%2 else SOIL)
        cube('field-track',(x+180,-4050,.10),(20,1040,.03),MARK)

def mountain_range():
    # One reusable cluster; the city places it as north and east collection instances.
    for x,y,r,h,mat in [(-220,0,150,560,ROCK_DARK),(-60,40,190,720,ROCK),(140,-20,165,640,ROCK_DARK),(320,30,120,470,ROCK)]:
        bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=r,radius2=0,depth=h,location=(x,y,h/2))
        obj=bpy.context.object; obj.name='lowpoly-mountain'; obj.data.materials.append(mat)
        for dx,dy in ((-r*.45,55),(r*.45,-42)):
            bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=r*.38,radius2=0,depth=h*.55,location=(x+dx,y+dy,h*.275))
            bpy.context.object.name='mountain-foothill'; bpy.context.object.data.materials.append(mat)

def riverfront():
    cube('riverfront-lawn',(0,0,.06),(420,80,.12),GRASS)
    cube('riverfront-promenade',(0,22,.14),(410,10,.05),CONCRETE)
    cube('riverfront-bike',(0,-17,.14),(410,7,.05),GLASS)
    for x in range(-175,176,50):
        cyl('riverfront-tree-planter',(x,-38,.20),9,.25,CONCRETE,12)
        cyl('riverfront-tree',(x,-38,10),2.1,20,ROCK,10)

def bridge():
    cube('bridge-deck',(0,0,.28),(18,620,.45),ASPHALT)
    for y in (-240,-120,0,120,240): cube('bridge-pier',(0,y,-.35),(5,8,.8),CONCRETE)
    for x in (-8.6,8.6): cube('bridge-rail',(x,0,.82),(.25,620,.55),STEEL)
    for y in range(-280,281,32): cube('bridge-mark',(0,y,.53),(.25,14,.03),MARK)

def port_harbor():
    cube('port-quay',(0,0,.10),(520,280,.20),CONCRETE)
    cube('port-water-edge',(0,-160,.05),(520,70,.08),SEA)
    for x in (-185,-60,65,190):
        cube('port-dock-finger',(x,-160,.16),(28,210,.20),CONCRETE)
        cyl('port-crane-column',(x,32,23),4.0,46,STEEL,12); cube('port-crane-boom',(x+32,32,42),(68,5,5),STEEL)
    for x in (-150,-90,-30,30,90,150):
        for y in (80,118): cube('port-container',(x,y,5),(42,24,10),GLASS if (x+y)%3 else CONCRETE)

def apartment_slab():
    cube('apartment-podium',(0,0,2),(56,36,4),CONCRETE)
    cube('apartment-tower',(0,0,39),(34,22,74),GLASS)
    for z in range(12,72,10): cube('apartment-balcony',(0,-11.4,z),(38,.9,1.0),CONCRETE)
    cube('apartment-roof',(0,0,77),(38,26,2),STEEL)

def neighborhood_shop():
    cube('shop-base',(0,0,5),(38,24,10),CONCRETE); cube('shop-glass',(0,-12.2,6),(30,.5,7),GLASS)
    cube('shop-canopy',(0,-15,10),(36,6,1),STEEL)

def industrial_shed():
    cube('factory-base',(0,0,7),(72,46,14),CONCRETE); cube('factory-roof',(0,0,15),(76,50,2),STEEL)
    for x in (-24,0,24): cyl('factory-stack',(x,12,31),3.5,32,STEEL,12)
    cube('factory-loading',(0,-24,4),(60,5,7),ASPHALT)

def warehouse_shed():
    cube('warehouse-base',(0,0,8),(92,58,16),CONCRETE); cube('warehouse-roof',(0,0,17),(96,62,2),STEEL)
    for x in (-34,-17,0,17,34): cube('warehouse-dock',(x,-30,3),(11,2,6),ASPHALT)

# District-density modules. These are deliberately generic functional
# silhouettes, not copies of any photographed building or brand identity.
def cbd_midrise():
    cube('office-podium',(0,0,4),(46,34,8),CONCRETE); cube('office-midrise',(0,0,36),(28,22,62),GLASS)
    for z in range(14,64,11): cube('office-belt',(0,-11.25,z),(31,.55,1.1),STEEL)
    cube('office-roof-garden',(0,0,68),(30,24,1.5),GRASS)
def cbd_support():
    cube('support-base',(0,0,5),(42,30,10),CONCRETE); cube('support-glass',(0,-15.2,7),(32,.5,8),GLASS)
    cube('support-rooftop',(0,0,11),(24,18,2),STEEL)
def commercial_mall():
    cube('mall-base',(0,0,8),(76,56,16),CONCRETE); cube('mall-atrium',(0,-18,17),(48,20,18),GLASS)
    cube('mall-roof',(0,0,17),(80,60,2),STEEL); cube('mall-canopy',(0,-34,7),(68,10,1),GLASS)
def retail_row():
    for x in (-27,-9,9,27):
        cube('retail-shop',(x,0,5),(16,22,10),CONCRETE); cube('retail-window',(x,-11.1,5),(13,.35,6),GLASS)
        cube('retail-awning',(x,-12.5,8),(14,3,.7),STEEL)
def industrial_utility():
    cube('utility-hall',(0,0,8),(58,38,16),CONCRETE)
    for x in (-18,0,18): cyl('utility-stack',(x,5,31),3.2,32,STEEL,12)
    cube('utility-pipe',(0,-16,18),(54,3,3),STEEL)
def process_tank():
    for x in (-18,0,18):
        cyl('process-tank',(x,0,14),11,28,STEEL,20); cyl('tank-cap',(x,0,28.5),5,1.2,ROCK,16)
    cube('tank-walkway',(0,-13,22),(58,3,1),STEEL)
def pipe_rack():
    for z in (5,12,19): cube('pipe-main',(0,0,z),(76,2,2),STEEL)
    for x in (-32,-16,0,16,32):
        cube('rack-post',(x,0,11),(2,2,24),STEEL); cube('rack-cross',(x,0,22),(2,24,1.5),STEEL)
def crossdock():
    cube('crossdock-hall',(0,0,9),(112,70,18),CONCRETE); cube('crossdock-roof',(0,0,19),(116,74,2),STEEL)
    for x in range(-45,46,15):
        cube('dock-north',(x,36,4),(10,2,7),ASPHALT); cube('dock-south',(x,-36,4),(10,2,7),ASPHALT)
def container_stack():
    cube('container-yard',(0,0,.3),(88,62,.6),ASPHALT)
    for row in (-21,-7,7,21):
        for col in (-30,-15,0,15,30): cube('container',(col,row,4),(12,6,8),GLASS if (row+col)%3 else CONCRETE)
def port_crane():
    cube('port-crane-rail',(0,0,.3),(58,18,.6),STEEL)
    for x in (-22,22): cube('port-crane-leg',(x,0,22),(4,5,44),STEEL)
    cube('port-crane-beam',(0,0,43),(56,5,5),STEEL); cube('port-crane-boom',(17,-24,46),(5,50,4),STEEL)
def residential_tower():
    cube('tower-podium',(0,0,3),(46,36,6),CONCRETE); cube('tower-body',(0,0,62),(26,20,112),GLASS)
    for z in range(13,116,12): cube('tower-balcony',(0,-10.4,z),(30,.7,1),CONCRETE)
    cube('tower-roof',(0,0,119),(30,24,2),STEEL)
def residential_midrise():
    cube('midrise-podium',(0,0,2),(62,28,4),CONCRETE); cube('midrise-body',(0,0,28),(52,20,52),GLASS)
    for z in range(10,52,10): cube('midrise-balcony',(0,-10.5,z),(55,.6,1),CONCRETE)
def residential_school():
    cube('school-wing-a',(-18,0,7),(32,28,14),CONCRETE); cube('school-wing-b',(18,0,7),(32,28,14),CONCRETE)
    cube('school-field',(0,-34,.3),(72,30,.6),GRASS); cube('school-gym',(0,20,9),(42,20,18),STEEL)
def residential_playground():
    cube('playground-base',(0,0,.2),(54,38,.4),SOIL)
    cyl('playground-roundabout',(0,0,1),7,1.4,GLASS,16)
    for x in (-18,18): cube('playground-slide',(x,0,4),(5,12,8),STEEL)
def parking_lot():
    cube('parking-asphalt',(0,0,.2),(76,54,.4),ASPHALT)
    for x in range(-30,31,12):
        for y in (-18,18): cube('parking-mark',(x,y,.45),(8,.25,.04),MARK)
def village_house():
    cube('village-home',(0,0,4),(20,16,8),CONCRETE); cube('village-roof',(0,0,9),(23,19,2),ROCK_DARK)
def mountain_variation():
    for x,y,r,h,mat in [(-260,0,210,760,ROCK_DARK),(-30,70,260,980,ROCK),(230,-20,175,650,ROCK_DARK),(410,50,135,480,ROCK)]:
        bpy.ops.mesh.primitive_cone_add(vertices=9,radius1=r,radius2=0,depth=h,location=(x,y,h/2)); bpy.context.object.data.materials.append(mat)
        for dx,dy in ((-r*.52,40),(r*.45,-65)): bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=r*.34,radius2=0,depth=h*.45,location=(x+dx,y+dy,h*.225)); bpy.context.object.data.materials.append(GRASS)
def tree_cluster():
    for x in (-28,-12,5,22):
        for y in (-18,0,18):
            cyl('tree-trunk',(x,y,4),1.0,8,ROCK_DARK,8); bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=8,location=(x,y,12)); bpy.context.object.data.materials.append(GRASS)

def district_ground(name,base,accent):
    # A lightweight, reusable ground plate with pedestrian bands and planted
    # setbacks. These are procedural city surfaces, not photo textures.
    cube(name+'-base',(0,0,-.04),(1000,1000,.08),base)
    cube(name+'-main-avenue',(0,0,.025),(940,44,.03),ASPHALT)
    cube(name+'-cross-avenue',(0,0,.03),(44,940,.03),ASPHALT)
    for offset in (-360,-180,180,360):
        cube(name+'-sidewalk-x',(0,offset,.04),(900,14,.03),accent)
        cube(name+'-sidewalk-y',(offset,0,.04),(14,900,.03),accent)
    for x in range(-390,391,65):
        cube(name+'-lane-mark-'+str(x),(x,0,.06),(26,.45,.025),MARK)
    for y in range(-390,391,65):
        cube(name+'-lane-mark-y-'+str(y),(0,y,.06),(.45,26,.025),MARK)

def cbd_ground(): district_ground('cbd',CBD_PAVE,CONCRETE)
def residential_ground():
    district_ground('residential',RES_PAVE,CONCRETE)
    for x in (-260,0,260): cube('residential-green-'+str(x),(x,260,.05),(180,118,.035),GRASS)
def market_ground(): district_ground('market',MARKET_PAVE,GLASS)
def nexus_ground(): district_ground('nexus',INDUSTRIAL_PAVE,CONCRETE)
def logistics_ground(): district_ground('logistics',LOGISTICS_PAVE,CONCRETE)
def ledger_ground(): district_ground('ledger',LEDGER_PAVE,CONCRETE)
def port_ground(): district_ground('port',PORT_PAVE,CONCRETE)

BUILDERS={
 'terrain-geography-v3':(terrain_curved,'environment','10km curved-river terrain banks'),
 'han-river-curved-v3':(river_curved,'environment','curved Han-scale river surface'),
 'west-sea-port-v3':(west_sea,'environment','western sea and coastal buffer'),
 'south-plains-v3':(south_plain,'environment','southern plain and field patterns'),
 'mountain-range-v3':(mountain_range,'environment','reusable north/east low-poly mountain range'),
 'riverfront-park-v3':(riverfront,'environment','riverfront park, promenade and bicycle lane'),
 'river-bridge-geography-v3':(bridge,'road','12m compatible long river bridge'),
 'port-harbor-v3':(port_harbor,'environment','western marine logistics harbor'),
 'residential-slab-v3':(apartment_slab,'apartment','generic Korean metropolitan apartment silhouette'),
 'neighborhood-shop-v3':(neighborhood_shop,'commercial','generic low-rise neighborhood retail'),
 'industrial-shed-v3':(industrial_shed,'factory','low-poly manufacturing hall and stacks'),
 'warehouse-shed-v3':(warehouse_shed,'warehouse','low-poly warehouse and loading bays'),
 'cbd-midrise-v3':(cbd_midrise,'office','generic mid-rise office block with roof garden'),
 'cbd-support-v3':(cbd_support,'office','generic support office and civic wing'),
 'commercial-mall-v3':(commercial_mall,'commercial','generic mall and covered atrium'),
 'retail-row-v3':(retail_row,'commercial','generic street retail row'),
 'industrial-utility-v3':(industrial_utility,'factory','utility hall, stacks and service pipe'),
 'process-tank-v3':(process_tank,'factory','reusable process tank cluster'),
 'pipe-rack-v3':(pipe_rack,'factory','modular industrial pipe rack'),
 'crossdock-v3':(crossdock,'warehouse','cross-dock hall with loading faces'),
 'container-stack-v3':(container_stack,'warehouse','container stack and paved yard'),
 'port-crane-v3':(port_crane,'environment','generic port gantry crane'),
 'residential-tower-v3':(residential_tower,'apartment','generic metropolitan residential tower'),
 'residential-midrise-v3':(residential_midrise,'apartment','generic mid-rise apartment block'),
 'residential-school-v3':(residential_school,'environment','generic school, gym and playing field'),
 'residential-playground-v3':(residential_playground,'environment','generic residential playground'),
 'parking-lot-v3':(parking_lot,'street-prop','generic marked parking area'),
 'village-house-v3':(village_house,'environment','generic low-density plains village house'),
 'mountain-variation-v3':(mountain_variation,'environment','varied mountain ridge with foothills'),
 'tree-cluster-v3':(tree_cluster,'environment','reusable varied tree cluster'),
 'cbd-ground-v3':(cbd_ground,'environment','procedural CBD stone, asphalt and sidewalk ground'),
 'residential-ground-v3':(residential_ground,'environment','procedural residential paving, grass and internal roads'),
 'market-ground-v3':(market_ground,'environment','procedural commercial paving and pedestrian bands'),
 'nexus-ground-v3':(nexus_ground,'environment','procedural industrial concrete and service lanes'),
 'logistics-ground-v3':(logistics_ground,'environment','procedural logistics yard concrete and truck lanes'),
 'ledger-ground-v3':(ledger_ground,'environment','procedural financial district paving and public realm'),
 'port-ground-v3':(port_ground,'environment','procedural port quay concrete and cargo lanes'),
}

def export(asset_id,builder,category,note):
    clean(); builder()
    for obj in bpy.context.scene.objects: obj.select_set(True)
    target=runtime/f'{asset_id}.glb'
    bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_apply=True)
    payload={'assetId':asset_id,'category':category,'source':'procedural','sourcePath':'scripts/blender/create_geography_v3_kit.py','runtimePath':f'assets/runtime/v3/library/{asset_id}.glb','triangleCount':sum(len(o.data.polygons) for o in bpy.context.scene.objects if o.type=='MESH'),'textureCount':0,'textureBytes':0,'bounds':None,'checksum':hashlib.sha256(target.read_bytes()).hexdigest(),'district':'infrastructure','lodLevels':[0],'license':None,'sourceNote':note}
    (metadata/f'{asset_id}.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf8'); return payload

created=[export(asset,*spec) for asset,spec in BUILDERS.items()]
assets={item['assetId']:item for item in v2_library}
assets.update({item['assetId']:item for item in created})
(repo/'assets/runtime/v3/asset-library.json').parent.mkdir(parents=True,exist_ok=True)
(repo/'assets/runtime/v3/asset-library.json').write_text(json.dumps({'version':'3.0.0','assets':sorted(assets.values(),key=lambda item:item['assetId'])},indent=2)+'\n',encoding='utf8')
print(json.dumps({'geographyV3':'PASS','created':[item['assetId'] for item in created]}))
