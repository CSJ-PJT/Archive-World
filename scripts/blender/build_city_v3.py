"""Deterministically assemble Archive City v3.0 Geography Edition.

v2 files are read-only inputs. District scenes use collection instances and the
master scene links district collections, so neither source GLBs nor v2 scenes are
rewritten or packed into the v3 master.
"""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
repo=Path(args[args.index('--repo')+1]).resolve() if '--repo' in args else Path.cwd()
library=json.loads((repo/'assets/runtime/v3/asset-library.json').read_text(encoding='utf8'))['assets']
paths={item['assetId']:repo/item['runtimePath'] for item in library}
asset_libraries=json.loads((repo/'scenes/v3/asset-libraries-v3.json').read_text(encoding='utf8'))['libraries']
library_paths={item['assetId']:repo/item['libraryPath'] for item in asset_libraries}
districts=['archiveos','market','nexus','logistics','ledger','residential','infrastructure']
P=[]
def add(district,iid,asset,x,z,foot,rot=0,state='building'):
    P.append((district,iid,asset,x,z,foot,rot,state))

# North-bank CBD: distinct landmark trio plus a dense, walkable office ring.
add('archiveos','archiveos-control-tower','building-archiveos-2e8c32fa',0,1520,42,0,'landmark')
add('archiveos','archiveos-ai-center','building-archive-15186c21',110,1580,30,.12,'building')
add('archiveos','archiveos-security-center','building-archiveos2-a614889b',-115,1450,30,-.12,'building')
add('archiveos','archiveos-plaza','archiveos-landmark-plaza-v2',0,1400,54,0,'plaza')
for row,z in enumerate((1370,1470,1620)):
    for col,x in enumerate((-220,-150,150,220)):
        add('archiveos',f'archiveos-office-{row}-{col}','building-1-d57f1be7' if (row+col)%2 else 'building-2-cfee9093',x,z,24,(col%2)*.12,'building')

# South-west Market: mixed commercial blocks, low retail, service yards and vans.
for idx,(asset,x,z,foot) in enumerate([
 ('building-market-9badf3fa',-1950,-1460,42),('building-market-181c8568',-1760,-1390,36),('building-7-d09a344b',-2110,-1320,26),('building-1-d57f1be7',-1640,-1280,26)]):
    add('market',f'market-anchor-{idx}',asset,x,z,foot,0,'building')
for row,z in enumerate((-1700,-1570,-1260)):
    for col,x in enumerate((-2220,-2080,-1880,-1700)):
        asset='neighborhood-shop-v3' if (row+col)%3 else 'building-2-cfee9093'
        add('market',f'market-block-{row}-{col}',asset,x,z,34,(col%2)*.15,'building')
add('market','market-riverfront-park','riverfront-park-v3',-2050,-190,420,0,'park')

# Southern Nexus: clusters of actual factory assets and reusable process sheds.
for idx,(asset,x,z,foot) in enumerate([
 ('building-nexus-5b2737a0',420,-1800,54),('building-nexus-9adda402',630,-1710,42),('building-a-2-0e6498d0',250,-1900,38),('building-b-0da0b3c5',820,-1880,38),('building-c-f2297019',420,-2070,38)]):
    add('nexus',f'nexus-anchor-{idx}',asset,x,z,foot,idx*.1,'building')
for row,z in enumerate((-2250,-2100,-1950,-1650)):
    for col,x in enumerate((120,300,520,720)):
        add('nexus',f'nexus-process-{row}-{col}','industrial-shed-v3',x,z,76,(row%2)*.12,'building')

# South-east Logistics: larger warehouse repetition, docks, container/port connection.
for idx,(asset,x,z,foot) in enumerate([
 ('building-archive-logistics-4cd90681',2420,-1450,60),('building-archive-1-ea52880d',2630,-1580,48),('building-archive-2-2fe57f23',2250,-1720,44),('container-yard-modular-v1',2780,-1350,44),('cold-storage-loading-dock-v1',2380,-1610,34)]):
    add('logistics',f'logistics-anchor-{idx}',asset,x,z,foot,0,'building')
for row,z in enumerate((-2050,-1860,-1680)):
    for col,x in enumerate((2180,2400,2630,2860)):
        add('logistics',f'logistics-warehouse-{row}-{col}','warehouse-shed-v3',x,z,98,(row%2)*.1,'building')
add('logistics','logistics-riverfront-park','riverfront-park-v3',2120,-60,420,0,'park')

# North-west Ledger: ordered financial blocks and a central settlement tower.
for idx,(asset,x,z,foot) in enumerate([
 ('building-ledger-181c8568',-1640,1830,44),('building-ledger2-ea294a50',-1810,1700,34),('building-2-cfee9093',-1460,1690,30),('building-7-d09a344b',-1430,1930,28)]):
    add('ledger',f'ledger-anchor-{idx}',asset,x,z,foot,0,'building')
for row,z in enumerate((1560,1770,1990)):
    for col,x in enumerate((-1980,-1850,-1710,-1520)):
        add('ledger',f'ledger-office-{row}-{col}','building-1-d57f1be7' if (row+col)%2 else 'building-2-cfee9093',x,z,24,.08,'building')
add('ledger','ledger-riverfront-park','riverfront-park-v3',-1510,140,420,0,'park')

