"""Generate the complete V11 Archive-native Urban Stream actual GLB."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
PROD = HERE.parent / "production_geometry"
CORE = HERE.parent / "core_district_precision"
sys.path[:0] = [str(HERE), str(PROD), str(CORE)]
from geometry_core import MeshBatch, validate_geometry
from batch_consolidation import consolidate
from materials_v11 import create_materials
from section_builder import build_sections
from frontage_builder import build_frontages
from node_builder_v11 import build_nodes
from bridge_builder_v11 import build_bridges
from vegetation_v11 import build_vegetation
from activity_v11 import build_activity
from lighting_v11 import build_lighting


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--alignment", required=True)
    parser.add_argument("--output-root", required=True)
    parsed = parser.parse_args(args)
    output = Path(parsed.output_root)
    output.mkdir(parents=True, exist_ok=True)
    alignment = json.loads(Path(parsed.alignment).read_text(encoding="utf-8"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    materials = create_materials()
    batch = MeshBatch(materials)
    sections = build_sections(batch, alignment["segments"])
    bridges = build_bridges(batch, alignment["bridges"])
    nodes = build_nodes(batch)
    frontages = build_frontages(batch)
    vegetation = build_vegetation(batch, alignment["segments"])
    activity = build_activity(batch)
    lighting = build_lighting(batch, alignment["segments"])
    consolidation = consolidate(batch)
    objects = batch.finalize()
    validation = validate_geometry(objects)
    for obj in objects:
        obj["assetId"] = "archive-urban-stream-final-v11"
        obj["canonical"] = False
        obj["v3Applied"] = False
        obj["directReferenceCopy"] = False
        obj["originality"] = "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY"
        obj["generationSeed"] = 111901
    glb = output / "archive-urban-stream-final.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", export_yup=True, export_normals=True, export_texcoords=False, export_materials="EXPORT", export_apply=True)
    report = {
        "status": "PASS", "glb": str(glb), "bytes": glb.stat().st_size,
        "geometry": batch.statistics(), "consolidation": consolidation,
        "validation": validation, "sections": sections, "bridges": bridges,
        "nodes": nodes, "frontages": frontages, "vegetation": vegetation,
        "activity": activity, "lighting": lighting, "imageDatablocks": len(bpy.data.images),
        "externalImages": 0, "officeV5Changed": False, "canonical": False,
        "v3Applied": False, "directReferenceCopy": False,
        "originality": "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY",
    }
    (output / "final-stream-generation-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "glb": str(glb), "bytes": report["bytes"], "triangles": report["geometry"]["triangles"], "meshObjects": report["geometry"]["meshObjects"]}))


if __name__ == "__main__":
    main()
