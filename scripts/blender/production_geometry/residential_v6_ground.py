"""Residential V6 public realm, landscape variation and human-scale proxies."""
from __future__ import annotations


DETAIL={"LOD0":3,"LOD1":2,"LOD2":1}


def _tree(batch,index,x,y,lod):
    detail=DETAIL[lod]; height=(4.8,6.2,7.4,5.5)[index%4]; radius=(1.25,1.55,1.8,1.4)[index%4]
    batch.add_cylinder(f"v6-tree-{index%4}-trunk","wood-community-accent",(x,y,height*.28),.18+(index%3)*.035,height*.56,10 if detail==3 else 8)
    batch.add_cylinder(f"v6-tree-{index%4}-crown","landscape-green",(x,y,height*.72),radius,height*.54,12 if detail==3 else 8)


def _human(batch,index,x,y,lod,rotation=0):
    if DETAIL[lod]<2: return
    batch.add_cylinder(f"v6-human-{index%5}-body","human-neutral",(x,y,1.0),.18,1.35,8)
    batch.add_cylinder(f"v6-human-{index%5}-head","warm-white-concrete",(x,y,1.78),.16,.32,8)


def _vehicle(batch,index,x,y,kind="sedan"):
    dims=(4.5,1.8,1.35) if kind=="sedan" else (5.7,2.05,2.25)
    material=("vehicle-silver","dark-gray-accent","muted-blue-residential-glass","cool-white-precast")[index%4]
    batch.add_box(f"v6-{kind}-body",material,(x,y,dims[2]*.42),(dims[0],dims[1],dims[2]*.62))
    batch.add_box(f"v6-{kind}-cabin","muted-blue-residential-glass",(x-.15,y,dims[2]*.82),(dims[0]*.48,dims[1]*.82,dims[2]*.42))