# North-east Residential: 40+ apartment/low-rise instances in separated blocks.
apartment_assets=['building-3-3d248d87','building-4-874697a4','building-5-8ec67334','building-6-c55667d3','residential-slab-v3']
for row,z in enumerate((1500,1660,1820,2020,2190,2360)):
    for col,x in enumerate((1780,1940,2100,2290,2480,2660)):
        asset=apartment_assets[(row*3+col)%len(apartment_assets)]
        add('residential',f'residential-tower-{row}-{col}',asset,x,z,44,(col%2)*.1,'building')
for row,z in enumerate((1420,2450)):
    for col,x in enumerate((1850,2080,2320,2550)):
        add('residential',f'residential-shop-{row}-{col}','neighborhood-shop-v3',x,z,42,0,'building')
add('residential','residential-central-park','urban-park-v2',2220,1920,80,0,'park')

# Fill each functional district at city scale. These are collection instances of
# existing GLBs or the lightweight v3 civic modules; no source geometry is copied.
for district,asset,x0,z0,columns,rows,step_x,step_z,foot in [
 ('archiveos','building-1-d57f1be7',-520,1180,6,5,180,165,28),
 ('market','neighborhood-shop-v3',-2700,-2250,7,6,185,190,42),
 ('nexus','industrial-shed-v3',-160,-2700,8,7,190,190,82),
 ('logistics','warehouse-shed-v3',1700,-2500,8,7,205,205,104),
 ('ledger','building-2-cfee9093',-2450,1250,6,6,180,180,28),
 ('residential','residential-slab-v3',1350,1120,9,9,185,175,46),
]:
    for row in range(rows):
        for col in range(columns):
            if (row+col)%5==0 and district in ('archiveos','ledger'): continue
            add(district,f'{district}-density-{row:02d}-{col:02d}',asset,x0+col*step_x,z0+row*step_z,foot,((row+col)%3)*.08,'building')

# Functional density is layered per district rather than simply repeating one
# landmark. These collection instances deliberately mix heights, footprints and
# civic/industrial support uses.
for row,z in enumerate((980,1160,1810,1990,2170)):
    for col,x in enumerate((-700,-520,-340,340,520,700)):
        add('archiveos',f'archiveos-midrise-{row}-{col}','cbd-midrise-v3' if (row+col)%3 else 'cbd-support-v3',x,z,42+(row%2)*6,(col%3-.8)*.09,'building')
for x,z in ((-90,1320),(100,1320),(-110,1680),(120,1680)):
    add('archiveos',f'archiveos-parking-{x}-{z}','parking-lot-v3',x,z,58,0,'prop')

for row,z in enumerate((-2350,-2120,-1880,-1150,-980)):
    for col,x in enumerate((-2720,-2500,-2280,-2060,-1840,-1620)):
        asset=('commercial-mall-v3','retail-row-v3','neighborhood-shop-v3')[(row+col)%3]
        add('market',f'market-retail-{row}-{col}',asset,x,z,62 if asset=='commercial-mall-v3' else 42,(row%3)*.12,'building')
for x,z in ((-2500,-1500),(-2280,-1500),(-1840,-1500),(-1620,-1500)):
    add('market',f'market-parking-{x}','parking-lot-v3',x,z,58,0,'prop')

for row,z in enumerate((-3000,-2800,-2500,-1450,-1300)):
    for col,x in enumerate((-300,-80,140,360,580,800,1020)):
        asset=('industrial-utility-v3','process-tank-v3','pipe-rack-v3','industrial-shed-v3')[(row+col)%4]
        add('nexus',f'nexus-module-{row}-{col}',asset,x,z,74 if asset!='pipe-rack-v3' else 68,(col%3)*.12,'building')
for x,z in ((-120,-2080),(240,-2080),(600,-2080),(960,-2080)):
    add('nexus',f'nexus-industrial-parking-{x}','parking-lot-v3',x,z,58,0,'prop')

for row,z in enumerate((-2900,-2700,-2400,-1250,-1080)):
    for col,x in enumerate((1700,1940,2180,2420,2660,2900,3140)):
        asset=('crossdock-v3','warehouse-shed-v3','container-stack-v3')[(row+col)%3]
        add('logistics',f'logistics-module-{row}-{col}',asset,x,z,108 if asset=='crossdock-v3' else 90,(row%2)*.08,'building')
for x,z in ((1880,-2300),(2200,-2300),(2520,-2300),(2840,-2300),(3060,-2300)):
    add('logistics',f'logistics-truck-yard-{x}','parking-lot-v3',x,z,68,0,'prop')

for row,z in enumerate((900,1120,2300,2500,2700)):
    for col,x in enumerate((-2700,-2500,-2300,-2100,-1900,-1500,-1300)):
        add('ledger',f'ledger-finance-{row}-{col}','cbd-midrise-v3' if (row+col)%2 else 'building-2-cfee9093',x,z,36+(col%3)*4,(row%3)*.10,'building')
for x,z in ((-2300,1800),(-2080,1800),(-1850,1800),(-1620,1800)):
    add('ledger',f'ledger-civic-parking-{x}','parking-lot-v3',x,z,52,0,'prop')

