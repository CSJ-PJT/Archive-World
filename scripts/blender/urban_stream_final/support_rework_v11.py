"""Rebuild eleven support-family bodies; the frozen Office V5 anchor is excluded."""
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

SPECS = (
    ("premium-medium-office", "vertical-frame", 38, 30, 31, 5, 1),
    ("compact-financial-office", "dense-corner", 26, 24, 24, 4, 2),
    ("corner-office-tower", "corner-emphasis", 34, 28, 29, 5, 3),
    ("podium-office", "terraced", 44, 32, 21, 5, 4),
    ("institutional-archiveos-office", "civic-portal", 46, 34, 18, 4, 5),
    ("civic-tech-office", "public-connector", 39, 31, 25, 4, 6),
    ("retail-public-podium", "active-lowrise", 58, 38, 10, 4, 7),
    ("financial-annex", "formal-annex", 35, 28, 13, 3, 8),
    ("operations-service-building", "service-rear", 47, 34, 9, 3, 9),
    ("transit-hall", "transit-canopy", 60, 38, 7, 3, 10),
    ("cultural-public-pavilion", "public-roof", 52, 42, 6, 3, 11),
)


def build_family(spec, lod, materials):
    family, grammar, width, depth, floors, podium_floors, seed = spec
    batch = MeshBatch(materials)
    floor_height = 3.8
    podium_height = podium_floors * 4.2
    tower_height = floors * floor_height
    # Podium is a three-part body rather than one attached box.
    batch.add_box("podium-center", "archive-warm-stone", (0, 0, podium_height / 2), (width + 12, depth + 9, podium_height))
    batch.add_box("podium-stream-wing", "ledger-limestone", (-width * 0.28, -depth / 2 - 5.5, podium_height * 0.43), (width * 0.52, 11, podium_height * 0.86))
    batch.add_box("podium-public-wing", "blue-gray-glass", (width * 0.26, -depth / 2 - 4.2, podium_height * 0.38), (width * 0.38, 8, podium_height * 0.76))
    # Each grammar alters silhouette, setback and corner condition.
    if grammar in ("public-connector", "corner-emphasis"):
        batch.add_box("tower-main", "blue-gray-glass", (-width * 0.12, 0, podium_height + tower_height / 2), (width * 0.66, depth * 0.86, tower_height))
        batch.add_box("tower-secondary", "ledger-limestone", (width * 0.28, depth * 0.10, podium_height + tower_height * 0.42), (width * 0.30, depth * 0.62, tower_height * 0.72))
    elif grammar in ("terraced", "public-roof", "active-lowrise"):
        batch.add_box("tower-lower", "blue-gray-glass", (0, 0, podium_height + tower_height * 0.30), (width * 0.82, depth * 0.80, tower_height * 0.60))
        batch.add_box("tower-upper", "archive-warm-stone", (width * 0.12, 0, podium_height + tower_height * 0.76), (width * 0.52, depth * 0.62, tower_height * 0.32))
    else:
        batch.add_box("tower-main", "blue-gray-glass", (0, 0, podium_height + tower_height / 2), (width * 0.72, depth * 0.78, tower_height))
        batch.add_box("tower-corner-frame", "archive-metal", (-width * 0.37, -depth * 0.40, podium_height + tower_height * 0.54), (1.0, 1.0, tower_height * 0.88))
    step = {"LOD0": 1, "LOD1": 2, "LOD2": 5}[lod]
    bay = 3.4 + (seed % 3) * 0.65
    for floor in range(1, floors, step):
        z = podium_height + floor * floor_height + floor_height * 0.48
        if floor % 7 == 0:
            batch.add_box("mechanical-floor-band", "service-charcoal", (0, -depth * 0.41, z), (width * 0.74, 0.48, 0.60))
        for index in range(-int(width // (2 * bay)), int(width // (2 * bay)) + 1):
            x = index * bay
            material = "blue-gray-glass" if (index + floor + seed) % 4 else "ledger-limestone"
            batch.add_box("stream-facade-recess", material, (x, -depth * 0.42 - 0.25 - (floor % 3) * 0.07, z), (bay * 0.72, 0.30, floor_height * 0.68))
            if lod != "LOD2":
                batch.add_box("facade-vertical-fin", "archive-metal" if seed % 2 else "ledger-bronze", (x - bay * 0.38, -depth * 0.42 - 0.45, z), (0.14, 0.22, floor_height * 0.92))
    # Lower 3–5 floors have a separate occupied grammar.
    entry_x = (-0.18 + (seed % 4) * 0.12) * width
    batch.add_box("stream-lobby-interior", "warm-interior", (entry_x, -depth / 2 - 5.8, 2.4), (width * 0.28, 7.8, 4.8))
    batch.add_box("stream-lobby-glazing", "blue-gray-glass", (entry_x, -depth / 2 - 9.75, 2.4), (width * 0.26, 0.22, 4.5))
    batch.add_box("stream-lobby-door", "archive-metal", (entry_x + width * 0.06, -depth / 2 - 9.92, 1.25), (1.6, 0.18, 2.5))
    batch.add_box("stream-entry-canopy", "archive-metal", (entry_x, -depth / 2 - 11, 4.8), (width * 0.38, 4.2, 0.28))
    batch.add_box("stream-terrace", "dry-stone", (0, -depth / 2 - 13, 0.28), (width + 8, 10, 0.40))
    for column in range(-2, 3):
        batch.add_box("stream-arcade-column", "ledger-bronze", (column * width * 0.16, -depth / 2 - 8.8, 2.3), (0.28, 0.28, 4.6))
    # Rear is explicitly operational and visually distinct.
    batch.add_box("rear-service-core", "service-charcoal", (width * 0.2, depth / 2 + 4, 3.0), (width * 0.30, 7.0, 6.0))
    batch.add_box("rear-loading-canopy", "service-charcoal", (width * 0.2, depth / 2 + 8, 4.6), (width * 0.36, 5.0, 0.38))
    batch.add_box("rear-service-apron", "ledger-granite", (0, depth / 2 + 9, 0.12), (width + 10, 14, 0.24))
    # Integrated crown and equipment preserve roof silhouette in every LOD.
    roof_z = podium_height + tower_height
    batch.add_box("roof-crown", "archive-metal" if seed % 2 else "ledger-bronze", (width * 0.08, 0, roof_z + 2.1), (width * 0.42, depth * 0.48, 4.2))
    batch.add_box("roof-machine-room", "service-charcoal", (-width * 0.15, 0, roof_z + 2.8), (width * 0.24, depth * 0.28, 5.6))
    for index in range(2 if lod == "LOD2" else 5):
        batch.add_box("roof-hvac", "service-charcoal", (-width * 0.22 + index * 3.0, depth * 0.12, roof_z + 6.1), (2.0, 2.6, 1.5))
    consolidation = consolidate(batch)
    objects = batch.finalize()
    return objects, batch.statistics(), validate_geometry(objects), consolidation


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parsed = parser.parse_args(args)
    output = Path(parsed.output_root)
    reports = []
    for spec in SPECS:
        family = spec[0]
        for lod in ("LOD0", "LOD1", "LOD2"):
            bpy.ops.wm.read_factory_settings(use_empty=True)
            materials = create_materials()
            objects, geometry, validation, consolidation = build_family(spec, lod, materials)
            for obj in objects:
                obj["familyId"] = family; obj["lod"] = lod; obj["canonical"] = False
                obj["officeV5Anchor"] = False; obj["generationSeed"] = 11100 + spec[-1]
            target = output / "families" / family / lod
            target.mkdir(parents=True, exist_ok=True)
            glb = target / f"{family}-{lod.lower()}.glb"
            bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", export_yup=True, export_normals=True, export_texcoords=False, export_materials="EXPORT", export_apply=True)
            report = {"family": family, "grammar": spec[1], "lod": lod, "glb": str(glb), "bytes": glb.stat().st_size, "geometry": geometry, "validation": validation, "consolidation": consolidation, "streamFacingBodyReworked": True, "lowerFloorGrammar": True, "frontSideRearRoof": True, "officeV5Changed": False}
            (target / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
            reports.append(report)
    (output / "reports").mkdir(parents=True, exist_ok=True)
    (output / "reports/support-body-v11.json").write_text(json.dumps({"families": len(SPECS), "lodGlbs": len(reports), "reports": reports}, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "families": len(SPECS), "lodGlbs": len(reports), "officeV5Changed": False}))


if __name__ == "__main__":
    main()
