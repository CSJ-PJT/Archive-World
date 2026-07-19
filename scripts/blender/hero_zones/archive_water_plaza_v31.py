"""Archive Water Plaza V31 attached facade-room and podium-detail pass.

This pass answers the failed floating-window read with a stricter rule: every
new glazed element is the front of a bounded room and every projecting frame
returns into the constructed facade.  The concept reference supplies only an
abstract quality direction; no identifiable architecture is reproduced.
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
import archive_water_plaza_v28 as v28
import archive_water_plaza_v29 as v29
import archive_water_plaza_v30 as v30


def add_facade_room_hierarchy(batch, spec):
    """Add attached multi-floor bays and a physically bounded entry vestibule."""
    x, y, width, depth, floors, floor_h, style = spec
    facing = -1 if y > 0 else 1
    inside = -facing
    podium_h = 7.8 + (style % 3) * .9
    lower_h = floors * floor_h * (.56 + .02 * (style % 2))
    lower_w, lower_d = width * .78, depth * .76
    facade_y = y + facing * lower_d * .5
    accent = "archive-metal" if style < 3 else "ledger-bronze"
    stone = "archive-warm-stone" if style < 3 else "ledger-limestone"

    # Three vertically staggered two-storey rooms prevent a single grid from
    # running uninterrupted up the tower.  The room back, side returns, floor,
    # ceiling and glass all meet one another; the frame itself penetrates the
    # facade datum by 0.18m.
    bay_w = lower_w * (.16 + .012 * (style % 3))
    room_depth = 2.4 + .25 * (style % 2)
    for index, lateral in enumerate((-.27, .02, .29)):
        room_x = x + lower_w * lateral
        room_z = podium_h + lower_h * (.22 + index * .245)
        room_h = min(8.2, floor_h * 2.18)
        room_y = facade_y + inside * room_depth * .5
        batch.add_box("v31-facade-room-floor", "ledger-granite",
                      (room_x, room_y, room_z - room_h * .5 + .14),
                      (bay_w, room_depth, .28))
        batch.add_box("v31-facade-room-ceiling", "warm-interior",
                      (room_x, room_y, room_z + room_h * .5 - .11),
                      (bay_w, room_depth, .22))
        batch.add_box("v31-facade-room-back", "warm-interior",
                      (room_x, facade_y + inside * (room_depth - .10), room_z),
                      (bay_w, .20, room_h))
        for side in (-1, 1):
            batch.add_box("v31-facade-room-return", stone,
                          (room_x + side * bay_w * .5, room_y, room_z),
                          (.24, room_depth, room_h + .34))
            batch.add_box("v31-attached-double-height-frame", accent,
                          (room_x + side * (bay_w * .5 + .16),
                           facade_y + facing * .28, room_z),
                          (.30, .92, room_h + .72))
        batch.add_box("v31-facade-room-glass", "occupied-window-glass",
                      (room_x, facade_y - facing * .05, room_z),
                      (bay_w - .34, .10, room_h - .32))
        for level in (-1, 0, 1):
            batch.add_box("v31-facade-room-transom", accent,
                          (room_x, facade_y + facing * .18,
                           room_z + level * room_h * .29),
                          (bay_w + .24, .56, .16))
        batch.add_box("v31-facade-room-head", accent,
                      (room_x, facade_y + facing * .28,
                       room_z + room_h * .5 + .28),
                      (bay_w + .62, .92, .34))

    # A real entry vestibule replaces the reading of a glass card under a flat
    # canopy.  It projects from the podium but returns into the room behind.
    podium_depth = depth + 5.0
    podium_face = y + facing * podium_depth * .5
    lobby_x = x + width * (-.19 + .075 * (style % 4))
    vestibule_depth = 4.8
    vestibule_y = podium_face + facing * vestibule_depth * .5
    batch.add_box("v31-entry-vestibule-floor", "ledger-granite",
                  (lobby_x, vestibule_y, 2.42), (8.8, vestibule_depth, .28))
    batch.add_box("v31-entry-vestibule-soffit", "warm-interior",
                  (lobby_x, vestibule_y, 6.62), (8.8, vestibule_depth, .22))
    for side in (-1, 1):
        batch.add_box("v31-entry-vestibule-return", stone,
                      (lobby_x + side * 4.4, vestibule_y, 4.48),
                      (.34, vestibule_depth, 4.4))
    batch.add_box("v31-entry-vestibule-glass", "frontage-glass",
                  (lobby_x, podium_face + facing * (vestibule_depth - .06), 4.5),
                  (8.35, .12, 4.0))
    batch.add_box("v31-entry-vestibule-door", accent,
                  (lobby_x + 1.65, podium_face + facing * (vestibule_depth + .04), 3.65),
                  (1.45, .18, 2.9))
    batch.add_box("v31-entry-portal-head", accent,
                  (lobby_x, podium_face + facing * (vestibule_depth + .12), 6.68),
                  (9.4, .34, .36))

    # Side-wall stone coursing and framed service door scale the podium flanks
    # without covering the occupied side-room glazing added in V30.
    podium_w = width + 7.0
    for side in (-1, 1):
        side_x = x + side * podium_w * .5
        for course in range(1, 5):
            batch.add_box("v31-podium-side-stone-course", stone,
                          (side_x + side * .08, y, .62 + course * 1.18),
                          (.16, (depth + 5.0) * .94, .10))
        service_y = y - facing * (depth + 5.0) * .30
        batch.add_box("v31-podium-side-service-portal", accent,
                      (side_x + side * .14, service_y, 2.2),
                      (.28, 3.8, 4.4))
        batch.add_box("v31-podium-side-service-door", "service-charcoal",
                      (side_x + side * .30, service_y, 1.55),
                      (.12, 2.5, 3.1))


def add_refined_building(batch, spec):
    v14.add_production_building(batch, spec)
    add_facade_room_hierarchy(batch, spec)


def add_precision_landscape_rooms():
    """Compose linear garden/seating rooms along the oversized civic terrace."""
    batch = v12.HeroBatch(v12.create_materials())
    activity = []
    room_specs = (
        (-338, 0), (-310, 1), (-280, 2), (-218, 3), (-186, 4), (-158, 5),
    )
    for side in (-1, 1):
        # Alternating civic paving fields give the 24m terrace a readable
        # hierarchy without obstructing its barrier-free movement spine.
        for field, field_x in enumerate((-337, -302, -267, -218, -183, -153)):
            batch.add_box("v31-civic-paving-field",
                          "dry-stone" if field % 2 else "promenade-paver",
                          (field_x, side * 24.9, 2.275),
                          (24.0 if field < 3 else 22.0, 7.2, .045))
        for index, (x, variant) in enumerate(room_specs):
            y = side * (32.4 + (variant % 2) * 1.2)
            length = 13.0 + (variant % 3) * 1.8
            stone = "archive-warm-stone" if (variant + (1 if side > 0 else 0)) % 2 else "dry-stone"
            batch.add_box("v31-linear-garden-retaining-edge", stone,
                          (x, y, 2.74), (length, 3.8, .92))
            batch.add_box("v31-linear-garden-soil", "soil-v11",
                          (x, y, 3.24), (length - .55, 3.25, .12))
            # Layered planting forms a waist-high spatial edge while keeping
            # entrances and the stream view corridor visible.
            for planting in range(7):
                px = x - length * .40 + planting * length * .80 / 6
                material = ("foliage-deep", "foliage-mid", "foliage-light")[(variant + planting) % 3]
                batch.add_uv_sphere("v31-garden-layered-shrub", material,
                                    (px, y + side * (.18 if planting % 2 else -.28), 3.78),
                                    .58 + .10 * ((planting + variant) % 3), 14, 7,
                                    (1.18, .72, .64 + .08 * (planting % 2)))
            seat_y = y - side * 2.25
            batch.add_box("v31-garden-integrated-seat", "timber-accent",
                          (x, seat_y, 2.82), (length * .62, .72, .20))
            batch.add_box("v31-garden-seat-back", "timber-accent",
                          (x, seat_y + side * .30, 3.28), (length * .62, .14, .86))
            # Small steel frame and warm soffit define every third room as a
            # shaded social node instead of another loose furniture cluster.
            if variant % 3 == 1:
                for frame_x in (-1, 1):
                    batch.add_box("v31-garden-shade-frame", "archive-metal",
                                  (x + frame_x * length * .39, seat_y, 5.1),
                                  (.18, 2.8, 4.6))
                batch.add_box("v31-garden-shade-canopy", "archive-metal",
                              (x, seat_y, 7.34), (length * .84, 3.2, .22))
                batch.add_box("v31-garden-shade-light", "warm-light",
                              (x, seat_y, 7.17), (length * .65, 1.4, .06))
            for person in range(3):
                px = x - 2.2 + person * 2.1
                action = "seated" if person != 1 else "conversation"
                activity.append(v12.add_human(
                    batch, px, seat_y - side * .55, 0 if side > 0 else 3.14159,
                    231000 + side * 100 + index * 10 + person, action, z_base=2.3,
                ))
    objects = batch.finalize()
    for obj in objects:
        obj["heroZone"] = "archive-water-plaza"
        obj["precisionPublicRealm"] = True
        obj["canonical"] = False
        obj["v3Applied"] = False
    return objects, batch.statistics(), activity


def apply_selective_architectural_edges(objects):
    """Bevel only close-range masonry/timber batches, never every component."""
    widths = {
        "archive-warm-stone": .035,
        "ledger-limestone": .035,
        "dry-stone": .028,
        "timber-accent": .022,
    }
    applied = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        lowered = obj.name.lower()
        width = next((value for token, value in widths.items() if token in lowered), None)
        if width is None:
            continue
        modifier = obj.modifiers.new(name="V31 selective architectural edge", type="BEVEL")
        modifier.width = width
        modifier.segments = 1
        modifier.limit_method = "ANGLE"
        modifier.angle_limit = .60
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        obj.select_set(False)
        applied.append({"object": obj.name, "widthM": width, "segments": 1})
    return applied


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
    v14.FACADE_GLASS_RECESS_M = .26
    v14.FACADE_GLASS_THICKNESS_M = .08
    v14.TOWER_FACADE_CAVITY_DEPTH_M = .34
    v14.ACTIVE_FRONTAGE_GRADE_M = 2.3
    original_building, original_tree = v12.add_building, v12.add_tree
    v12.add_building, v12.add_tree = add_refined_building, v30.add_natural_tree
    try:
        base_objects, base_geometry, base_validation, base_consolidation, trees, base_activity = v12.build_zone()
    finally:
        v12.add_building, v12.add_tree = original_building, original_tree
    public_objects, public_geometry, public_activity = v29.add_inhabited_promenade()
    landscape_objects, landscape_geometry, landscape_activity = add_precision_landscape_rooms()
    objects = base_objects + public_objects + landscape_objects
    precision_edges = v28.apply_precision_edges(objects)
    selective_edges = apply_selective_architectural_edges(objects)
    validation = v12.validate_geometry(objects)
    triangles = v28.triangle_count(objects)
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images) == 0
    assert all(item["glassBackToStructuralFaceGapM"] <= 1e-6 for item in v14.ENVELOPE_REPORTS)

    target = output / "archive-water-plaza-hero-v31.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(target), export_format="GLB", export_yup=True,
        export_normals=True, export_texcoords=False,
        export_materials="EXPORT", export_apply=True,
    )
    report = {
        "status": "TECHNICAL_PASS_VISUAL_GATE_PENDING",
        "zone": "Archive Water Plaza",
        "revision": 31,
        "qualityTarget": {"grade": "S", "minimumScore": 95},
        "implementationPath": "ATTACHED_MULTI_FLOOR_ROOMS_AND_BOUNDED_ENTRY_VESTIBULES",
        "glb": str(target), "bytes": target.stat().st_size,
        "geometry": {
            "triangles": triangles,
            "vertices": base_geometry["vertices"] + public_geometry["vertices"] + landscape_geometry["vertices"],
            "meshObjects": len(objects),
            "components": base_geometry["components"] + public_geometry["components"] + landscape_geometry["components"],
        },
        "validation": validation, "baseValidation": base_validation,
        "consolidation": base_consolidation,
        "buildingCount": 6, "attachedMultiFloorRoomCount": 18,
        "boundedVestibuleCount": 6, "podiumSideServicePortalCount": 12,
        "lobbyCount": 6, "retailPublicBayCount": 54,
        "treeVariantCount": 12, "treeCount": len(trees),
        "humanCount": len(base_activity) + len(v14.FRONTAGE_ACTIVITY) + len(public_activity) + len(landscape_activity),
        "precisionLandscapeRoomCount": 12,
        "precisionEdgeObjectCount": len(precision_edges) + len(selective_edges),
        "selectiveArchitecturalEdges": selective_edges,
        "envelopeConnection": {
            "status": "PASS",
            "frontGapM": max(item["glassBackToStructuralFaceGapM"] for item in v14.ENVELOPE_REPORTS),
            "sideGapM": max(item["sideGlassBackToStructuralFaceGapM"] for item in v14.ENVELOPE_REPORTS),
            "intentionalFacadeRecessM": .26,
            "boundedRoomRule": "FLOOR_CEILING_REAR_WALL_SIDE_RETURNS",
        },
        "referencePolicy": "Abstract visual direction only; no identifiable design is reproduced.",
        "officeV5Changed": False, "imageDatablocks": len(bpy.data.images),
        "directReferenceCopy": False,
        "originality": "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY",
    }
    (output / "archive-water-plaza-hero-v31-report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps({"status": report["status"], "triangles": triangles,
                      "attachedRooms": 18, "boundedVestibules": 6}))


if __name__ == "__main__":
    main()