for row,z in enumerate((1100,1300,1500,1700,2100,2300,2550,2750)):
    for col,x in enumerate((1200,1420,1640,1860,2080,2320,2560,2800,3040)):
        asset=('residential-tower-v3','residential-midrise-v3','residential-slab-v3','building-3-3d248d87','building-4-874697a4')[(row*2+col)%5]
        add('residential',f'residential-neighborhood-{row}-{col}',asset,x,z,48+(row%3)*5,(col%4)*.08,'building')
for idx,(asset,x,z,foot) in enumerate([
    ('residential-school-v3',1450,2050,82),('residential-school-v3',2840,1450,82),('residential-playground-v3',1750,1500,64),('residential-playground-v3',2450,2300,64),
    ('urban-park-v2',2100,2700,96),('parking-lot-v3',1500,1200,58),('parking-lot-v3',2600,1850,58),('neighborhood-shop-v3',2000,1080,48)]):
    add('residential',f'residential-civic-{idx}',asset,x,z,foot,0,'park' if 'park' in asset or 'playground' in asset else 'prop')

# Metropolitan realism pass: district surfaces establish a legible public realm
# below the linked collections.  They sit just below streets/buildings and do
# not embed or copy any source mesh or texture.
for district,asset,x,z,foot in [
 ('archiveos','cbd-ground-v3',0,1520,1850),('market','market-ground-v3',-2050,-1650,1900),
 ('nexus','nexus-ground-v3',420,-2050,2200),('logistics','logistics-ground-v3',2500,-1900,2300),
 ('ledger','ledger-ground-v3',-1850,1850,1850),('residential','residential-ground-v3',2200,1950,2300),
 ('infrastructure','port-ground-v3',-3350,540,1200),
]: add(district,f'{district}-district-ground',asset,x,z,foot,0,'terrain')

# ArchiveOS: one retained landmark and an intentionally lower office ring.
for row,z in enumerate((720,900,1080,1940,2120,2300)):
    for col,x in enumerate((-840,-640,-440,440,640,840,1040)):
        asset=('cbd-midrise-v3','cbd-support-v3','building-2-cfee9093')[(row+col)%3]
        add('archiveos',f'archiveos-metro-{row}-{col}',asset,x,z,38+(row%3)*4,((row-col)%4)*.06,'building')

# Market: mixed mid-rise commerce and low retail streets rather than warehouse rows.
for row,z in enumerate((-2600,-2420,-2240,-1060,-880,-700)):
    for col,x in enumerate((-2860,-2660,-2460,-2260,-2060,-1860,-1660)):
        asset=('retail-row-v3','neighborhood-shop-v3','commercial-mall-v3','cbd-support-v3')[(row+col)%4]
        add('market',f'market-metro-{row}-{col}',asset,x,z,58 if asset=='commercial-mall-v3' else 38,((row+col)%5)*.05,'building')

# Nexus: separate factory halls, warehouse sheds and process/utility equipment.
for row,z in enumerate((-3300,-3100,-1400,-1200)):
    for col,x in enumerate((-420,-180,60,300,540,780,1020,1260)):
        add('nexus',f'nexus-factory-{row}-{col}','industrial-shed-v3' if (row+col)%2 else 'industrial-utility-v3',x,z,78,((row-col)%3)*.08,'building')
for row,z in enumerate((-2850,-1550,-1120)):
    for col,x in enumerate((-360,-80,200,480,760,1040)):
        add('nexus',f'nexus-warehouse-{row}-{col}','warehouse-shed-v3',x,z,82,(col%3)*.07,'building')
for idx,(x,z) in enumerate([(-240,-2450),(0,-2450),(240,-2450),(480,-2450),(720,-2450),(960,-2450),(1200,-2450),(-120,-1750),(360,-1750),(840,-1750)]):
    add('nexus',f'nexus-utility-{idx}','process-tank-v3' if idx%2 else 'pipe-rack-v3',x,z,66,idx*.12,'building')

# Logistics: separated cross-dock halls, storage sheds and port-facing container yards.
for row,z in enumerate((-3300,-3050,-950,-760)):
    for col,x in enumerate((1650,1910,2170,2430,2690,2950)):
        add('logistics',f'logistics-crossdock-{row}-{col}','crossdock-v3' if (row+col)%2 else 'warehouse-shed-v3',x,z,104,((row-col)%3)*.05,'building')
for row,z in enumerate((-2800,-2480)):
    for col,x in enumerate((1740,1990,2240,2490,2740,2990,3240,3490,3740,3990,4240,4490,4740)):
        add('logistics',f'logistics-container-{row}-{col}','container-stack-v3',x,z,84,(col%3)*.10,'building')

# Ledger: an orderly financial skyline distinct from the ArchiveOS landmark ring.
for row,z in enumerate((720,940,2600,2820,3040)):
    for col,x in enumerate((-2860,-2640,-2420,-2200,-1980,-1760,-1540)):
        asset='building-2-cfee9093' if (row+col)%3 else 'cbd-midrise-v3'
        add('ledger',f'ledger-metro-{row}-{col}',asset,x,z,35+(col%2)*5,(row%3)*.06,'building')

# West Sea/Port gains independent docks, warehouses and container stacks; it
# remains a coastal logistics satellite, linked to the city by the freight road.
for row,z in enumerate((-250,40,330,620)):
    for col,x in enumerate((-4100,-3880,-3660,-3440,-3220,-3000)):
        asset=('warehouse-shed-v3','container-stack-v3','port-crane-v3')[(row+col)%3]
        add('infrastructure',f'port-metro-{row}-{col}',asset,x,z,90 if asset=='warehouse-shed-v3' else 68,(col%3)*.08,'building')
