"""Regenerate every non-anchor Core support family with a wall-first envelope.

Office V5 is deliberately excluded.  Window infill is bounded by structural
jamb/head/sill returns and an occupied room back; no facade card is allowed to
float in front of a solid tower mass.
"""
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


def _front_envelope(batch, width, depth, base_z, floors, floor_h, lod, seed,
                    stone, accent):
    step = {"LOD0": 1, "LOD1": 2, "LOD2": 6}[lod]
    bay_count = (max(4, round(width / 9.5)) if lod == "LOD2" else
                 max(5, round(width / (3.5 + .25 * (seed % 3)))))
    pitch = width / bay_count
    face_y = -depth * .5
    glass_y = face_y + .34
    room_back_y = face_y + 1.65
    height = floors * floor_h
    batch.add_box("integrated-front-room-back", "warm-interior",
                  (0, room_back_y, base_z + height * .5),
                  (width - .5, .18, height))
    for floor in range(0, floors, step):
        span = min(step, floors - floor)
        opening_h = span * floor_h - .72
        opening_z = base_z + floor * floor_h + span * floor_h * .5
        batch.add_box("integrated-floor-plate", "service-charcoal",
                      (0, face_y + .90, base_z + floor * floor_h + .10),
                      (width - .42, 1.32, .18))
        for bay in range(bay_count):
            x = -width * .5 + (bay + .5) * pitch
            blind = (floor + bay + seed) % 11 == 0
            material = stone if blind else (
                "occupied-window-glass" if (floor + bay + seed) % 4 == 0
                else "blue-gray-glass")
            batch.add_box("integrated-front-infill", material,
                          (x, glass_y, opening_z),
                          (pitch - .34, .14, opening_h))
            if lod == "LOD2":
                continue
            for side in (-1, 1):
                batch.add_box("integrated-front-jamb-return", accent,
                              (x + side * (pitch * .5 - .14),
                               face_y + .31, opening_z),
                              (.16, .72, opening_h + .12))
            batch.add_box("integrated-front-head-return", accent,
                          (x, face_y + .31, opening_z + opening_h * .5),
                          (pitch - .18, .72, .17))
            batch.add_box("integrated-front-sill-return", stone,
                          (x, face_y + .31, opening_z - opening_h * .5),
                          (pitch - .18, .72, .22))
        batch.add_box("integrated-front-spandrel", stone,
                      (0, face_y + .12, base_z + (floor + span) * floor_h),
                      (width, .32, .36 if floor % 8 else .58))
    for bay in range(bay_count + 1):
        x = -width * .5 + bay * pitch
        batch.add_box("integrated-front-structural-pier", accent,
                      (x, face_y + .08, base_z + height * .5),
                      (.20 if lod != "LOD2" else .28, .64, height + .36))
    return {"bayCount": bay_count, "detachedWindows": 0,
            "glassRecessM": .34, "boundedOpenings": True,
            "structuralReturns": lod != "LOD2",
            "sharedStructuralGrid": lod == "LOD2"}


