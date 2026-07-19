"""Residential V6 massing: distinct slab, point and courtyard-edge silhouettes."""
from __future__ import annotations


MASSES = (
    {"id":"west-slab","form":"slab","center":(-18.0,1.0),"width":24.0,"depth":13.0,"floors":31,"floorHeight":3.18,"base":7.0,"setbackFloor":23,"upperScale":(0.78,0.88),"crown":"terraced"},
    {"id":"east-point","form":"point","center":(17.0,5.0),"width":15.0,"depth":15.5,"floors":26,"floorHeight":3.22,"base":7.0,"setbackFloor":19,"upperScale":(0.84,0.78),"crown":"lantern"},
    {"id":"north-edge","form":"courtyard-edge","center":(0.0,22.0),"width":32.0,"depth":9.5,"floors":19,"floorHeight":3.15,"base":6.0,"setbackFloor":14,"upperScale":(0.72,0.90),"crown":"screen"},
)


def build_residential_v6_massing(batch, lod):
    """Build non-cloned lower/upper masses and silhouette-specific shoulders."""
    for index,mass in enumerate(MASSES):
        x,y=mass["center"]; w=mass["width"]; d=mass["depth"]; fh=mass["floorHeight"]
        lower=mass["setbackFloor"]; upper=mass["floors"]-lower; base=mass["base"]
        material=("painted-concrete","precast-concrete","light-stone")[index]
        batch.add_box(f"v6-{mass['id']}-lower-mass",material,(x,y,base+lower*fh/2),(w,d,lower*fh))
        uw=w*mass["upperScale"][0]; ud=d*mass["upperScale"][1]
        shift=(-w*.08 if index==0 else w*.1 if index==1 else w*.12)
        batch.add_box(f"v6-{mass['id']}-upper-step",material,(x+shift,y+d*.05,base+(lower+upper/2)*fh),(uw,ud,upper*fh))
        # A distinct full-height service/core spine avoids mirrored tower readings.
        if mass["form"]=="slab":
            batch.add_box("v6-west-slab-core","dark-stone",(x+w*.43,y+d*.12,base+lower*fh*.49),(1.35,d*.44,lower*fh*.92))
            batch.add_box("v6-west-terrace-step","precast-concrete",(x-w*.25,y-d*.18,base+(lower-2)*fh),(w*.34,d*.52,2*fh))
        elif mass["form"]=="point":
            batch.add_box("v6-east-point-core","cool-white-precast",(x-w*.34,y+d*.36,base+lower*fh*.5),(w*.24,1.25,lower*fh))
            batch.add_box("v6-east-corner-notch","dark-gray-accent",(x+w*.37,y-d*.36,base+lower*fh*.62),(w*.18,d*.2,lower*fh*.42))
        else:
            batch.add_box("v6-north-edge-core","dark-gray-accent",(x-w*.34,y+d*.34,base+lower*fh*.48),(w*.22,1.1,lower*fh*.88))
            batch.add_box("v6-courtyard-opening-frame","wood-community-accent",(x+w*.28,y-d*.53,base+4.2),(w*.22,.55,8.4))
    return {"massCount":3,"heightTiers":3,"forms":[m["form"] for m in MASSES],"asymmetric":True,
            "courtyardOpening":"south","towerMeshCloneCount":0}