for idx,(x,z) in enumerate([(-3980,850),(-3740,850),(-3500,850),(-3260,850),(-3020,850),(-3920,1080),(-3620,1080),(-3320,1080),(-3020,1080),(-3820,-500),(-3480,-500),(-3140,-500)]):
    add('infrastructure',f'port-yard-{idx}','container-stack-v3',x,z,72,idx*.11,'building')

# Public realm expansion: planted buffers, street lighting, parking and park
# modules are collection instances and intentionally vary their grid offsets.
PUBLIC_REALM=[
 ('archiveos',0,1520,16,10,160),('market',-2050,-1650,16,12,170),('nexus',420,-2050,12,12,185),
 ('logistics',2500,-1900,12,14,205),('ledger',-1850,1850,14,10,165),('residential',2200,1950,20,22,175),
]
for district,cx,cz,lights,trees,step in PUBLIC_REALM:
    for idx in range(lights):
        angle=(idx*2.399); radius=170+(idx%5)*72
        add(district,f'{district}-metro-light-{idx:02d}','urban-streetlight-v2',cx+math.cos(angle)*radius,cz+math.sin(angle)*radius,10,angle,'light')
    for idx in range(trees):
        angle=(idx*1.71); radius=230+(idx%4)*88
        add(district,f'{district}-metro-tree-{idx:02d}','urban-tree-v2',cx+math.cos(angle)*radius,cz+math.sin(angle)*radius,12,angle,'tree')
for district,cx,cz in [('archiveos',0,1520),('market',-2050,-1650),('nexus',420,-2050),('logistics',2500,-1900),('ledger',-1850,1850),('residential',2200,1950)]:
    for idx,(dx,dz) in enumerate(((-540,-420),(540,-420),(-540,420),(540,420))):
        add(district,f'{district}-metro-parking-{idx}','parking-lot-v3',cx+dx,cz+dz,62,idx*.18,'prop')
    add(district,f'{district}-metro-park','urban-park-v2',cx,cz+560,92,0,'park')

# Resolve measured footprint collisions between the pre-existing density field
# and the metropolitan expansion.  Values are metres in the same 10 km layout.
REPOSITION={
 'residential-density-04-04':(85,0),'residential-density-04-05':(80,0),'residential-density-04-07':(80,0),
 'market-retail-2-1':(0,80),'nexus-module-2-4':(0,100),'nexus-module-2-5':(0,100),
 'nexus-warehouse-1-2':(0,100),'logistics-container-1-4':(0,100),'logistics-module-3-0':(0,120),
 'logistics-module-3-6':(0,120),'residential-neighborhood-1-4':(0,80),
}
P=[(district,iid,asset,x+REPOSITION.get(iid,(0,0))[0],z+REPOSITION.get(iid,(0,0))[1],foot,rot,state) for district,iid,asset,x,z,foot,rot,state in P]

# Shared terrain and public realm. All are separate v3 modules and preserve v2 assets.
for item in [
 ('terrain-geography','terrain-geography-v3',0,0,10000,0,'terrain'),('han-river','han-river-curved-v3',0,0,10000,0,'water'),
 ('west-sea','west-sea-port-v3',-4450,0,10000,0,'sea'),('south-plains','south-plains-v3',700,-4050,10000,0,'plain'),
 ('north-range-a','mountain-range-v3',-2300,3650,920,0,'mountain'),('north-range-b','mountain-range-v3',300,3820,920,.12,'mountain'),('north-range-c','mountain-range-v3',2500,3700,920,-.12,'mountain'),
 ('north-range-d','mountain-variation-v3',-650,4140,1080,-.08,'mountain'),('north-range-e','mountain-variation-v3',1900,4200,1080,.10,'mountain'),
 ('east-range-a','mountain-range-v3',4300,1800,920,math.pi/2,'mountain'),('east-range-b','mountain-range-v3',4400,-400,920,math.pi/2,'mountain'),('east-range-c','mountain-range-v3',4300,-2500,920,math.pi/2,'mountain'),('east-range-d','mountain-variation-v3',4700,700,1080,math.pi/2,'mountain'),
 ('west-port','port-harbor-v3',-3350,400,620,0,'port'),('riverfront-west-north','riverfront-park-v3',-1350,170,420,0,'park'),('riverfront-central-north','riverfront-park-v3',120,250,420,0,'park'),('riverfront-east-north','riverfront-park-v3',1920,430,420,0,'park'),
 ('riverfront-west-south','riverfront-park-v3',-1450,-650,420,0,'park'),('riverfront-central-south','riverfront-park-v3',80,-430,420,0,'park'),('riverfront-east-south','riverfront-park-v3',1940,-190,420,0,'park'),
 ('port-crane-west','port-crane-v3',-3550,760,190,0,'port'),('port-crane-east','port-crane-v3',-3350,760,190,0,'port'),('port-container-west','container-stack-v3',-3350,1040,100,0,'port')]:
    add('infrastructure',item[0],item[1],item[2],item[3],item[4],item[5],item[6])

