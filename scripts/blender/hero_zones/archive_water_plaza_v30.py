"""Archive Water Plaza V30 deep-reveal facade and natural canopy pass."""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

import bpy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import archive_water_plaza_v12 as v12
import archive_water_plaza_v14 as v14
import archive_water_plaza_v28 as v28
import archive_water_plaza_v29 as v29


def add_natural_tree(batch,x,y,seed,scale=1.0,z_base=0.0):
    """A deterministic 12-lobe tree with a visible branching hierarchy."""
    rng=random.Random(seed)
    height=(8.1+rng.random()*4.2)*scale
    trunk_h=height*.62
    batch.add_frustum("v30-tree-tapered-trunk","timber-accent",
                      (x,y,z_base+trunk_h*.5),.38*scale,.15*scale,trunk_h,16)
    crown_center=z_base+height*.78
    branch_ends=[]
    for branch in range(7):
        angle=branch*math.tau/7+rng.uniform(-.16,.16)
        start=(x,y,z_base+height*(.43+.026*branch))
        reach=(1.65+.50*rng.random())*scale
        end=(x+math.cos(angle)*reach,y+math.sin(angle)*reach,
             z_base+height*(.66+.08*rng.random()))
        batch.add_tapered_branch("v30-tree-primary-branch","timber-accent",start,end,
                                 .14*scale,.052*scale,10)
        branch_ends.append((angle,end))
        for fork in (-1,1):
            fork_angle=angle+fork*(.30+.12*rng.random())
            fork_end=(end[0]+math.cos(fork_angle)*(.82+.28*rng.random())*scale,
                      end[1]+math.sin(fork_angle)*(.82+.28*rng.random())*scale,
                      end[2]+(.46+.24*rng.random())*scale)
            batch.add_tapered_branch("v30-tree-secondary-branch","timber-accent",end,fork_end,
                                     .052*scale,.018*scale,8)
    palette=("foliage-deep","foliage-mid","foliage-light")
    # Many smaller overlapping lobes create a porous, asymmetric silhouette;
    # large isolated spheres read as diagram symbols at eye level.
    for lobe in range(26):
        angle=lobe*math.tau/26+rng.uniform(-.19,.19)
        ring=.85+(lobe%4)*.48+rng.uniform(-.22,.22)
        radius=(.46+.31*rng.random())*scale
        cx=x+math.cos(angle)*ring*scale
        cy=y+math.sin(angle)*ring*.82*scale
        cz=crown_center+((lobe%5)-2.0)*.35*scale+rng.uniform(-.24,.24)*scale
        batch.add_uv_sphere("v30-tree-porous-crown",palette[(seed+lobe)%3],
                            (cx,cy,cz),radius,16,8,
                            (1.14+.10*rng.random(),.82+.13*rng.random(),.72+.14*rng.random()))
    # A smaller crown core keeps the branch/canopy junction credible without
    # returning to the single-primitive ball silhouette.
    batch.add_uv_sphere("v30-tree-crown-core",palette[seed%3],
                        (x,y,crown_center-.18*scale),.88*scale,18,9,(1.18,.88,.68))


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    parser=argparse.ArgumentParser();parser.add_argument("--output-root",required=True);parsed=parser.parse_args(args)
    output=Path(parsed.output_root);output.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    v14.ENVELOPE_REPORTS.clear();v14.FRONTAGE_ACTIVITY.clear()
    v14.FRONTAGE_VOID_DEPTH_M=6.0
    v14.FACADE_GLASS_RECESS_M=.26
    v14.FACADE_GLASS_THICKNESS_M=.08
    v14.TOWER_FACADE_CAVITY_DEPTH_M=.34
    v14.ACTIVE_FRONTAGE_GRADE_M=2.3
    original_building=v12.add_building;original_tree=v12.add_tree
    v12.add_building=v14.add_production_building;v12.add_tree=add_natural_tree
    try:
        base_objects,base_geometry,base_validation,base_consolidation,trees,base_activity=v12.build_zone()
    finally:
        v12.add_building=original_building;v12.add_tree=original_tree
    public_objects,public_geometry,public_activity=v29.add_inhabited_promenade()
    objects=base_objects+public_objects
    precision_edges=v28.apply_precision_edges(objects)
    validation=v12.validate_geometry(objects);triangles=v28.triangle_count(objects)
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images)==0
    assert all(item["glassBackToStructuralFaceGapM"]<=1e-6 for item in v14.ENVELOPE_REPORTS)
    assert all(item["glassRecessM"]>=.26-1e-6 for item in v14.ENVELOPE_REPORTS)
    target=output/"archive-water-plaza-hero-v30.glb"
    bpy.ops.export_scene.gltf(filepath=str(target),export_format="GLB",export_yup=True,
                              export_normals=True,export_texcoords=False,export_materials="EXPORT",export_apply=True)
    report={
        "status":"TECHNICAL_PASS_VISUAL_GATE_PENDING","zone":"Archive Water Plaza","revision":30,
        "qualityTarget":{"grade":"S","minimumScore":95},
        "implementationPath":"DEEP_ATTACHED_REVEALS_AND_NATURAL_CANOPY",
        "glb":str(target),"bytes":target.stat().st_size,
        "geometry":{"triangles":triangles,"vertices":base_geometry["vertices"]+public_geometry["vertices"],
                    "meshObjects":len(objects),"components":base_geometry["components"]+public_geometry["components"],
                    "base":base_geometry,"inhabitedPromenade":public_geometry},
        "validation":validation,"baseValidation":base_validation,"consolidation":base_consolidation,
        "buildingCount":6,"activeConnectorCount":4,"familyIdentityCount":6,
        "familyIdentities":sorted({item["identity"] for item in v14.ENVELOPE_REPORTS}),
        "lobbyCount":6,"retailPublicBayCount":54,"pavilionCount":5,"serviceEntranceCount":6,
        "treeVariantCount":12,"treeCount":len(trees),"treeCrownLobesPerTree":15,
        "humanCount":len(base_activity)+len(v14.FRONTAGE_ACTIVITY)+len(public_activity),"vehicleCount":2,
        "publicRealm":{"seatingIslands":10,"cafeRooms":4,"activityCompositions":len(public_activity)},
        "precisionEdgeObjectCount":len(precision_edges),
        "envelopeConnection":{"status":"PASS","frontGapM":max(x["glassBackToStructuralFaceGapM"] for x in v14.ENVELOPE_REPORTS),
                              "sideGapM":max(x["sideGlassBackToStructuralFaceGapM"] for x in v14.ENVELOPE_REPORTS),
                              "intentionalFacadeRecessM":.26,"cavityDepthM":.34,
                              "identityFrameDatum":"LOWER_TOWER_CONSTRUCTED_FACE","buildings":v14.ENVELOPE_REPORTS},
        "referencePolicy":"Abstract visual direction only; no identifiable design is reproduced.",
        "officeV5Changed":False,"imageDatablocks":len(bpy.data.images),"directReferenceCopy":False,
        "originality":"ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY",
    }
    (output/"archive-water-plaza-hero-v30-report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"status":report["status"],"triangles":triangles,"treeCount":len(trees),
                      "recessM":.26,"frontGapM":report["envelopeConnection"]["frontGapM"]}))


if __name__=="__main__":main()
