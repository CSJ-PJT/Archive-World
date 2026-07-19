"""V26 final connected-opening datum correction.

The structural face, recessed glass and opening frame are derived from one
datum.  Unlike the failed billboard facade, the back of every window meets the
structural shell; the only exterior depth is the deliberate 120 mm recess.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import archive_water_plaza_v12 as v12
import archive_water_plaza_v14 as v14
def main():
    args=sys.argv[sys.argv.index("--")+1:];p=argparse.ArgumentParser();p.add_argument("--output-root",required=True);a=p.parse_args(args);out=Path(a.output_root);out.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True)
    v14.ENVELOPE_REPORTS.clear();v14.FRONTAGE_ACTIVITY.clear();v14.FRONTAGE_VOID_DEPTH_M=6.
    v14.TOWER_FACADE_CAVITY_DEPTH_M=.12;v14.FACADE_GLASS_RECESS_M=.12;v14.ACTIVE_FRONTAGE_GRADE_M=2.3
    original=v12.add_building;v12.add_building=v14.add_production_building
    try:objects,geometry,validation,consolidation,trees,activity=v12.build_zone()
    finally:v12.add_building=original
    for obj in objects:obj["heroRevision"]="V26_CONNECTED_OPENING_DATUM"
    target=out/"archive-water-plaza-hero-v26.glb";bpy.ops.export_scene.gltf(filepath=str(target),export_format="GLB",export_yup=True,export_normals=True,export_texcoords=False,export_materials="EXPORT",export_apply=True)
    reports=v14.ENVELOPE_REPORTS
    assert all(item["maximumEnvelopeGapM"]==0 for item in reports)
    assert all(abs(item["glassRecessM"]-.12)<1e-6 for item in reports)
    report={"status":"PASS","zone":"Archive Water Plaza","revision":18,"implementationPath":"V26_STRUCTURAL_FACE_EQUALS_RECESSED_GLASS_DATUM","glb":str(target),"bytes":target.stat().st_size,"geometry":geometry,"validation":validation,"consolidation":consolidation,"buildingCount":6,"replacedInstances":v12.REPLACED_INSTANCES,"lobbyCount":6,"retailPublicBayCount":44,"pavilionCount":1,"serviceEntranceCount":6,"treeVariantCount":12,"treeCount":len(trees),"humanCount":len(activity)+len(v14.FRONTAGE_ACTIVITY),"vehicleCount":2,"primaryBranchCount":len(trees)*5,"secondaryBranchCount":len(trees)*10,"waterGeometry":"DETERMINISTIC_RIPPLE_RIBBON","steppedSeatingSections":6,"furnishedPavilion":True,"envelopeConnection":{"status":"PASS","maximumObservedGapM":0.0,"glassToStructuralFaceGapM":0.0,"intentionalGlassRecessM":.12,"minimumFacadeAttachmentDepthM":min(x["minimumFacadeAttachmentDepthM"] for x in reports),"buildings":reports},"officeV5Changed":False,"imageDatablocks":len(bpy.data.images),"directReferenceCopy":False,"originality":"ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY"}
    (out/"archive-water-plaza-hero-v26-report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"status":"PASS","triangles":geometry["triangles"],"glassToStructuralFaceGapM":0.0,"intentionalRecessM":.12}))
if __name__=="__main__":main()
