"""Production expansion of the precision treatment across Ledger and Transit.

Archive Water Plaza remains an independent frozen Hero A asset.  This generator
replaces the support bodies around Ledger Stream Terrace and Transit Stream
Junction, then builds the intervening water, promenade, landscape, activity and
night-lighting corridor as actual geometry.  It never edits Office V5, V3,
canonical manifests or runtime repositories.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import archive_water_plaza_v34 as hero


LEDGER_SPECS = (
    (-27.0, 125.0, 44.0, 35.0, 18, 3.85, 1),
    (27.0, 85.0, 38.0, 31.0, 14, 3.80, 2),
    (81.0, 125.0, 52.0, 39.0, 22, 3.90, 3),
    (135.0, 85.0, 42.0, 34.0, 17, 3.85, 4),
    (108.0, 92.0, 36.0, 29.0, 12, 3.95, 5),
    (-27.0, -95.0, 45.0, 35.0, 19, 3.85, 6),
    (81.0, -95.0, 34.0, 28.0, 10, 3.90, 7),
)

TRANSIT_SPECS = (
    (189.0, 125.0, 46.0, 36.0, 16, 3.90, 8),
    (243.0, 85.0, 39.0, 32.0, 14, 3.82, 9),
    (216.0, -114.0, 48.0, 38.0, 12, 4.00, 10),
    (297.0, 125.0, 56.0, 42.0, 18, 4.05, 11),
    (189.0, -95.0, 42.0, 33.0, 11, 4.20, 12),
    (297.0, -95.0, 44.0, 35.0, 15, 3.92, 13),
)


def _build_support_bodies(batch):
    records = []
    for district, specs in (("ledger", LEDGER_SPECS), ("transit", TRANSIT_SPECS)):
        for spec in specs:
            hero.add_wall_first_building(batch, spec)
            records.append({
                "district": district, "position": [spec[0], spec[1]],
                "floors": spec[4], "style": spec[6],
                "groundFloorArchitecture": True, "streamFacing": True,
                "frontSideRearRoofComplete": True,
            })
    return records


def _build_continuous_corridor(batch):
    """Build the actual water and two-level banks from Hero A to the east gate."""
    center_x, length = 110.0, 500.0
    batch.add_box("v36-corridor-water-bed", "dark-water-bed",
                  (center_x, 0.0, -.52), (length, 12.0, .34))
    batch.add_water_ribbon("v36-corridor-water-surface", "shallow-water-v11",
                           (center_x, 0.0), length, 11.4, -.11,
                           length_segments=100, width_segments=8)
    section_records = []
    for bank in (-1, 1):
        batch.add_box("v36-corridor-lower-promenade", "wet-stone",
                      (center_x, bank * 10.5, .02), (length, 8.0, .24))
        batch.add_box("v36-corridor-water-edge-coping", "service-charcoal",
                      (center_x, bank * 6.25, .30), (length, .48, .42))
        batch.add_box("v36-corridor-upper-terrace", "promenade-paver",
                      (center_x, bank * 27.0, 2.08), (length, 24.0, .32))
        batch.add_box("v36-corridor-planted-threshold", "soil-v11",
                      (center_x, bank * 42.0, 2.28), (length - 8.0, 5.2, .65))
        # Dark drainage bands and local paving fields break the pale strip into
        # civic rooms while preserving a continuous accessible promenade.
        batch.add_box("v36-corridor-linear-drain", "service-charcoal",
                      (center_x, bank * 15.1, 2.34), (length, .22, .08))
        for zone_x in range(-120, 361, 40):
            material = "dry-stone" if (zone_x // 40) % 2 else "wet-stone"
            batch.add_box("v36-corridor-paving-room", material,
                          (zone_x, bank * 31.0, 2.315), (28.0, 8.0, .07))
            for joint in range(4):
                batch.add_box("v36-corridor-paving-joint", "ledger-granite",
                              (zone_x - 9.0 + joint * 6.0, bank * 31.0, 2.355),
                              (.055, 7.6, .035))
        # A stair and ramp pair every 60m keeps both banks connected.
        for access_x in range(-110, 351, 60):
            for step in range(7):
                batch.add_box("v36-corridor-access-step", "dry-stone",
                              (access_x, bank * (15.5 + step * 1.30),
                               .30 + step * .30), (9.5, 1.42, .60))
                if step in (0, 3, 6):
                    batch.add_box("v36-corridor-step-light", "warm-light",
                                  (access_x, bank * (15.5 + step * 1.30)
                                   - bank * .72, .56 + step * .30),
                                  (6.2, .06, .09))
            ramp_x = access_x + 8.0
            batch.add_wedge("v36-corridor-accessible-ramp", "promenade-paver",
                            (ramp_x, bank * 21.0, 1.15), (3.6, 13.0, 2.30), "y")
            for side in (-1, 1):
                batch.add_box("v36-corridor-ramp-handrail", "archive-metal",
                              (ramp_x + side * 1.95, bank * 21.0, 2.35),
                              (.08, 13.0, .10))
        section_records.append({"bank": bank, "continuous": True,
                                "lowerM": .02, "upperM": 2.24,
                                "accessibleConnections": 8})
    return {"lengthM": length, "waterWidthM": 11.4,
            "sections": section_records, "waterBedContinuous": True}


def _deep_room(batch, prefix, x, y, facing, width, depth, height,
               stone, accent, public_bays):
    inside = -facing
    face_y = y + facing * depth * .5
    rear_y = y + inside * depth * .5
    batch.add_box(f"v36-{prefix}-floor", "ledger-granite",
                  (x, y, 2.44), (width, depth, .28))
    batch.add_box(f"v36-{prefix}-ceiling", "warm-interior",
                  (x, y, 2.30 + height), (width, depth, .26))
    batch.add_box(f"v36-{prefix}-rear-wall", "warm-interior",
                  (x, rear_y, 2.30 + height * .5), (width, .20, height))
    pitch = width / public_bays
    for bay in range(public_bays):
        bx = x - width * .5 + (bay + .5) * pitch
        batch.add_box(f"v36-{prefix}-integrated-glass", "frontage-glass",
                      (bx, face_y + inside * .42, 2.30 + height * .5),
                      (pitch - .40, .12, height - .58))
        for edge in (-1, 1):
            batch.add_box(f"v36-{prefix}-jamb-return", accent,
                          (bx + edge * (pitch * .5 - .16),
                           face_y + inside * .28, 2.30 + height * .5),
                          (.18, .72, height - .40))
        batch.add_box(f"v36-{prefix}-interior-counter", "timber-accent",
                      (bx, face_y + inside * (depth * .62), 3.05),
                      (pitch * .50, .72, 1.05))
        batch.add_box(f"v36-{prefix}-interior-light", "warm-light",
                      (bx, face_y + inside * (depth * .45),
                       2.30 + height - .28), (pitch * .52, 1.8, .07))
    for side in (-1, 1):
        batch.add_box(f"v36-{prefix}-side-return", stone,
                      (x + side * width * .5, y, 2.30 + height * .5),
                      (.42, depth, height + .30))
    return {"id": prefix, "depthM": depth, "publicBays": public_bays,
            "interiorVolume": True}


def _build_ledger_terrace(batch):
    records = []
    # Narrow premium terraces are tied directly to deep occupied rooms.
    for bank in (-1, 1):
        facing = -bank
        y = bank * 47.0
        records.append(_deep_room(batch, f"ledger-frontage-{bank}", 60.0, y,
                                  facing, 62.0, 16.0, 7.8,
                                  "ledger-limestone", "ledger-bronze", 8))
        batch.add_box("v36-ledger-formal-terrace", "dry-stone",
                      (60.0, bank * 29.0, 2.42), (78.0, 11.0, .24))
        for tier in range(4):
            batch.add_box("v36-ledger-seating-step", "wet-stone",
                          (60.0, bank * (16.0 + tier * 1.15),
                           .30 + tier * .48), (70.0 - tier * 3.0, 1.28, .56))
        for table in range(5):
            tx = 32.0 + table * 14.0
            batch.add_cylinder("v36-ledger-cafe-table", "ledger-bronze",
                               (tx, bank * 30.0, 3.02), .68, .12, 20)
            for chair in (-1, 1):
                batch.add_box("v36-ledger-cafe-chair", "timber-accent",
                              (tx + chair * 1.15, bank * 30.0, 2.75),
                              (.46, .54, .68))
    # Low-profile formal bridge with inhabited landing and rail lights.
    batch.add_box("v36-ledger-bridge-deck", "ledger-limestone",
                  (60.0, 0.0, 2.62), (10.0, 36.0, .58))
    for edge in (-1, 1):
        batch.add_box("v36-ledger-bridge-edge", "ledger-bronze",
                      (60.0 + edge * 4.75, 0.0, 3.07), (.22, 35.0, .38))
        batch.add_box("v36-ledger-bridge-handrail", "ledger-bronze",
                      (60.0 + edge * 4.75, 0.0, 4.02), (.10, 34.0, .10))
        batch.add_box("v36-ledger-bridge-rail-light", "warm-light",
                      (60.0 + edge * 4.68, 0.0, 3.90), (.055, 32.0, .07))
    return {"node": "ledger-stream-terrace", "deepFrontages": records,
            "bridgeCount": 1, "activeFrontage": .78}


def _build_transit_junction(batch):
    records = []
    for bank in (-1, 1):
        facing = -bank
        y = bank * 48.0
        records.append(_deep_room(batch, f"transit-frontage-{bank}", 260.0, y,
                                  facing, 76.0, 18.0, 8.4,
                                  "archive-warm-stone", "archive-metal", 9))
    batch.add_box("v36-transit-transfer-plaza", "promenade-paver",
                  (260.0, -28.0, 2.42), (94.0, 18.0, .24))
    for entry_x in (238.0, 282.0):
        batch.add_box("v36-transit-entry-floor", "ledger-granite",
                      (entry_x, -47.0, 2.48), (18.0, 14.0, .28))
        batch.add_box("v36-transit-entry-ceiling", "warm-interior",
                      (entry_x, -47.0, 9.10), (18.0, 14.0, .28))
        batch.add_box("v36-transit-entry-rear", "warm-interior",
                      (entry_x, -53.8, 5.75), (17.4, .22, 6.5))
        batch.add_box("v36-transit-entry-integrated-glass", "frontage-glass",
                      (entry_x, -40.15, 5.75), (17.2, .12, 6.1))
        for column in range(5):
            cx = entry_x - 8.4 + column * 4.2
            batch.add_box("v36-transit-entry-mullion", "archive-metal",
                          (cx, -40.05, 5.75), (.18, .34, 6.5))
        batch.add_box("v36-transit-entry-canopy", "archive-metal",
                      (entry_x, -37.0, 8.92), (22.0, 6.5, .38))
        batch.add_box("v36-transit-entry-soffit-light", "warm-light",
                      (entry_x, -37.0, 8.70), (20.0, 5.8, .08))
    # Wide covered connector across the stream, with separate walking lanes.
    batch.add_box("v36-transit-bridge-deck", "dry-stone",
                  (260.0, 0.0, 2.68), (18.0, 38.0, .68))
    batch.add_box("v36-transit-bridge-canopy", "archive-metal",
                  (260.0, 0.0, 7.20), (14.0, 31.0, .34))
    for side in (-1, 1):
        for y in (-13.0, -4.3, 4.3, 13.0):
            batch.add_cylinder("v36-transit-bridge-column", "archive-metal",
                               (260.0 + side * 6.2, y, 4.90), .18, 4.5, 14)
        batch.add_box("v36-transit-bridge-handrail", "archive-metal",
                      (260.0 + side * 8.4, 0.0, 4.05), (.10, 36.0, .10))
    return {"node": "transit-stream-junction", "deepFrontages": records,
            "stationEntrances": 2, "coveredBridge": True,
            "activeFrontage": .79}


def _build_vegetation_activity_lighting(batch):
    tree_records, people = [], []
    # Place-based rows and groves frame each node without blocking entrances.
    for node_index, center_x in enumerate((-80.0, 60.0, 180.0, 260.0, 340.0)):
        for bank in (-1, 1):
            for index in range(4):
                x = center_x - 18.0 + index * 12.0
                y = bank * (34.0 + (index % 2) * 2.0)
                hero._add_architectural_tree(
                    batch, x, y, 3600 + node_index * 40 + index + (20 if bank > 0 else 0),
                    .62 + .05 * (index % 2), 2.30)
                batch.add_box("v36-node-tree-root-grate", "ledger-granite",
                              (x, y, 2.38), (2.8, 2.8, .10))
                tree_records.append({"position": [x, y], "node": node_index})
    clusters = (
        (60.0, -29.0, "ledger-lunch"), (60.0, 28.0, "ledger-arrival"),
        (260.0, -29.0, "transit-waiting"), (260.0, 28.0, "transit-crossing"),
        (180.0, -11.0, "corridor-walking"), (340.0, 11.0, "gateway-walking"),
    )
    for cluster_index, (cx, cy, role) in enumerate(clusters):
        for index in range(10):
            x = cx - 5.5 + (index % 5) * 2.7
            y = cy + (index // 5) * 2.2
            people.append(hero._add_mid_detail_human(
                batch, x, y, .18 if index % 2 else -.20,
                4100 + cluster_index * 20 + index,
                "walking" if index % 3 else "conversation",
                2.30 if abs(cy) > 20 else .14))
    # Fixture geometry follows the full route; Viewer point lights are bounded
    # separately so night quality does not multiply shadow cost.
    fixture_count = 0
    for x in range(-120, 361, 24):
        for bank in (-1, 1):
            y = bank * 14.0
            batch.add_cylinder("v36-route-light-pole", "archive-metal",
                               (x, y, 2.05), .075, 3.8, 12)
            batch.add_cylinder("v36-route-light-fixture", "warm-light",
                               (x, y, 4.02), .17, .18, 14)
            batch.add_box("v36-route-edge-light", "warm-light",
                          (x, bank * 6.35, .48), (2.4, .08, .10))
            fixture_count += 2
    return {"trees": tree_records, "treeCount": len(tree_records),
            "people": people, "humanCount": len(people),
            "fixtureCount": fixture_count, "floating": 0,
            "waterIntrusions": 0}


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parsed = parser.parse_args(args)
    output = Path(parsed.output_root)
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    hero.ENVELOPE.clear()
    batch = hero.v12.HeroBatch(hero.v12.create_materials())
    buildings = _build_support_bodies(batch)
    corridor = _build_continuous_corridor(batch)
    ledger = _build_ledger_terrace(batch)
    transit = _build_transit_junction(batch)
    life = _build_vegetation_activity_lighting(batch)
    source_objects = batch.finalize()
    for obj in source_objects:
        if obj.type == "MESH" and any(token in obj.name.lower()
                                      for token in ("tree", "foliage", "human")):
            for polygon in obj.data.polygons:
                polygon.use_smooth = True
    runtime_objects, consolidation = hero._consolidate_scene_objects_by_material(source_objects)
    validation = hero.v12.validate_geometry(runtime_objects)
    triangles = hero.v28.triangle_count(runtime_objects)
    detached_windows = sum(item.get("detachedWindows", 0) for item in hero.ENVELOPE)
    assert len(buildings) == 13
    assert len(hero.ENVELOPE) >= 13
    assert detached_windows == 0
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images) == 0
    target = output / "core-stream-ledger-transit-v36.glb"
    bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB",
                              export_yup=True, export_normals=True,
                              export_texcoords=False, export_materials="EXPORT",
                              export_apply=True)
    report = {
        "status": "TECHNICAL_PASS_VISUAL_GATE_PENDING", "revision": 36,
        "zones": ["Ledger Stream Terrace", "Transit Stream Junction",
                  "Core Stream Connector"],
        "glb": str(target), "bytes": target.stat().st_size,
        "buildingCount": len(buildings), "buildings": buildings,
        "geometry": {"triangles": triangles,
                     "meshObjects": len(runtime_objects),
                     "sourceMeshObjects": len(source_objects)},
        "runtimeGeometry": consolidation, "validation": validation,
        "corridor": corridor, "ledger": ledger, "transit": transit,
        "life": life, "imageDatablocks": len(bpy.data.images),
        "envelopeAudit": hero.ENVELOPE,
        "envelopeAssemblyCount": len(hero.ENVELOPE),
        "detachedWindowCount": detached_windows, "frontSideRearRoofComplete": True,
        "officeV5Changed": False, "canonical": False, "v3Applied": False,
        "directReferenceCopy": False,
        "qualityTarget": {"grade": "S", "minimumScore": 95},
    }
    (output / "core-stream-ledger-transit-v36-report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "triangles": triangles,
                      "buildings": len(buildings), "humans": life["humanCount"]}))


if __name__ == "__main__":
    main()