# A large but instance-only public-realm population: trees, lights and river furniture.
tree_positions=[]
for x in range(-3400,3601,240): tree_positions.extend([(x,3000),(x,2750)])
for z in range(-2600,3001,260): tree_positions.extend([(3650,z),(3850,z)])
for idx,(x,z) in enumerate(tree_positions[:132]): add('infrastructure',f'forest-tree-{idx:03d}','urban-tree-v2',x,z,12,0,'tree')
for idx,(x,z) in enumerate([(-3300,3000),(-2800,3250),(-2000,3450),(-1100,3500),(20,3650),(1150,3550),(2300,3450),(3500,2950),(3900,2200),(3980,1200),(4020,200),(3980,-900),(3880,-1900)]):
    add('infrastructure',f'forest-cluster-{idx:02d}','tree-cluster-v3',x,z,80,idx*.17,'tree')
for row,z in enumerate((-4550,-4150,-3750)):
    for col,x in enumerate((-2100,-1500,-900,-300,300,900,1500,2100,2700)):
        if (row+col)%3: add('infrastructure',f'plain-village-{row}-{col}','village-house-v3',x,z,30,(row%2)*.2,'building')
for idx,x in enumerate(range(-3100,3101,150)):
    add('infrastructure',f'river-light-n-{idx:02d}','urban-streetlight-v2',x,river_y:=(-100+230*math.sin(x/1300)+55*math.sin((x+480)/520)+310),10,0,'light')
    add('infrastructure',f'river-light-s-{idx:02d}','urban-streetlight-v2',x,river_y-620,10,math.pi,'light')

# Vehicles are district-owned instances: travelling, waiting, parking, docked and loading.
vehicle_assets=['vehicle-asset-535bcba9','vehicle-3-234d82b4','vehicle-1-a74d9cb9','vehicle-2-49e64913','vehicle-1-d7e1871c','vehicle-forklift-industrial-v1','vehicle-agv-platform-v1']
vehicle_zones=[
 ('market',-2150,-1780,25),('nexus',180,-2320,25),('logistics',2200,-2200,45),
 ('ledger',-2000,1450,15),('residential',1760,1320,40),('infrastructure',-3500,520,10),
]
vehicle_index=0
for district,bx,bz,count in vehicle_zones:
    for local in range(count):
        asset=vehicle_assets[vehicle_index%len(vehicle_assets)]
        # Lane/yard offsets express driving, waiting and docked states without
        # turning collection instances into copied meshes.
        lane=(local%8)*42; row=(local//8)*46
        add(district,f'{district}-vehicle-{vehicle_index:03d}',asset,bx+lane,bz+row,12 if 'truck' in asset else 8,(local%4)*.25,'vehicle')
        vehicle_index+=1

# Local district streets are visible in district previews; global topology is generated below.
for district,bx,bz in [('archiveos',0,1500),('market',-1900,-1500),('nexus',450,-1900),('logistics',2500,-1700),('ledger',-1700,1800),('residential',2200,1900)]:
    for n,(dx,dz,rot) in enumerate(((0,0,0),(110,0,0),(0,110,math.pi/2),(-110,0,0))):
        add(district,f'{district}-local-road-{n}','road-unified-straight-v2',bx+dx,bz+dz,180,rot,'road')
    for n,offset in enumerate((-420,-210,210,420)):
        add(district,f'{district}-avenue-x-{n}','road-unified-straight-v2',bx+offset,bz,760,0,'road')
        add(district,f'{district}-avenue-z-{n}','road-unified-straight-v2',bx,bz+offset,760,math.pi/2,'road')

# Connected city-scale road topology. Roads are 12 m compliant, and bridge segments match the curved river banks.
N=[
 ('archiveos',0,1520),('ledger',-1680,1800),('residential',2200,1900),('market',-1900,-1500),('nexus',450,-1900),('logistics',2500,-1650),('port',-3300,400),
 ('bridgeWestN',-1450,20),('bridgeWestS',-1450,-660),('bridgeCentralN',80,250),('bridgeCentralS',80,-450),('bridgeEastN',1950,440),('bridgeEastS',1950,-170),
 ('outerNW',-3300,3300),('outerNE',3500,3300),('outerSE',3500,-3300),('outerSW',-3300,-3300),('icWest',-2600,-2750),('icEast',2850,-2750),
 ('northHub',600,2600),('southHub',600,-2700),('coastHub',-3050,-500),('eastHub',3300,300),('plainHub',-300,-3200),
]
E=[
 ('archiveos','ledger','arterial',4,'both','primary','ledger'),('archiveos','residential','arterial',4,'both','primary','residential'),('archiveos','northHub','arterial',4,'both','primary','archiveos'),
 ('ledger','bridgeWestN','arterial',4,'both','primary','ledger'),('bridgeWestN','bridgeWestS','bridge',4,'both','bridge','infrastructure'),('bridgeWestS','market','arterial',4,'both','primary','market'),
 ('archiveos','bridgeCentralN','arterial',4,'both','primary','archiveos'),('bridgeCentralN','bridgeCentralS','bridge',4,'both','bridge','infrastructure'),('bridgeCentralS','nexus','industrial',4,'both','freight','nexus'),
 ('residential','bridgeEastN','arterial',4,'both','primary','residential'),('bridgeEastN','bridgeEastS','bridge',4,'both','bridge','infrastructure'),('bridgeEastS','logistics','industrial',4,'both','freight','logistics'),
 ('market','nexus','industrial',4,'both','freight','nexus'),('nexus','logistics','industrial',4,'both','freight','logistics'),('ledger','port','arterial',4,'both','freight','infrastructure'),('port','coastHub','service',2,'both','local','infrastructure'),
 ('coastHub','southHub','highway-link',4,'both','freight','infrastructure'),('southHub','logistics','industrial',4,'both','freight','logistics'),
 ('market','icWest','highway-link',4,'both','highway','infrastructure'),('logistics','icEast','highway-link',4,'both','highway','infrastructure'),('nexus','southHub','highway-link',4,'both','highway','infrastructure'),
 ('outerNW','outerNE','highway-link',4,'both','highway','infrastructure'),('outerNE','outerSE','highway-link',4,'both','highway','infrastructure'),('outerSE','outerSW','highway-link',4,'both','highway','infrastructure'),('outerSW','outerNW','highway-link',4,'both','highway','infrastructure'),
 ('outerNW','ledger','service',2,'both','local','ledger'),('outerNE','residential','service',2,'both','local','residential'),('outerSW','icWest','service',2,'both','local','infrastructure'),('outerSE','icEast','service',2,'both','local','infrastructure'),
 ('coastHub','outerSW','highway-link',4,'both','highway','infrastructure'),('eastHub','outerNE','highway-link',4,'both','highway','infrastructure'),('plainHub','outerSW','highway-link',4,'both','highway','infrastructure'),
]
ROAD_STRAIGHT='road-unified-straight-v2'; ROAD_INTERSECTION='road-unified-intersection-v2'; ROAD_ROUNDABOUT='road-unified-roundabout-v2'; ROAD_CURVE='road-unified-curve90-v2'; ROAD_RAMP='road-unified-ramp-v2'; ROAD_BRIDGE='river-bridge-geography-v3'; ROAD_HIGHWAY='highway-straight-v3'; ROAD_IC='highway-interchange-v3'
ROAD_FEATURES=[
 ('ic-west',ROAD_IC,-2600,-2750,0,1,'infrastructure'),('ic-east',ROAD_IC,2850,-2750,math.pi,1,'infrastructure'),
 ('ic-west-ramp',ROAD_RAMP,-2460,-2700,math.pi/2,8,'infrastructure'),('ic-east-ramp',ROAD_RAMP,2700,-2700,-math.pi/2,8,'infrastructure'),
 ('archive-roundabout',ROAD_ROUNDABOUT,0,1520,0,1,'archiveos'),
]
for x in (-2300,-1900,-1500,-1100,350,750,1150,1550,2050,2450): ROAD_FEATURES.append((f'network-curve-{x}',ROAD_CURVE,x,-1050,0,1,'infrastructure'))

def purge():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections): bpy.data.collections.remove(col)
    for data in list(bpy.data.meshes):
        if data.users==0: bpy.data.meshes.remove(data)
    # Imported GLBs create material/image datablocks. Remove no-user data before
    # the next district so a later Blend does not retain previous district textures.
    for data in list(bpy.data.materials):
        if data.users==0: bpy.data.materials.remove(data)
    for data in list(bpy.data.images):
        if data.users==0: bpy.data.images.remove(data)

