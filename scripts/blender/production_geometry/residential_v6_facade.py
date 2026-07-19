"""Zone-aware Residential V6 facade, corner and balcony systems."""
from __future__ import annotations


DETAIL={"LOD0":3,"LOD1":2,"LOD2":1}
ZONE_NAMES=("base","lower","middle","upper","crown")
PATTERNS=("recessed-window","projected-window","paired-window","balcony-window","service-slot","deep-frame","solid-spandrel")
BALCONIES=("recessed","projected","corner","continuous","loggia")


def _zone(floor, floors):
    ratio=floor/max(1,floors)
    return "base" if floor<=3 else "lower" if ratio<.38 else "middle" if ratio<.68 else "upper" if ratio<.9 else "crown"


def _front_bay(batch,role,material,x,y,z,width,height,lod,depth,frame_material="aluminum"):
    batch.add_box(f"{role}-glass",material,(x,y,z),(width,max(.12,depth*.18),height))
    if DETAIL[lod]>=2:
        batch.add_box(f"{role}-jamb",frame_material,(x-width/2,y-depth*.12,z),(.09,max(.12,depth*.28),height+.18))
        batch.add_box(f"{role}-jamb",frame_material,(x+width/2,y-depth*.12,z),(.09,max(.12,depth*.28),height+.18))
    if DETAIL[lod]>=3:
        batch.add_box(f"{role}-head",frame_material,(x,y-depth*.12,z+height/2),(width+.16,max(.12,depth*.28),.1))
        batch.add_box(f"{role}-sill","cool-white-precast",(x,y+depth*.08,z-height/2),(width+.18,max(.12,depth*.36),.13))
        batch.add_box(f"{role}-shadow-reveal","dark-gray-accent",(x,y+depth*.2,z-height*.27),(width*.86,.08,.08))


def _side_bay(batch,role,material,x,y,z,width,height,lod,depth,direction):
    batch.add_box(f"{role}-glass",material,(x,y,z),(max(.12,depth*.18),width,height))
    if DETAIL[lod]>=2:
        batch.add_box(f"{role}-jamb","aluminum",(x+direction*depth*.1,y-width/2,z),(max(.12,depth*.28),.09,height+.16))
        batch.add_box(f"{role}-jamb","aluminum",(x+direction*depth*.1,y+width/2,z),(max(.12,depth*.28),.09,height+.16))


def _balcony(batch,kind,prefix,x,y,z,width,depth,lod,corner=False):
    material="cool-white-precast" if kind in ("recessed","loggia") else "warm-white-concrete"
    batch.add_box(f"{prefix}-{kind}-slab",material,(x,y-depth/2,z-.72),(width,depth,.18 if kind!="continuous" else .22))
    batch.add_box(f"{prefix}-{kind}-railing","balcony-glass",(x,y-depth+.05,z-.16),(width,.09,1.0))
    if DETAIL[lod]>=2:
        batch.add_box(f"{prefix}-{kind}-privacy","dark-gray-accent",(x-width/2+.08,y-depth/2,z-.16),(.16,depth,.98))
    if DETAIL[lod]>=3 and (corner or kind=="loggia"):
        batch.add_box(f"{prefix}-{kind}-return","aluminum",(x+width/2-.06,y-depth/2,z-.16),(.12,depth,.98))


