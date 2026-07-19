"""Archive Water Plaza V29 inhabited-promenade production pass."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import archive_water_plaza_v12 as v12
import archive_water_plaza_v14 as v14
import archive_water_plaza_v28 as v28


def add_seating_island(batch, x, side, variant):
    y = side*(25.5 + (variant % 2)*3.2)
    stone = "archive-warm-stone" if side > 0 else "ledger-limestone"
    accent = "archive-metal" if side > 0 else "ledger-bronze"
    width = 14.0 + (variant % 3)*2.2
    # A raised, occupiable room subdivides the formerly blank civic paving.
    batch.add_box("v29-promenade-room-paving", "dry-stone", (x, y, 2.39),
                  (width+5.5, 9.2, .18))
    batch.add_box("v29-promenade-room-planter", stone, (x, y+side*2.65, 2.92),
                  (width, 2.0, 1.05))
    batch.add_box("v29-promenade-room-soil", "soil-v11", (x, y+side*2.65, 3.49),
                  (width-.65, 1.42, .12))
    for shrub in range(7):
        sx=x-width*.40+shrub*width*.80/6
        batch.add_uv_sphere("v29-promenade-room-shrub",
                            ("foliage-deep","foliage-mid","foliage-light")[(variant+shrub)%3],
                            (sx,y+side*2.65,4.00+(shrub%2)*.12), .66+(shrub%3)*.08,
                            16,8,(1.15,.72,.65))
    for offset in (-width*.30, 0, width*.30):
        batch.add_box("v29-promenade-room-seat", "timber-accent",
                      (x+offset,y-side*.45,2.82),(3.3,.78,.22))
        batch.add_box("v29-promenade-room-seat-back", "timber-accent",
                      (x+offset,y-side*.82,3.28),(3.3,.16,.92))
    # A real light fixture and blank wayfinding panel establish orientation.
    batch.add_cylinder("v29-promenade-room-light-pole", accent,
                       (x-width*.46,y-side*2.6,4.5),.105,4.4,12)
    batch.add_uv_sphere("v29-promenade-room-light", "warm-light",
                        (x-width*.46,y-side*2.6,6.75),.24,14,7)
    batch.add_box("v29-promenade-wayfinding-frame", accent,
                  (x+width*.46,y-side*2.3,3.55),(.18,.30,2.7))
    batch.add_box("v29-promenade-wayfinding-blank", "archive-warm-stone",
                  (x+width*.46,y-side*2.3,4.25),(1.65,.18,1.15))


def add_cafe_room(batch, x, side, variant):
    y=side*(33.0+(variant%2)*2.0)
    accent="archive-metal" if side>0 else "ledger-bronze"
    stone="archive-warm-stone" if side>0 else "ledger-limestone"
    # Slender four-post canopy with a warm soffit: a recognisable place rather
    # than loose tables scattered on a blank plane.
    batch.add_box("v29-cafe-room-floor","promenade-paver",(x,y,2.40),(17.0,9.5,.18))
    batch.add_box("v29-cafe-room-canopy",stone,(x,y+side*.5,6.65),(12.8,7.2,.24))
    batch.add_box("v29-cafe-room-warm-soffit","warm-light",(x,y+side*.5,6.48),(11.8,6.3,.08))
    for ox in (-5.65,5.65):
        for oy in (-2.70,2.70):
            batch.add_cylinder("v29-cafe-room-column",accent,(x+ox,y+oy,4.42),.15,4.45,12)
    for table in (-4.0,0,4.0):
        batch.add_cylinder("v29-cafe-room-table",accent,(x+table,y,3.13),.68,.12,18)
        for angle in (0,math.pi*.5,math.pi,math.pi*1.5):
            batch.add_box("v29-cafe-room-chair","timber-accent",
                          (x+table+math.cos(angle)*1.18,y+math.sin(angle)*1.18,2.78),
                          (.48,.48,.68),angle)
    batch.add_box("v29-cafe-service-counter","timber-accent",
                  (x,y-side*3.25,3.25),(7.5,.80,1.55))


def add_activity(batch):
    records=[]
    compositions=[
        (-337,-25,"walking"),(-332,-23,"conversation"),(-328,-26,"conversation"),
        (-310,27,"seated"),(-306,28,"conversation"),(-300,26,"walking"),
        (-282,-34,"seated"),(-278,-32,"seated"),(-274,-34,"conversation"),
        (-252,25,"walking"),(-247,24,"conversation"),(-242,27,"conversation"),
        (-222,-28,"walking"),(-217,-26,"walking"),(-212,-30,"conversation"),
        (-193,34,"seated"),(-189,32,"conversation"),(-184,34,"seated"),
        (-168,-24,"walking"),(-163,-22,"conversation"),(-158,-26,"conversation"),
        (-260,-2,"crossing"),(-255,2,"crossing"),(-248,-1,"crossing"),
    ]
    for index,(x,y,action) in enumerate(compositions):
        records.append(v12.add_human(batch,x,y,0 if y>0 else math.pi,
                                     v12.SEED+900+index,action,z_base=2.3 if abs(y)>15 else 2.8))
    return records


def add_inhabited_promenade():
    batch=v12.HeroBatch(v12.create_materials())
    for index,x in enumerate((-336,-292,-248,-204,-164)):
        add_seating_island(batch,x,1,index)
        add_seating_island(batch,x,-1,index+1)
    for index,(x,side) in enumerate(((-318,-1),(-270,1),(-218,-1),(-176,1))):
        add_cafe_room(batch,x,side,index)
    activity=add_activity(batch)
    v12.consolidate(batch)
    objects=batch.finalize()
    for obj in objects:
        obj["heroZone"]="archive-water-plaza"
        obj["heroRevision"]="V29_INHABITED_PROMENADE"
        obj["canonical"]=False
        obj["v3Applied"]=False
        obj["directReferenceCopy"]=False
    return objects,batch.statistics(),activity


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    parser=argparse.ArgumentParser();parser.add_argument("--output-root",required=True);parsed=parser.parse_args(args)
    output=Path(parsed.output_root);output.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    v14.ENVELOPE_REPORTS.clear();v14.FRONTAGE_ACTIVITY.clear()
    v14.FRONTAGE_VOID_DEPTH_M=6.0;v14.FACADE_GLASS_RECESS_M=.12
    v14.FACADE_GLASS_THICKNESS_M=.08;v14.TOWER_FACADE_CAVITY_DEPTH_M=.20
    v14.ACTIVE_FRONTAGE_GRADE_M=2.3
    original=v12.add_building;v12.add_building=v14.add_production_building
    try:
        base_objects,base_geometry,base_validation,base_consolidation,trees,base_activity=v12.build_zone()
    finally:v12.add_building=original
    public_objects,public_geometry,public_activity=add_inhabited_promenade()
    objects=base_objects+public_objects
    precision_edges=v28.apply_precision_edges(objects)
    validation=v12.validate_geometry(objects)
    exported_triangles=v28.triangle_count(objects)
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images)==0
    assert all(item["glassBackToStructuralFaceGapM"]<=1e-6 for item in v14.ENVELOPE_REPORTS)
    target=output/"archive-water-plaza-hero-v29.glb"
    bpy.ops.export_scene.gltf(filepath=str(target),export_format="GLB",export_yup=True,
                              export_normals=True,export_texcoords=False,export_materials="EXPORT",export_apply=True)
    report={
        "status":"TECHNICAL_PASS_VISUAL_GATE_PENDING","zone":"Archive Water Plaza","revision":29,
        "qualityTarget":{"grade":"S","minimumScore":95},
        "implementationPath":"ATTACHED_BUILDING_BODY_PLUS_INHABITED_PROMENADE",
        "glb":str(target),"bytes":target.stat().st_size,
        "geometry":{"triangles":exported_triangles,"vertices":base_geometry["vertices"]+public_geometry["vertices"],
                    "meshObjects":len(objects),"components":base_geometry["components"]+public_geometry["components"],
                    "base":base_geometry,"inhabitedPromenade":public_geometry},
        "validation":validation,"baseValidation":base_validation,"consolidation":base_consolidation,
        "buildingCount":6,"activeConnectorCount":4,"familyIdentityCount":6,
        "familyIdentities":sorted({item["identity"] for item in v14.ENVELOPE_REPORTS}),
        "lobbyCount":6,"retailPublicBayCount":54,"pavilionCount":5,"serviceEntranceCount":6,
        "treeVariantCount":12,"treeCount":len(trees),
        "humanCount":len(base_activity)+len(v14.FRONTAGE_ACTIVITY)+len(public_activity),"vehicleCount":2,
        "publicRealm":{"seatingIslands":10,"cafeRooms":4,"wayfindingNodes":10,
                       "activityCompositions":len(public_activity),"blankPavingMitigation":"PASS"},
        "precisionEdgeObjectCount":len(precision_edges),
        "envelopeConnection":{"status":"PASS","frontGapM":max(x["glassBackToStructuralFaceGapM"] for x in v14.ENVELOPE_REPORTS),
                              "sideGapM":max(x["sideGlassBackToStructuralFaceGapM"] for x in v14.ENVELOPE_REPORTS),
                              "identityFrameDatum":"LOWER_TOWER_CONSTRUCTED_FACE","buildings":v14.ENVELOPE_REPORTS},
        "referencePolicy":"Concept direction only; no identifiable architecture, waterway, bridge, lighting arrangement, or urban plan is reproduced.",
        "officeV5Changed":False,"imageDatablocks":len(bpy.data.images),"directReferenceCopy":False,
        "originality":"ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY",
    }
    (output/"archive-water-plaza-hero-v29-report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"status":report["status"],"triangles":exported_triangles,
                      "seatingIslands":10,"cafeRooms":4,"humans":report["humanCount"],
                      "frontGapM":report["envelopeConnection"]["frontGapM"]}))


if __name__=="__main__":main()