def _side_rear_envelope(batch, width, depth, base_z, floors, floor_h, lod,
                        seed, stone, accent):
    step = {"LOD0": 1, "LOD1": 2, "LOD2": 6}[lod]
    side_bays = (3 if lod == "LOD2" else max(4, round(depth / 5.2)))
    pitch = depth * .78 / side_bays
    for side in (-1, 1):
        face_x = side * width * .5
        for floor in range(0, floors, step):
            span = min(step, floors - floor)
            opening_h = span * floor_h - .82
            z = base_z + floor * floor_h + span * floor_h * .5
            for bay in range(side_bays):
                y = -depth * .39 + (bay + .5) * pitch
                material = stone if (floor + bay + seed) % 9 == 0 else "blue-gray-glass"
                batch.add_box("integrated-side-infill", material,
                              (face_x - side * .32, y, z),
                              (.14, pitch - .34, opening_h))
                if lod == "LOD2":
                    continue
                for edge in (-1, 1):
                    batch.add_box("integrated-side-jamb-return", accent,
                                  (face_x - side * .28,
                                   y + edge * (pitch * .5 - .13), z),
                                  (.68, .16, opening_h + .12))
                batch.add_box("integrated-side-head-return", accent,
                              (face_x - side * .28, y, z + opening_h * .5),
                              (.68, pitch - .18, .17))
                batch.add_box("integrated-side-sill-return", stone,
                              (face_x - side * .28, y, z - opening_h * .5),
                              (.68, pitch - .18, .22))
    rear_y = depth * .5
    rear_bays = max(4, round(width / 5.0))
    rear_pitch = width * .78 / rear_bays
    for floor in range(0, floors, step):
        span = min(step, floors - floor)
        z = base_z + floor * floor_h + span * floor_h * .5
        for bay in range(rear_bays):
            x = -width * .39 + (bay + .5) * rear_pitch
            material = "service-charcoal" if (floor + bay + seed) % 6 == 0 else "blue-gray-glass"
            batch.add_box("integrated-rear-infill", material,
                          (x, rear_y - .28, z),
                          (rear_pitch - .38, .14, span * floor_h - .94))
        batch.add_box("integrated-rear-service-band", accent,
                      (0, rear_y - .10, base_z + (floor + span) * floor_h),
                      (width * .80, .42, .38))


def _deep_ground_floor(batch, width, depth, podium_h, seed, stone, accent):
    facing_y = -depth * .5 - 5.4
    lobby_x = (-.18 + (seed % 4) * .12) * width
    lobby_w = width * (.30 + .02 * (seed % 3))
    room_depth = 10.2
    batch.add_box("occupied-lobby-floor", "ledger-granite",
                  (lobby_x, facing_y, .16), (lobby_w, room_depth, .32))
    batch.add_box("occupied-lobby-ceiling", "warm-interior",
                  (lobby_x, facing_y, 7.62), (lobby_w, room_depth, .30))
    batch.add_box("occupied-lobby-back", "warm-interior",
                  (lobby_x, facing_y + room_depth * .5, 3.85),
                  (lobby_w, .22, 7.25))
    bays = max(3, round(lobby_w / 4.2))
    pitch = lobby_w / bays
    for bay in range(bays):
        x = lobby_x - lobby_w * .5 + (bay + .5) * pitch
        batch.add_box("occupied-lobby-glass-infill", "frontage-glass",
                      (x, facing_y - room_depth * .5 + .34, 3.85),
                      (pitch - .30, .14, 6.82))
        for side in (-1, 1):
            batch.add_box("occupied-lobby-jamb-return", accent,
                          (x + side * (pitch * .5 - .12),
                           facing_y - room_depth * .5 + .32, 3.85),
                          (.15, .70, 7.05))
        batch.add_box("occupied-lobby-ceiling-light", "warm-light",
                      (x, facing_y, 7.40), (pitch * .62, 4.8, .08))
        batch.add_box("occupied-lobby-furniture", "timber-accent",
                      (x, facing_y + 1.0, .84),
                      (pitch * .52, 1.2, 1.10))
    batch.add_box("inhabited-entry-canopy", accent,
                  (lobby_x, facing_y - room_depth * .5 - 2.2, 7.30),
                  (lobby_w + 5.0, 5.0, .38))
    batch.add_box("inhabited-entry-soffit", "warm-light",
                  (lobby_x, facing_y - room_depth * .5 - 2.2, 7.08),
                  (lobby_w + 3.8, 4.4, .08))
    # A second public bay prevents a single pasted lobby from carrying the base.
    retail_x = -lobby_x * .52
    batch.add_box("occupied-public-bay", "warm-interior",
                  (retail_x, -depth * .5 - 4.0, 3.35),
                  (width * .28, 7.0, 6.7))
    batch.add_box("occupied-public-bay-glass", "frontage-glass",
                  (retail_x, -depth * .5 - 7.55, 3.35),
                  (width * .27, .14, 6.2))
    batch.add_box("occupied-public-bay-canopy", stone,
                  (retail_x, -depth * .5 - 9.0, 6.72),
                  (width * .32, 3.2, .32))
    return {"lobbyDepthM": room_depth, "interiorVolume": True,
            "publicBayCount": 2, "detachedGlazing": 0}