def build_residential_v6_facades(batch,masses,lod):
    detail=DETAIL[lod]; floor_step=1 if lod=="LOD0" else 2
    stats={"patterns":set(),"windows":0,"balconies":0,"mullions":0,"depthRangeMeters":[.25,1.5],
           "verticalZones":set(),"balconyFamilies":set(),"cornerFamilies":set(),"sidePatterns":set(),"rearPatterns":set()}
    for mi,mass in enumerate(masses):
        x,y=mass["center"]; w=mass["width"]; d=mass["depth"]; floors=mass["floors"]; fh=mass["floorHeight"]; base=mass["base"]
        front_bays=max(6,int(w/2.05)); side_bays=max(3,int(d/2.55)); bw=(w-1.1)/front_bays; sw=(d-1.0)/side_bays
        for floor in range(1,floors,floor_step):
            zone=_zone(floor,floors); stats["verticalZones"].add(zone); z=base+floor*fh+fh*.5
            for bay in range(front_bays):
                pattern=PATTERNS[(bay+floor//3+mi*2)%len(PATTERNS)]; role=f"v6-{mass['id']}-{zone}-{pattern}"
                bx=x-w/2+.55+bw*(bay+.5); depth=.25+((bay+floor+mi)%6)*.17
                glass="muted-blue-residential-glass" if zone in ("middle","upper") else "residential-glass"
                _front_bay(batch,role,glass,bx,y-d/2-depth*.12,z,bw*.68,fh*(.48+(.05*((bay+mi)%3))),lod,depth)
                rear_pattern=("rear-loggia","rear-service","rear-window")[(bay+floor+mi)%3]
                _front_bay(batch,f"v6-{mass['id']}-{zone}-{rear_pattern}","residential-glass",bx,y+d/2+depth*.1,z,bw*.58,fh*.43,lod,depth)
                stats["patterns"].update((pattern,rear_pattern)); stats["rearPatterns"].add(rear_pattern); stats["windows"]+=2
            for bay in range(side_bays):
                by=y-d/2+.5+sw*(bay+.5); side_pattern=("side-ribbon","side-punched","side-core")[(bay+floor//4+mi)%3]
                _side_bay(batch,f"v6-{mass['id']}-{zone}-{side_pattern}","residential-glass",x-w/2-.08,by,z,sw*.62,fh*.46,lod,.4,-1)
                if bay%2==0:
                    _side_bay(batch,f"v6-{mass['id']}-{zone}-corner-return","muted-blue-residential-glass",x+w/2+.08,by,z,sw*.55,fh*.42,lod,.52,1)
                    stats["cornerFamilies"].add(("wrap","notched","framed")[(floor+mi)%3])
                stats["sidePatterns"].add(side_pattern); stats["windows"]+=1+(bay%2==0)
            stride=2 if lod=="LOD0" else 4 if lod=="LOD1" else 6
            if floor%stride==0:
                kind=BALCONIES[(floor//stride+mi)%len(BALCONIES)]; width=w*(.28 if kind=="corner" else .42 if kind!="continuous" else .68)
                depth=(.45,.72,1.05,1.28,1.5)[BALCONIES.index(kind)]; bx=x+(-w*.23 if (floor//stride+mi)%2 else w*.2)
                _balcony(batch,kind,f"v6-{mass['id']}-{zone}",bx,y-d/2-.12,z,width,depth,lod,kind=="corner")
                stats["balconyFamilies"].add(kind); stats["balconies"]+=1
        for band_floor,band_name in ((4,"transfer"),(max(7,int(floors*.48)),"middle"),(floors-2,"mechanical")):
            batch.add_box(f"v6-{mass['id']}-{band_name}-band","cool-white-precast",(x,y-d/2-.22,base+band_floor*fh),(w+.35,.42,.34 if band_name!="mechanical" else .78))
        batch.add_box(f"v6-{mass['id']}-service-blind-bay","dark-gray-accent",(x+w/2+.18,y+d*.15,base+floors*fh*.5),(.38,d*.3,floors*fh*.72))
    stats.update({"patterns":sorted(stats["patterns"]),"verticalZones":sorted(stats["verticalZones"]),
                  "balconyFamilies":sorted(stats["balconyFamilies"]),"cornerFamilies":sorted(stats["cornerFamilies"]),
                  "sidePatterns":sorted(stats["sidePatterns"]),"rearPatterns":sorted(stats["rearPatterns"]),
                  "mullions":stats["windows"]*(2 if detail>=2 else 0)})
    return stats