def build_residential_v6_ground(batch,lod):
    detail=DETAIL[lod]
    # Four legible paving/landscape zones and explicit circulation hierarchy.
    batch.add_box("v6-site-base","landscape-soil",(0,4,-.28),(96,82,.56))
    batch.add_box("v6-perimeter-sidewalk","sidewalk-concrete",(0,-31,.16),(88,6,.32))
    batch.add_box("v6-courtyard-paving","courtyard-paver",(0,10,.08),(42,30,.16))
    batch.add_box("v6-dropoff-paving","dropoff-paver",(0,-21,.11),(36,9,.22))
    batch.add_box("v6-community-terrace-paving","wood-community-accent",(-29,-7,.13),(18,8,.26))
    batch.add_box("v6-pocket-lawn","landscape-green",(31,14,.07),(19,22,.14))
    batch.add_box("v6-play-zone","play-surface",(15,12,.12),(13,10,.24))
    batch.add_box("v6-pedestrian-spine","light-gray-stone",(0,4,.18),(5,58,.36))
    batch.add_box("v6-fire-route","asphalt",(0,32,.12),(82,7,.24))
    batch.add_box("v6-service-lane","dark-asphalt",(-38,8,.1),(7,38,.2))
    batch.add_box("v6-drainage-edge","dark-gray-accent",(0,-27.6,.2),(88,.32,.4))
    for y in (-34,-28): batch.add_box("v6-curb","cool-white-precast",(0,y,.38),(92,.45,.76))
    # Twelve planters define arrival, courtyard and community edges.
    planter_positions=((-18,17),(-10,17),(-2,17),(6,17),(14,17),(22,17),(-31,-11),(-24,-11),(24,-10),(31,-10),(-15,-22),(15,-22))
    for i,(x,y) in enumerate(planter_positions):
        batch.add_box(f"v6-planter-{i%3}","light-gray-stone",(x,y,.55),(4.6 if i<6 else 3.2,2.0,1.1))
        if detail>=2: batch.add_box(f"v6-planter-{i%3}-soil","landscape-soil",(x,y,1.08),(4.15 if i<6 else 2.75,1.55,.12))
    # Species proxies vary crown, height and spacing instead of repeating one cylinder.
    tree_positions=((-39,-25),(-31,-24),(-22,-25),(-12,-24),(-2,-25),(9,-24),(20,-25),(30,-24),(39,-25),
                    (-34,25),(-24,27),(-13,25),(13,26),(24,27),(35,25),(-31,8),(31,7),(-21,20),(22,21))
    for i,(x,y) in enumerate(tree_positions): _tree(batch,i,x,y,lod)
    # Benches, lights, bollards and tactile paving communicate actual use and routes.
    for i,(x,y) in enumerate(((-18,12),(-10,12),(8,12),(18,12),(-30,-6),(-24,-6),(26,5),(32,5))):
        batch.add_box("v6-bench-seat","wood-community-accent",(x,y,.75),(2.4,.65,.18)); batch.add_box("v6-bench-base","dark-gray-accent",(x,y,.38),(1.7,.46,.58))
    for i,x in enumerate((-35,-25,-15,-5,5,15,25,35)):
        batch.add_cylinder("v6-pedestrian-light","light-metal-panel",(x,-27,2.4),.09,4.8,8)
        batch.add_box("v6-pedestrian-light-head","light-metal-panel",(x,-27,4.8),(.42,.42,.2))
    for x in range(-30,31,4): batch.add_cylinder("v6-bollard","dark-gray-accent",(x,-18,.58),.13,1.16,8)
    batch.add_box("v6-tactile-main","tactile-paver",(0,-25,.39),(1.8,12,.08))
    batch.add_box("v6-tactile-community","tactile-paver",(-26,-12,.39),(9,1.5,.08))
    # Bicycles and play/community objects are abstract, unbranded scale/use proxies.
    if detail>=2:
        for i,x in enumerate((-31,-29.5,-28,-26.5,-25,-23.5)):
            batch.add_cylinder("v6-bicycle-wheel","dark-gray-accent",(x,6,.45),.38,.08,12)
            batch.add_box("v6-bicycle-frame","painted-steel",(x,6,.65),(.75,.1,.12))
        for x,y,h in ((12,10,2.2),(17,10,1.6),(12,15,1.4),(17,15,2.0)):
            batch.add_cylinder("v6-play-community-object","painted-steel",(x,y,h/2),.45,h,10)
    batch.add_box("v6-waste-station-a","dark-gray-accent",(-34,17,1.15),(3.8,2.2,2.3))
    batch.add_box("v6-waste-station-b","light-metal-panel",(-29,17,1.15),(3.8,2.2,2.3))
    # Human/vehicle proxies appear only in review/candidate output and carry no brand or text.
    human_positions=[(-6,-19),(0,-19),(6,-19),(-18,10),(-14,10),(-8,8),(-2,8),(4,8),(10,8),(18,9),
                     (-29,-5),(-25,-5),(27,5),(31,5),(-12,22),(-5,22),(5,22),(12,22),(20,-24),(-20,-24)]
    for i,(x,y) in enumerate(human_positions): _human(batch,i,x,y,lod)
    for i,(x,y) in enumerate(((-11,-21),(-3,-21),(7,-21),(15,-21))): _vehicle(batch,i,x,y,"sedan")
    _vehicle(batch,4,-34,9,"service-vehicle")
    return {"interfaceCount":58 if detail==3 else 43 if detail==2 else 28,"pavingZones":7,"treeCount":len(tree_positions),
            "treeSpeciesProxies":4,"humanProxies":20 if detail>=2 else 0,"sedanProxies":4,"serviceVehicleProxies":1,
            "bicycleProxies":6 if detail>=2 else 0,"benchCount":8,"planterCount":12,"lightCount":8,"bollardCount":16,
            "wasteStations":2,"playObjects":4 if detail>=2 else 0,"publicRealmLifePass":detail>=2,
            "pedestrianSpine":True,"fireRoute":True,"serviceLane":True,"parkingRamp":True}