def _grammar_specific_architecture(batch, grammar, width, depth, podium_h,
                                   roof_z, lod, stone, accent):
    """Give every support family a legible role beyond height and scale."""
    components = []
    detail_step = 2 if lod == "LOD2" else 1
    if grammar == "vertical-frame":
        for x in (-width * .34, 0, width * .34)[::detail_step]:
            batch.add_box("identity-vertical-megaframe", accent,
                          (x, -depth * .38, podium_h + (roof_z - podium_h) * .5),
                          (.72, 1.4, roof_z - podium_h + 3.0))
        components += ["vertical-megaframe", "stone-base"]
    elif grammar == "dense-corner":
        for side in (-1, 1):
            batch.add_box("identity-corner-lantern", "frontage-glass",
                          (side * width * .40, -depth * .40, podium_h + 13.0),
                          (width * .16, 3.0, 23.0))
            batch.add_box("identity-corner-lantern-frame", accent,
                          (side * width * .40, -depth * .45, podium_h + 13.0),
                          (width * .18, .34, 24.0))
        components += ["corner-lanterns", "dense-curtain-wall"]
    elif grammar == "corner-emphasis":
        batch.add_box("identity-corner-wing-left", stone,
                      (-width * .42, -depth * .18, podium_h + 17.0),
                      (width * .18, depth * .52, 34.0))
        batch.add_box("identity-corner-wing-right", "blue-gray-glass",
                      (width * .38, -depth * .31, podium_h + 12.0),
                      (width * .22, depth * .30, 24.0))
        components += ["asymmetric-corner-wings", "corner-entry"]
    elif grammar == "terraced":
        for level, factor in enumerate((.92, .72, .52)[::detail_step]):
            batch.add_box("identity-occupied-terrace", "dry-stone",
                          (width * .18 * (level % 2), -depth * .22,
                           podium_h + 10.0 + level * 13.0),
                          (width * factor, depth * (.66 - level * .10), .46))
            batch.add_box("identity-terrace-planter", stone,
                          (-width * .28, -depth * .40,
                           podium_h + 10.6 + level * 13.0),
                          (width * .22, 2.2, 1.0))
        components += ["three-stage-terraces", "occupied-setbacks"]
    elif grammar == "civic-portal":
        for side in (-1, 1):
            batch.add_box("identity-civic-portal-pier", accent,
                          (side * width * .34, -depth * .56, 10.5),
                          (1.1, 2.0, 21.0))
        batch.add_box("identity-civic-portal-beam", accent,
                      (0, -depth * .56, 20.2), (width * .70, 2.0, 1.2))
        batch.add_box("identity-civic-public-hall", "frontage-glass",
                      (0, -depth * .52, 8.0), (width * .60, 1.2, 14.0))
        components += ["civic-portal", "public-hall"]
    elif grammar == "public-connector":
        batch.add_box("identity-public-connector", "frontage-glass",
                      (0, -depth * .44, podium_h + 15.0),
                      (width * .78, 4.0, 6.0))
        batch.add_box("identity-public-connector-frame", accent,
                      (0, -depth * .48, podium_h + 15.0),
                      (width * .84, .52, 7.0))
        components += ["elevated-public-connector", "civic-tech-atrium"]
    elif grammar == "active-lowrise":
        for x in (-width * .30, 0, width * .30)[::detail_step]:
            batch.add_box("identity-retail-lantern", "frontage-glass",
                          (x, -depth * .57, 6.0),
                          (width * .20, 2.4, 10.0))
            batch.add_box("identity-retail-canopy", accent,
                          (x, -depth * .62, 10.8),
                          (width * .23, 4.0, .32))
        components += ["three-retail-lanterns", "public-roof"]
    elif grammar == "formal-annex":
        for x in range(-12, 13, 6)[::detail_step]:
            batch.add_cylinder("identity-formal-colonnade", accent,
                               (x, -depth * .59, 5.0), .28, 9.5, 18)
        batch.add_box("identity-formal-entablature", stone,
                      (0, -depth * .59, 9.7), (width * .86, 1.4, 1.0))
        components += ["formal-colonnade", "granite-plinth"]
    elif grammar == "service-rear":
        for x in (-width * .28, 0, width * .28)[::detail_step]:
            batch.add_box("identity-service-screen", "service-charcoal",
                          (x, depth * .63, 8.0),
                          (width * .20, 1.0, 14.0))
        batch.add_box("identity-service-crown", "service-charcoal",
                      (0, 0, roof_z + 4.0), (width * .66, depth * .50, 7.0))
        components += ["screened-service-rear", "operations-crown"]
    elif grammar == "transit-canopy":
        batch.add_box("identity-transit-long-canopy", accent,
                      (0, -depth * .66, 9.0),
                      (width * 1.10, 12.0, .58))
        for x in range(-24, 25, 8)[::detail_step]:
            batch.add_cylinder("identity-transit-canopy-column", accent,
                               (x, -depth * .66, 4.7), .20, 8.2, 18)
        batch.add_box("identity-transit-entry-volume", "frontage-glass",
                      (0, -depth * .56, 5.4),
                      (width * .44, 5.0, 9.6))
        components += ["long-span-canopy", "station-entry-volume"]
    elif grammar == "public-roof":
        for x, height in ((-width * .28, 5.0), (0, 8.0), (width * .28, 6.5))[::detail_step]:
            batch.add_box("identity-cultural-roof-lantern", "frontage-glass",
                          (x, 0, roof_z + height * .5),
                          (width * .20, depth * .34, height))
            batch.add_box("identity-cultural-roof-cap", accent,
                          (x, 0, roof_z + height + .3),
                          (width * .24, depth * .38, .42))
        components += ["asymmetric-roof-lanterns", "public-pavilion"]
    return components