def collection_bounds(col):
    points=[]
    def collect(obj,parent=Matrix.Identity(4)):
        matrix=parent@obj.matrix_world
        if obj.type=='MESH':
            for vertex in obj.bound_box: points.append(matrix@Vector(vertex))
        if obj.instance_type=='COLLECTION' and obj.instance_collection:
            for nested in obj.instance_collection.all_objects: collect(nested,matrix)
    for obj in col.all_objects: collect(obj)
    if not points:return Vector((0,0,0)),Vector((1,1,1))
    return Vector((min(p.x for p in points),min(p.y for p in points),min(p.z for p in points))),Vector((max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)))

def source_collection(asset_id):
    if asset_id not in paths or asset_id not in library_paths: raise RuntimeError(f'missing v3 asset library {asset_id}')
    with bpy.data.libraries.load(str(library_paths[asset_id]),link=True) as (source,target):
        target.collections=['ASSET_'+asset_id]
    col=target.collections[0]
    if col is None: raise RuntimeError(f'library collection not found: {asset_id}')
    return col

def add_instance(district,sources,item):
    _,iid,asset,x,z,foot,rot,state=item
    if asset not in sources:sources[asset]=source_collection(asset)
    low,high=collection_bounds(sources[asset]); span=max(high.x-low.x,high.y-low.y,.01)
    obj=bpy.data.objects.new('Instance_'+iid,None); district.objects.link(obj); obj.instance_type='COLLECTION'; obj.instance_collection=sources[asset]
    elevation=-.25 if state=='terrain' else (-.08 if state in ('water','sea') else 0)
    obj.location=(x,z,elevation)
    obj.scale=(1,foot/max(high.y-low.y,.01),1) if state=='road' else (foot/span,)*3
    obj.rotation_euler[2]=rot
    obj['instanceId']=iid; obj['assetId']=asset; obj['district']=district['district']; obj['state']=state; obj['footprintMeters']=foot; obj['instanceMode']='COLLECTION_INSTANCE'

