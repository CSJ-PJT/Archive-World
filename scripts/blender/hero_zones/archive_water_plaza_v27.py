"""Archive Water Plaza V27 S-grade candidate geometry.

The concept reference is used only for abstract spatial and visual-quality
guidance.  No identifiable building, bridge, waterway, lighting arrangement,
or urban plan is reproduced.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import archive_water_plaza_v12 as v12
import archive_water_plaza_v14 as v14


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parsed = parser.parse_args(args)
    output = Path(parsed.output_root)
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)

    v14.ENVELOPE_REPORTS.clear()
    v14.FRONTAGE_ACTIVITY.clear()
    v14.FRONTAGE_VOID_DEPTH_M = 6.0
    v14.FACADE_GLASS_RECESS_M = 0.12
    v14.FACADE_GLASS_THICKNESS_M = 0.08
    v14.TOWER_FACADE_CAVITY_DEPTH_M = 0.20
    v14.ACTIVE_FRONTAGE_GRADE_M = 2.3

    original = v12.add_building
    v12.add_building = v14.add_production_building
    try:
        objects, geometry, validation, consolidation, trees, activity = v12.build_zone()
    finally:
        v12.add_building = original

    for obj in objects:
        obj["heroRevision"] = "V27_S_GRADE_CANDIDATE"
        obj["qualityTarget"] = "S_95_PLUS"

    target = output / "archive-water-plaza-hero-v27.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(target), export_format="GLB", export_yup=True,
        export_normals=True, export_texcoords=False,
        export_materials="EXPORT", export_apply=True,
    )

    envelope = v14.ENVELOPE_REPORTS
    identities = sorted({item["identity"] for item in envelope})
    assert len(envelope) == 6 and len(identities) == 6
    assert all(item["glassBackToStructuralFaceGapM"] <= 1e-6 for item in envelope)
    assert all(item["sideGlassBackToStructuralFaceGapM"] <= 1e-6 for item in envelope)
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images) == 0

    report = {
        "status": "TECHNICAL_PASS_VISUAL_GATE_PENDING",
        "zone": "Archive Water Plaza",
        "revision": 27,
        "qualityTarget": {"grade": "S", "minimumScore": 95},
        "implementationPath": "ARCHIVE_NATIVE_S_GRADE_HERO_GEOMETRY",
        "glb": str(target),
        "bytes": target.stat().st_size,
        "geometry": geometry,
        "validation": validation,
        "consolidation": consolidation,
        "buildingCount": 6,
        "activeConnectorCount": 4,
        "familyIdentityCount": len(identities),
        "familyIdentities": identities,
        "lobbyCount": 6,
        "retailPublicBayCount": 54,
        "pavilionCount": 1,
        "serviceEntranceCount": 6,
        "treeVariantCount": 12,
        "treeCount": len(trees),
        "humanCount": len(activity) + len(v14.FRONTAGE_ACTIVITY),
        "vehicleCount": 2,
        "envelopeConnection": {
            "status": "PASS",
            "frontGapM": max(item["glassBackToStructuralFaceGapM"] for item in envelope),
            "sideGapM": max(item["sideGlassBackToStructuralFaceGapM"] for item in envelope),
            "intentionalGlassRecessM": 0.12,
            "buildings": envelope,
        },
        "referencePolicy": (
            "Concept reference is used only for abstract spatial and visual-quality guidance. "
            "No direct reproduction of identifiable architecture, waterway design, bridge design, "
            "lighting arrangement, or urban plan is permitted."
        ),
        "officeV5Changed": False,
        "imageDatablocks": len(bpy.data.images),
        "directReferenceCopy": False,
        "originality": "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY",
    }
    (output / "archive-water-plaza-hero-v27-report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"], "triangles": geometry["triangles"],
        "familyIdentities": len(identities), "frontGapM": report["envelopeConnection"]["frontGapM"],
        "sideGapM": report["envelopeConnection"]["sideGapM"],
    }))


if __name__ == "__main__":
    main()