def build_family(spec, lod, materials):
    family, grammar, width, depth, floors, podium_floors, seed = spec
    batch = MeshBatch(materials)
    floor_h = 3.8
    podium_h = podium_floors * 4.2
    tower_h = floors * floor_h
    stone = "archive-warm-stone" if seed % 2 else "ledger-limestone"
    accent = "archive-metal" if seed % 3 else "ledger-bronze"
    # Articulated base and setback masses differ by grammar.
    batch.add_box("integrated-podium-core", stone,
                  (0, 1.1, podium_h * .5),
                  (width + 11.0, depth + 6.0, podium_h))
    batch.add_box("integrated-podium-stream-wing", "ledger-limestone",
                  (-width * .27, -depth * .5 - 3.2, podium_h * .42),
                  (width * .50, 7.0, podium_h * .82))
    batch.add_box("integrated-podium-public-wing", "blue-gray-glass",
                  (width * .25, -depth * .5 - 2.4, podium_h * .36),
                  (width * .38, 5.4, podium_h * .70))
    lower_floors = max(4, int(floors * (.62 if seed % 2 else .68)))
    upper_floors = floors - lower_floors
    lower_w = width * (.72 + .03 * (seed % 3))
    lower_d = depth * (.70 + .02 * ((seed + 1) % 3))
    lower_x = width * (-.08 if seed % 2 else .07)
    lower_h = lower_floors * floor_h
    batch.add_box("integrated-lower-structural-core", stone,
                  (lower_x, 1.15, podium_h + lower_h * .5),
                  (lower_w, lower_d - 2.3, lower_h))
    front = _front_envelope(batch, lower_w, lower_d, podium_h,
                            lower_floors, floor_h, lod, seed, stone, accent)
    _side_rear_envelope(batch, lower_w, lower_d, podium_h, lower_floors,
                        floor_h, lod, seed, stone, accent)
    if upper_floors > 0:
        upper_w = lower_w * (.66 + .04 * (seed % 3))
        upper_d = lower_d * (.70 + .03 * ((seed + 1) % 3))
        upper_x = lower_x + width * (.08 if seed % 2 else -.07)
        upper_h = upper_floors * floor_h
        batch.add_box("integrated-upper-structural-core", stone,
                      (upper_x, 1.0, podium_h + lower_h + upper_h * .5),
                      (upper_w, upper_d - 2.1, upper_h))
        _front_envelope(batch, upper_w, upper_d, podium_h + lower_h,
                        upper_floors, floor_h, lod, seed + 4, stone, accent)
        _side_rear_envelope(batch, upper_w, upper_d, podium_h + lower_h,
                            upper_floors, floor_h, lod, seed + 4, stone, accent)
    ground = _deep_ground_floor(batch, width, depth, podium_h, seed, stone, accent)
    # Operational rear and integrated crown remain complete at all LODs.
    batch.add_box("rear-service-core", "service-charcoal",
                  (width * .20, depth * .5 + 4.0, 3.0),
                  (width * .30, 7.0, 6.0))
    batch.add_box("rear-loading-canopy", "service-charcoal",
                  (width * .20, depth * .5 + 8.0, 4.6),
                  (width * .36, 5.0, .38))
    roof_z = podium_h + tower_h
    batch.add_box("integrated-roof-crown", accent,
                  (width * .08, 0, roof_z + 2.1),
                  (width * (.36 + .03 * (seed % 3)), depth * .44, 4.2))
    batch.add_box("integrated-machine-room", "service-charcoal",
                  (-width * .15, 0, roof_z + 2.8),
                  (width * .24, depth * .28, 5.6))
    for index in range(2 if lod == "LOD2" else 5):
        batch.add_box("integrated-roof-hvac", "service-charcoal",
                      (-width * .22 + index * 3.0, depth * .12, roof_z + 6.1),
                      (2.0, 2.6, 1.5))
    identity = _grammar_specific_architecture(
        batch, grammar, width, depth, podium_h, roof_z, lod, stone, accent)
    consolidation = consolidate(batch)
    objects = batch.finalize()
    return objects, batch.statistics(), validate_geometry(objects), consolidation, {
        "front": front, "groundFloor": ground, "detachedWindowCount": 0,
        "frontSideRearRoof": True, "identityComponents": identity,
    }


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
            objects, geometry, validation, consolidation, envelope = build_family(
                spec, lod, materials)
            assert not validation["emptyMeshes"] and not validation["looseGeometry"]
            assert envelope["detachedWindowCount"] == 0
            assert len(bpy.data.images) == 0
            for obj in objects:
                obj["familyId"] = family
                obj["lod"] = lod
                obj["canonical"] = False
                obj["officeV5Anchor"] = False
                obj["generationSeed"] = 11370 + spec[-1]
            target = output / "families" / family / lod
            target.mkdir(parents=True, exist_ok=True)
            glb = target / f"{family}-{lod.lower()}.glb"
            bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB",
                                      export_yup=True, export_normals=True,
                                      export_texcoords=False, export_materials="EXPORT",
                                      export_apply=True)
            report = {
                "family": family, "grammar": spec[1], "lod": lod,
                "glb": str(glb), "bytes": glb.stat().st_size,
                "geometry": geometry, "validation": validation,
                "consolidation": consolidation, "envelope": envelope,
                "wallFirst": True, "streamFacingBodyReworked": True,
                "lowerFloorGrammar": True, "frontSideRearRoof": True,
                "officeV5Changed": False, "imageDatablocks": len(bpy.data.images),
            }
            (target / "report.json").write_text(json.dumps(report, indent=2),
                                                 encoding="utf-8")
            reports.append(report)
    (output / "reports").mkdir(parents=True, exist_ok=True)
    summary = {"status": "TECHNICAL_PASS_VISUAL_GATE_PENDING",
               "revision": 13, "families": len(SPECS),
               "lodGlbs": len(reports), "detachedWindowCount": 0,
               "officeV5Changed": False, "reports": reports}
    (output / "reports/support-body-v13-integrated.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"status": summary["status"], "families": len(SPECS),
                      "lodGlbs": len(reports), "detachedWindowCount": 0,
                      "officeV5Changed": False}))


if __name__ == "__main__":
    main()