def realtime_render_engine(scene):
    engine_property=scene.render.bl_rna.properties['engine']
    supported={item.identifier for item in engine_property.enum_items}
    for engine in ('BLENDER_EEVEE_NEXT','BLENDER_EEVEE'):
        if engine in supported:
            return engine
    raise RuntimeError('No supported EEVEE render engine is available: '+', '.join(sorted(supported)))

def camera_and_render(collection,name,output):
    # A district holds collection instances.  Bounds gathered from the linked
    # source collections are local to those libraries and therefore cannot
    # describe the district's placement.  Frame the actual instance roots so
    # a reproducible district preview never falls back to the world origin.
    roots=[obj for obj in collection.all_objects if obj.name.startswith(('Instance_','RoadModule_'))]
    if roots:
        min_x,max_x=min(obj.location.x for obj in roots),max(obj.location.x for obj in roots)
        min_y,max_y=min(obj.location.y for obj in roots),max(obj.location.y for obj in roots)
        center=Vector(((min_x+max_x)/2,(min_y+max_y)/2,0))
        span=max(max_x-min_x,max_y-min_y,220)*1.45
    else:
        low,high=collection_bounds(collection); center=(low+high)/2; span=max((high-low).x,(high-low).y,220)
    cam_data=bpy.data.cameras.new('Camera_'+name); cam=bpy.data.objects.new('Camera_'+name,cam_data); bpy.context.scene.collection.objects.link(cam)
    if name=='city': center=Vector((0,0,0)); span=10000; cam.location=center+Vector((span*.74,-span*.80,span*.72)); cam_data.lens=42
    else: cam.location=center+Vector((span*1.18,-span*1.18,span*.85)); cam_data.lens=42
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.clip_start=.1; cam_data.clip_end=max(span*10,30000); bpy.context.scene.camera=cam
    sun_data=bpy.data.lights.new('Sun_'+name,'SUN'); sun_data.energy=3.1; sun=bpy.data.objects.new('Sun_'+name,sun_data); bpy.context.scene.collection.objects.link(sun); sun.rotation_euler=(.55,-.32,.64)
    bpy.context.scene.render.engine=realtime_render_engine(bpy.context.scene); bpy.context.scene.render.resolution_x=1600; bpy.context.scene.render.resolution_y=1000; bpy.context.scene.render.resolution_percentage=100
    if bpy.context.scene.world is None:bpy.context.scene.world=bpy.data.worlds.new('ArchiveCityV3World')
    bpy.context.scene.world.color=(.055,.09,.11); bpy.context.scene.render.filepath=str(output); bpy.ops.render.render(write_still=True)

def build_district(name):
    purge(); district=bpy.data.collections.new('DISTRICT_'+name); district['district']=name; bpy.context.scene.collection.children.link(district); sources={}
    for item in (entry for entry in P if entry[0]==name): add_instance(district,sources,item)
    road_modules=[]
    if name=='infrastructure':
        nodes={node:Vector((x,z,0)) for node,x,z in N}; degree={node:sum(1 for edge in E if node in edge[:2]) for node in nodes}
        def module(mid,asset,location,rotation=0,scale=(1,1,1),owner='infrastructure'):
            if asset not in sources:sources[asset]=source_collection(asset)
            obj=bpy.data.objects.new('RoadModule_'+mid,None); district.objects.link(obj); obj.instance_type='COLLECTION'; obj.instance_collection=sources[asset]; obj.location=location; obj.rotation_euler[2]=rotation; obj.scale=scale
            obj['instanceId']=mid; obj['assetId']=asset; obj['district']=owner; obj['instanceMode']='COLLECTION_INSTANCE'; obj['connectionStandard']='ArchiveRoadV2-12m'
            road_modules.append({'moduleId':mid,'assetId':asset,'position':[round(location.x,3),0,round(location.y,3)],'rotation':[0,0,round(rotation,6)],'district':owner,'connectionStandard':'ArchiveRoadV2-12m'})
        for node,count in degree.items():
            if node=='archiveos':module('junction-archiveos',ROAD_ROUNDABOUT,nodes[node],0,(1,1,1),'archiveos')
            elif count>=3:module('junction-'+node,ROAD_INTERSECTION,nodes[node],0,(1,1,1),'infrastructure')
        for idx,(start_id,end_id,road_type,*_) in enumerate(E):
            start,end=nodes[start_id],nodes[end_id]; delta=end-start; length=delta.length; asset=ROAD_BRIDGE if road_type=='bridge' else (ROAD_HIGHWAY if road_type=='highway-link' else ROAD_STRAIGHT)
            clear=0 if road_type in ('bridge','highway-link') else 16; visible=max(length-clear*2,2); center=start+delta.normalized()*(clear+visible/2)
            if asset not in sources:sources[asset]=source_collection(asset)
            low,high=collection_bounds(sources[asset]); module('road-'+str(idx),asset,center,math.atan2(-delta.x,delta.y),(1,visible/max(high.y-low.y,.01),1),'infrastructure')
        for mid,asset,x,z,rot,scale,owner in ROAD_FEATURES: module(mid,asset,Vector((x,z,0)),rot,(1,scale,1),owner)
    preview=repo/'assets/previews/v3'/f'{name}-overview.png'; preview.parent.mkdir(parents=True,exist_ok=True); camera_and_render(district,name,preview)
    scene_file=repo/'scenes/v3'/f'{name}.blend'; scene_file.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(scene_file)); bpy.ops.export_scene.gltf(filepath=str(repo/'assets/runtime/v3'/f'{name}.glb'),export_format='GLB',use_selection=False,export_apply=True)
    return {'id':name,'runtimePath':f'assets/runtime/v3/{name}.glb','previewPath':f'assets/previews/v3/{name}-overview.png','blendPath':f'scenes/v3/{name}.blend','roadModules':road_modules}

