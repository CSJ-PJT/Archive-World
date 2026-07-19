"""Residential V6 roof systems with three independent crown silhouettes."""
from __future__ import annotations


DETAIL={"LOD0":3,"LOD1":2,"LOD2":1}


def _parapet(batch,prefix,x,y,w,d,top,material,height):
    for cx,cy,dx,dy in ((x,y-d/2,w,.32),(x,y+d/2,w,.32),(x-w/2,y,.32,d),(x+w/2,y,.32,d)):
        batch.add_box(f"{prefix}-parapet",material,(cx,cy,top+height/2),(dx,dy,height))


def build_residential_v6_roofs(batch,masses,lod):
    detail=DETAIL[lod]; equipment=0; variants=[]
    for index,mass in enumerate(masses):
        x,y=mass["center"]; w=mass["width"]*mass["upperScale"][0]; d=mass["depth"]*mass["upperScale"][1]
        top=mass["base"]+mass["floors"]*mass["floorHeight"]
        prefix=f"v6-{mass['id']}-roof"; _parapet(batch,prefix,x,y,w,d,top,"cool-white-precast",1.0+index*.25)
        if mass["crown"]=="terraced":
            batch.add_box(f"{prefix}-terraced-crown","warm-white-concrete",(x-w*.12,y,top+3.0),(w*.52,d*.48,6.0)); equipment+=1
            batch.add_box(f"{prefix}-upper-terrace","light-gray-stone",(x+w*.22,y-d*.1,top+1.0),(w*.28,d*.38,2.0)); equipment+=1
            variants.append("terraced-crown")
        elif mass["crown"]=="lantern":
            batch.add_box(f"{prefix}-lantern","entrance-glazing",(x,y,top+4.2),(w*.46,d*.46,8.4)); equipment+=1
            batch.add_box(f"{prefix}-lantern-frame","aluminum",(x,y,top+8.6),(w*.56,d*.56,.45)); equipment+=1
            variants.append("glass-lantern")
        else:
            batch.add_box(f"{prefix}-screen-crown","dark-gray-accent",(x-w*.12,y,top+2.4),(w*.58,d*.52,4.8)); equipment+=1
            batch.add_box(f"{prefix}-offset-cap","light-metal-panel",(x+w*.2,y-d*.08,top+5.0),(w*.34,d*.42,.5)); equipment+=1
            variants.append("offset-screen")
        batch.add_box(f"{prefix}-machine-room","light-metal-panel",(x+w*.16,y+d*.08,top+2.2),(w*.30,d*.32,4.4)); equipment+=1
        batch.add_box(f"{prefix}-hvac-screen","dark-gray-accent",(x-w*.24,y+d*.2,top+1.45),(w*.24,d*.24,2.9)); equipment+=1
        batch.add_box(f"{prefix}-maintenance-walkway","sidewalk-concrete",(x,y-d*.30,top+.14),(w*.68,1.05,.28)); equipment+=1
        unit_count=4 if detail==3 else 2 if detail==2 else 1
        for unit in range(unit_count):
            batch.add_box(f"{prefix}-hvac-unit","painted-steel",(x-w*.28+unit*w*.18,y+d*.29,top+.72),(w*.12,d*.15,1.44)); equipment+=1
        solar_count=6 if detail==3 else 3 if detail==2 else 1
        for panel in range(solar_count):
            batch.add_box(f"{prefix}-solar-panel","dark-metal-panel",(x-w*.3+panel*w*.12,y-d*.18,top+.75),(w*.095,d*.22,.14),-.16); equipment+=1
        if detail>=2:
            batch.add_cylinder(f"{prefix}-communications","aluminum",(x+w*.28,y+d*.24,top+4.8),.15,6.5,10 if detail==3 else 8); equipment+=1
        if detail==3:
            batch.add_box(f"{prefix}-service-enclosure","painted-steel",(x+w*.3,y-d*.24,top+1.15),(w*.16,d*.18,2.3)); equipment+=1
    return {"equipmentCount":equipment,"parapetEdges":len(masses)*4,"crownVariants":variants,
            "crownVariantCount":len(set(variants)),"maintenanceWalkways":len(masses),"solarZones":len(masses),
            "roofSkylineDistinct":len(set(variants))==len(masses)}
