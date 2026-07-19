"""Generate Residential V6 only; Office V5 is intentionally outside this entry point."""
from __future__ import annotations

import argparse,json,sys,time
from pathlib import Path

import bpy

HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE)); sys.path.insert(0,str(HERE.parent))
from geometry_core import MeshBatch,validate_geometry
from geometry_metrics import collect
from material_library import create_material_library,validate_assignment
from residential_v6_materials import extend_residential_v6_palette
from residential_v6_massing import MASSES,build_residential_v6_massing
from residential_v6_facade import build_residential_v6_facades
from residential_v6_lowrise import build_residential_v6_lowrise
from residential_v6_ground import build_residential_v6_ground
from residential_v6_roof import build_residential_v6_roofs
from residential_v6_render import render_residential_v6

FAMILY="residential-courtyard-piloti-pq-v6"
TARGETS={"LOD0":(120000,180000),"LOD1":(40000,85000),"LOD2":(15000,35000)}


def arguments():
    values=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p=argparse.ArgumentParser(); p.add_argument("--lod",choices=tuple(TARGETS),required=True); p.add_argument("--output-root",required=True)
    p.add_argument("--render",action="store_true"); p.add_argument("--render-size",type=int,default=1920); p.add_argument("--seed",type=int,default=62026)
    return p.parse_args(values)


def main():
    a=arguments(); started=time.monotonic(); bpy.ops.wm.read_factory_settings(use_empty=True)
    materials,metadata=create_material_library(); palette=extend_residential_v6_palette(materials,metadata); base_materials=validate_assignment("residential",materials,metadata)
    assert palette["imageTextureNodes"]==0 and base_materials["imageTextureNodes"]==0
    batch=MeshBatch(materials); massing=build_residential_v6_massing(batch,a.lod); facade=build_residential_v6_facades(batch,MASSES,a.lod)
    entrance=build_residential_v6_lowrise(batch,a.lod); ground=build_residential_v6_ground(batch,a.lod); roof=build_residential_v6_roofs(batch,MASSES,a.lod)
    objects=batch.finalize(); validation=validate_geometry(objects)
    for obj in objects: obj["family"]=FAMILY; obj["lod"]=a.lod; obj["generationSeed"]=a.seed; obj["proceduralOnly"]=True; obj["canonical"]=False
    material_report={**base_materials,"v6Palette":palette,"materialCount":len({s.material.name for o in objects for s in o.material_slots if s.material})}
    metrics=collect(objects,batch.statistics(),facade,entrance,roof,ground,material_report); metrics["emptyMeshes"]=validation["emptyMeshes"]; metrics["looseGeometry"]=validation["looseGeometry"]
    metrics.update({"massing":massing,"facadeBayFamilies":len(facade["patterns"]),"balconyFamilies":len(facade["balconyFamilies"]),
                    "cornerFamilies":len(facade["cornerFamilies"]),"verticalZones":len(facade["verticalZones"]),
                    "sidePatterns":len(facade["sidePatterns"]),"rearPatterns":len(facade["rearPatterns"]),
                    "entranceHierarchyPass":len(entrance["hierarchy"])>=5,"lowRiseLifePass":entrance["lowRiseFunctions"]>=12,
                    "publicRealmLifePass":ground["publicRealmLifePass"],"roofSkylineDistinct":roof["roofSkylineDistinct"]})
    low,high=TARGETS[a.lod]; lod_validation={"lod":a.lod,"triangles":metrics["triangles"],"target":[low,high],
        "triangleTargetPass":low<=metrics["triangles"]<=high,"groundZPass":abs(metrics["bounds"]["min"][2])<=.8,
        "originPass":metrics["origin"]==[0,0,0],"emptyMeshes":validation["emptyMeshes"],"looseGeometry":validation["looseGeometry"]}
    out=Path(a.output_root)/"residential"/a.lod; out.mkdir(parents=True,exist_ok=True); glb=out/f"{FAMILY}-{a.lod.lower()}.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_yup=True,export_normals=True,export_texcoords=False,
        export_materials="EXPORT",export_cameras=False,export_lights=False,export_apply=True)
    renders=render_residential_v6(Path(a.output_root)/"residential/previews",objects,metrics["bounds"],a.render_size) if a.render else []
    report={"schemaVersion":1,"family":FAMILY,"mode":"residential","lod":a.lod,"seed":a.seed,"status":"TECHNICAL_GENERATED",
        "officeBaselineFrozen":True,"proceduralOnly":True,"textureEnabled":False,"geometry":metrics,"facade":facade,"entrance":entrance,
        "roof":roof,"ground":ground,"materials":material_report,"lodValidation":lod_validation,"glb":{"file":glb.name,"bytes":glb.stat().st_size},
        "renders":renders,"generationSeconds":round(time.monotonic()-started,3),"officialValidator":"PENDING_EXTERNAL","visualApproval":"PENDING_REVIEW"}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"family":FAMILY,"lod":a.lod,"triangles":metrics["triangles"],"targetPass":lod_validation["triangleTargetPass"],
        "repetition":metrics["facadeRepetitionRatio"],"patterns":metrics["facadePatternCount"],"renders":len(renders),"glbBytes":glb.stat().st_size}))


if __name__=="__main__": main()