results=[build_district(name) for name in districts]
bpy.ops.wm.read_factory_settings(use_empty=True); master=bpy.data.collections.new('ARCHIVE_CITY_V3_LINKED'); bpy.context.scene.collection.children.link(master)
for name in districts:
    with bpy.data.libraries.load(str(repo/'scenes/v3'/f'{name}.blend'),link=True) as (source,target): target.collections=['DISTRICT_'+name]
    linked=target.collections[0]; obj=bpy.data.objects.new('LinkedDistrict_'+name,None); master.objects.link(obj); obj.instance_type='COLLECTION'; obj.instance_collection=linked
camera_and_render(master,'city',repo/'assets/previews/v3/city-overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(repo/'scenes/archive-city-v3.blend'))
infra=next(item['roadModules'] for item in results if item['id']=='infrastructure')
building_assets={item[2] for item in P if item[7] in ('building','landmark')}; vehicle_count=sum(1 for item in P if item[7]=='vehicle'); prop_count=sum(1 for item in P if item[7] in ('tree','light','park','plaza','port','prop'))
district_statistics={}
for district in districts:
    entries=[item for item in P if item[0]==district]
    district_statistics[district]={
        'buildings':sum(1 for item in entries if item[7] in ('building','landmark')),
        'vehicles':sum(1 for item in entries if item[7]=='vehicle'),
        'propsAndTrees':sum(1 for item in entries if item[7] in ('tree','light','park','plaza','port','prop')),
        'roads':sum(1 for item in entries if item[7]=='road'),
        'total':len(entries),
    }
district_centers={'archiveos':[0,1520],'market':[-2050,-1650],'nexus':[420,-2050],'logistics':[2500,-1900],'ledger':[-1850,1850],'residential':[2200,1950],'port':[-3350,420]}
layout={'version':'3.2.0','districts':districts,'roadConnectionStandard':{'id':'ArchiveRoadV2-12m','widthMeters':12,'surface':'ArchiveRoad_Asphalt_V2','elevationMeters':0},'instances':[{'instanceId':item[1],'assetId':item[2],'district':item[0],'position':[item[3],0,item[4]],'rotation':[0,item[6],0],'footprintMeters':item[5],'runtimePath':str(paths[item[2]].relative_to(repo)).replace('\\','/'),'state':item[7]} for item in P],'roadModules':infra,'roadTopology':{'nodes':[{'nodeId':name,'position':[x,0,z]} for name,x,z in N],'edges':[{'edgeId':'edge-'+str(idx),'from':a,'to':b,'roadType':road_type,'laneCount':lanes,'direction':direction,'speedClass':speed,'district':district,'vehicleAllowed':True,'assetId':ROAD_BRIDGE if road_type=='bridge' else (ROAD_HIGHWAY if road_type=='highway-link' else ROAD_STRAIGHT),'connectionStandard':'ArchiveRoadV2-12m'} for idx,(a,b,road_type,lanes,direction,speed,district) in enumerate(E)]},'geography':{'worldBounds':{'min':[-5000,-5000],'max':[5000,-5000+10000]},'districtCenters':district_centers,'river':{'assetId':'han-river-curved-v3','shape':'curved','orientation':'west-sea-to-east','centerline':[[x,0,round(-100+230*math.sin(x/1300)+55*math.sin((x+480)/520),2)] for x in range(-3800,3801,400)]},'bridges':['road-4','road-7','road-10'],'northMountains':5,'eastMountains':4,'westSea':'west-sea-port-v3','southPlains':'south-plains-v3','outerHighwayModules':['edge-19','edge-20','edge-21','edge-22'],'interchanges':['ic-west','ic-east']},'statistics':{'buildingInstances':sum(1 for item in P if item[7] in ('building','landmark')),'vehicleInstances':vehicle_count,'roadModules':len(infra),'propsAndTrees':prop_count,'totalInstances':len(P),'districts':district_statistics}}
(repo/'assets/world/archive-city-v3-layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf8')
(repo/'assets/runtime/v3/archive-city-v3-manifest.json').write_text(json.dumps({'version':'3.2.0','preloadPolicy':{'overview':'infrastructure','districtDetail':'lazy','lodPolicy':'overview=LOD2; district=LOD0/LOD1 by camera distance'},'districts':results,'masterBlend':'scenes/archive-city-v3.blend','layout':'assets/world/archive-city-v3-layout.json'},indent=2)+'\n',encoding='utf8')
print('ARCHIVE_CITY_V3='+json.dumps({'districts':len(results),'instances':len(P),'roads':len(E),'buildings':layout['statistics']['buildingInstances'],'vehicles':vehicle_count,'roadModules':len(infra),'props':prop_count,'districtStatistics':district_statistics}))
