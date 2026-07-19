"""Generate one deterministic Production Geometry V5 pilot LOD and optional review package."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import bpy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE)); sys.path.insert(0,str(HERE.parent))
from geometry_core import MeshBatch,validate_geometry
from facade_builder import residential_facades,office_facades
from entrance_builder import residential_entrance,office_entrance
from roof_builder import residential_roofs,office_roofs
from ground_builder import residential_ground,office_ground
from material_library import create_material_library,validate_assignment
from geometry_metrics import collect
from lod_builder import validate_single
from render_review import render_views


RESIDENTIAL_MASSES=[(-16,3,16,12,28,3.2,6),(14,6,11,11,32,3.2,6),(0,18,22,8,20,3.2,6)]
OFFICE_TOWERS=[(-11,3,16,14,40,3.7,14),(13,6,13,12,31,3.7,14)]


def arguments(default_mode=None):
    values=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p=argparse.ArgumentParser(); p.add_argument("--mode",choices=("residential","office"),default=default_mode,required=default_mode is None)
    p.add_argument("--lod",choices=("LOD0","LOD1","LOD2"),required=True); p.add_argument("--output-root",required=True)
    p.add_argument("--render",action="store_true"); p.add_argument("--render-size",type=int,default=1920); p.add_argument("--seed",type=int,default=52025)
    return p.parse_args(values)


def residential(batch,lod):
    for index,(x,y,w,d,floors,floor_h,base) in enumerate(RESIDENTIAL_MASSES):
        material="painted-concrete" if index!=1 else "precast-concrete"
        batch.add_box("res-massing",material,(x,y,base+floors*floor_h/2),(w,d,floors*floor_h))
        # Setback shoulder and stepped top are architectural silhouette geometry.
        batch.add_box("res-setback-shoulder","dark-stone",(x+(w*.32 if index%2 else -w*.32),y,base+floors*floor_h*.48),(w*.18,d*.86,floors*floor_h*.62))
    facade=residential_facades(batch,RESIDENTIAL_MASSES,lod); entrance=residential_entrance(batch,lod)
    roof=residential_roofs(batch,RESIDENTIAL_MASSES,lod); ground=residential_ground(batch,lod)
    return "residential-courtyard-piloti-pq-v5",facade,entrance,roof,ground


def office(batch,lod):
    for index,(x,y,w,d,floors,floor_h,base) in enumerate(OFFICE_TOWERS):
        batch.add_box("office-massing","curtain-wall-glass",(x,y,base+floors*floor_h/2),(w,d,floors*floor_h))
        setback=10 if index==0 else 7
        batch.add_box("office-setback-frame","limestone",(x+(w*.38 if index==0 else -w*.38),y,base+floors*floor_h*.48),(w*.14,d*.94,floors*floor_h*.48))
        batch.add_box("office-upper-setback","dark-metal-panel",(x,y,base+(floors-setback/2)*floor_h),(w*.82,d*.82,setback*floor_h))
    batch.add_box("office-sky-lobby","curtain-wall-glass",(1,4,87),(12,8,7))
    batch.add_box("office-sky-lobby-frame","light-metal-panel",(1,4,90.7),(13,9,.4))
    facade=office_facades(batch,OFFICE_TOWERS,lod); entrance=office_entrance(batch,lod)
    roof=office_roofs(batch,OFFICE_TOWERS,lod); ground=office_ground(batch,lod)
    return "archive-cbd-twin-atrium-pq-v5",facade,entrance,roof,ground


def main(default_mode=None):
    a=arguments(default_mode); started=time.monotonic(); bpy.ops.wm.read_factory_settings(use_empty=True)
    materials,material_metadata=create_material_library(); material_report=validate_assignment(a.mode,materials,material_metadata)
    assert not material_report["missing"] and material_report["imageTextureNodes"]==0
    batch=MeshBatch(materials); family,facade,entrance,roof,ground=(residential(batch,a.lod) if a.mode=="residential" else office(batch,a.lod))
    objects=batch.finalize(); validation=validate_geometry(objects)
    for obj in objects: obj["family"]=family; obj["lod"]=a.lod; obj["generationSeed"]=a.seed; obj["proceduralOnly"]=True
    batch_stats=batch.statistics(); metrics=collect(objects,batch_stats,facade,entrance,roof,ground,material_report)
    metrics["emptyMeshes"]=validation["emptyMeshes"]; metrics["looseGeometry"]=validation["looseGeometry"]
    lod_validation=validate_single(a.mode,a.lod,metrics)
    out=Path(a.output_root)/a.mode/a.lod; out.mkdir(parents=True,exist_ok=True)
    glb=out/f"{family}-{a.lod.lower()}.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_yup=True,export_normals=True,export_texcoords=False,
                              export_materials="EXPORT",export_cameras=False,export_lights=False,export_apply=True)
    renders=render_views(Path(a.output_root)/a.mode/"previews",objects,metrics["bounds"],a.render_size) if a.render else []
    report={"schemaVersion":1,"family":family,"mode":a.mode,"lod":a.lod,"seed":a.seed,"status":"TECHNICAL_GENERATED",
            "proceduralOnly":True,"textureEnabled":False,"geometry":metrics,"facade":facade,"entrance":entrance,"roof":roof,"ground":ground,
            "materials":material_report,"lodValidation":lod_validation,"glb":{"file":glb.name,"bytes":glb.stat().st_size},
            "renders":renders,"generationSeconds":round(time.monotonic()-started,3),"officialValidator":"PENDING_EXTERNAL",
            "visualApproval":"PENDING_REVIEW"}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"family":family,"lod":a.lod,"triangles":metrics["triangles"],"targetPass":lod_validation["triangleTargetPass"],
                      "objects":metrics["meshObjects"],"components":metrics["components"],"renders":len(renders),"glbBytes":glb.stat().st_size}))


if __name__=="__main__": main()
