"""Ground interface, public realm, access and landscape geometry."""


def _tree(batch,x,y,lod,prefix):
    segments=12 if lod=="LOD0" else 8
    batch.add_cylinder(f"{prefix}-tree-trunk","wood-accent",(x,y,2.0),.24,4.0,segments)
    batch.add_cylinder(f"{prefix}-tree-canopy","soil",(x,y,5.0),1.5,3.2,segments)


def residential_ground(batch,lod):
    detail={"LOD0":3,"LOD1":2,"LOD2":1}[lod]
    batch.add_box("res-site","soil",(0,0,-.3),(88,72,.6))
    batch.add_box("res-courtyard-paving","plaza-paver",(0,7,.05),(34,25,.1))
    batch.add_box("res-sidewalk","sidewalk-concrete",(0,-29,.18),(78,6,.36))
    batch.add_box("res-fire-access","asphalt",(0,28,.12),(72,7,.24))
    batch.add_box("res-dropoff","asphalt",(0,-21,.12),(32,8,.24))
    for y in (-32,-26): batch.add_box("res-curb","precast-concrete",(0,y,.38),(82,.42,.76))
    for x in range(-34,35,8): _tree(batch,x,-25,lod,"res-street")
    for x,y in ((-30,18),(-22,20),(22,20),(30,18),(-29,-10),(29,-10)): _tree(batch,x,y,lod,"res-courtyard")
    for x in (-18,-10,-2,6,14):
        batch.add_box("res-planter","dark-stone",(x,16,.55),(5.0,2.2,1.1))
        if detail>=2: batch.add_box("res-landscape-buffer","soil",(x,16,1.08),(4.5,1.7,.12))
    batch.add_box("res-tactile-paving","plaza-paver",(0,-26,.42),(2.0,8,.08))
    if detail==3:
        for y in range(-28,-20): batch.add_box("res-tactile-stud","dark-stone",(0,y+.2,.48),(1.6,.18,.08))
        for x in (-25,-15,15,25):
            batch.add_box("res-bench","wood-accent",(x,10,1.0),(2.4,.7,.18))
            batch.add_box("res-bench-support","dark-metal-panel",(x,10,.55),(1.8,.5,.7))
    return {"interfaceCount":25 if detail==3 else 20 if detail==2 else 15,"treeCount":15,
            "sidewalkWidth":6.0,"fireAccessWidth":7.0,"dropoffWidth":8.0,"courtyardArea":850}


def office_ground(batch,lod):
    detail={"LOD0":3,"LOD1":2,"LOD2":1}[lod]
    batch.add_box("office-site","granite",(0,0,-.3),(104,82,.6))
    batch.add_box("office-plaza","plaza-paver",(0,-24,.08),(62,25,.16))
    batch.add_box("office-service-lane","asphalt",(0,31,.12),(88,9,.24))
    batch.add_box("office-dropoff","asphalt",(0,-34,.12),(55,8,.24))
    batch.add_box("office-paving-transition","sidewalk-concrete",(0,-18,.16),(72,6,.32))
    batch.add_box("office-water-basin","dark-stone",(28,-22,.35),(16,8,.7))
    batch.add_box("office-water","water",(28,-22,.72),(15,7,.12))
    for x in range(-42,43,8): _tree(batch,x,-17,lod,"office-plaza")
    for x in range(-36,37,4): batch.add_cylinder("office-security-bollard","dark-metal-panel",(x,-30,.65),.15,1.3,8)
    for x in (-24,-16,-8,8,16,24):
        batch.add_box("office-plaza-seat","wood-accent",(x,-22,.65),(2.8,.8,.22))
        batch.add_box("office-seat-support","dark-metal-panel",(x,-22,.3),(2.2,.55,.6))
    for x in (-34,-24,24,34): batch.add_box("office-planter","limestone",(x,-10,.65),(6,2.4,1.3))
    batch.add_box("office-tactile-paving","plaza-paver",(0,-31,.38),(2.2,13,.08))
    if detail==3:
        for y in range(-37,-24): batch.add_box("office-tactile-stud","dark-stone",(0,y+.3,.45),(1.8,.16,.08))
        for x in (-20,-10,10,20):
            batch.add_cylinder("office-pedestrian-light","light-metal-panel",(x,-14,2.5),.1,5,8)
            batch.add_box("office-light-head","light-metal-panel",(x,-14,5.0),(.45,.45,.22))
    return {"interfaceCount":31 if detail==3 else 25 if detail==2 else 18,"treeCount":11,
            "plazaArea":1550,"serviceLaneWidth":9.0,"dropoffWidth":8.0,"waterFeature":True}
