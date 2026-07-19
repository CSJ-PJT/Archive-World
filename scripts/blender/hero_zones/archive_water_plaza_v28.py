"""Archive Water Plaza V28 precision envelope and architectural edge pass.

The concept target supplies only abstract quality direction.  All geometry is
Archive-native, deterministic, procedural, texture-free and non-canonical.
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


BEVEL_WIDTHS = {
    "canopy": .08,
    "bench": .045,
    "seat": .04,
    "planter": .055,
    "portal": .045,
    "pavilion": .055,
    "crown": .055,
    "transfer": .04,
    "bridge": .045,
    "counter": .035,
    "signage": .025,
}


def apply_precision_edges(objects):
    applied = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        lowered = obj.name.lower()
        width = next((value for token, value in BEVEL_WIDTHS.items() if token in lowered), None)
        if width is None:
            continue
        modifier = obj.modifiers.new(name="V28 precision edge", type="BEVEL")
        modifier.width = width
        modifier.segments = 2
        modifier.limit_method = "ANGLE"
        modifier.angle_limit = .52
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        obj.select_set(False)
        applied.append({"object": obj.name, "widthM": width, "segments": 2})
    return applied


def triangle_count(objects):
    return sum(
        max(0, len(polygon.vertices) - 2)
        for obj in objects if obj.type == "MESH"
        for polygon in obj.data.polygons
    )


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
    v14.FACADE_GLASS_RECESS_M = .12
    v14.FACADE_GLASS_THICKNESS_M = .08
    v14.TOWER_FACADE_CAVITY_DEPTH_M = .20
    v14.ACTIVE_FRONTAGE_GRADE_M = 2.3

    original = v12.add_building
    v12.add_building = v14.add_production_building
    try:
        objects, source_geometry, validation, consolidation, trees, activity = v12.build_zone()
    finally:
        v12.add_building = original

    precision_edges = apply_precision_edges(objects)
    exported_triangles = triangle_count(objects)
    identities = sorted({item["identity"] for item in v14.ENVELOPE_REPORTS})
    for obj in objects:
        obj["heroRevision"] = "V28_ATTACHED_ARCHITECTURAL_BODY"
        obj["qualityTarget"] = "S_95_PLUS"

    assert len(v14.ENVELOPE_REPORTS) == 6 and len(identities) == 6
    assert all(item["glassBackToStructuralFaceGapM"] <= 1e-6 for item in v14.ENVELOPE_REPORTS)
    assert all(item["sideGlassBackToStructuralFaceGapM"] <= 1e-6 for item in v14.ENVELOPE_REPORTS)
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images) == 0
    assert precision_edges

    target = output / "archive-water-plaza-hero-v28.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(target), export_format="GLB", export_yup=True,
        export_normals=True, export_texcoords=False,
        export_materials="EXPORT", export_apply=True,
    )
    report = {
        "status": "TECHNICAL_PASS_VISUAL_GATE_PENDING",
        "zone": "Archive Water Plaza",
        "revision": 28,
        "qualityTarget": {"grade": "S", "minimumScore": 95},
        "implementationPath": "ATTACHED_BUILDING_BODY_AND_PRECISION_EDGE_PASS",
        "glb": str(target),
        "bytes": target.stat().st_size,
        "sourceGeometry": source_geometry,
        "geometry": {
            **source_geometry,
            "triangles": exported_triangles,
            "preBevelTriangles": source_geometry["triangles"],
        },
        "validation": validation,
        "consolidation": consolidation,
        "buildingCount": 6,
        "activeConnectorCount": 4,
        "familyIdentityCount": len(identities),
        "familyIdentities": identities,
        "attachedBodySystems": [
            "three-storey structural base",
            "bounded occupied corner rooms",
            "attached transfer terraces",
            "family-specific roof silhouettes",
            "rear service cores and louvers",
        ],
        "precisionEdgeObjectCount": len(precision_edges),
        "precisionEdges": precision_edges,
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
            "frontGapM": max(item["glassBackToStructuralFaceGapM"] for item in v14.ENVELOPE_REPORTS),
            "sideGapM": max(item["sideGlassBackToStructuralFaceGapM"] for item in v14.ENVELOPE_REPORTS),
            "identityFrameDatum": "LOWER_TOWER_CONSTRUCTED_FACE",
            "intentionalGlassRecessM": .12,
            "buildings": v14.ENVELOPE_REPORTS,
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
    (output / "archive-water-plaza-hero-v28-report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "triangles": exported_triangles,
        "preBevelTriangles": source_geometry["triangles"],
        "familyIdentities": len(identities),
        "precisionEdges": len(precision_edges),
        "frontGapM": report["envelopeConnection"]["frontGapM"],
        "sideGapM": report["envelopeConnection"]["sideGapM"],
    }))


if __name__ == "__main__":
    main()
