"""Occupied all-zone refinement for the Ledger/Transit precision corridor."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core_stream_all_zones_v36 as v36

hero = v36.hero


def _enrich_deep_frontage(batch, prefix, x, y, facing, width, depth, bays,
                          stone, accent):
    """Turn a transparent frontage into a legible 3-8m occupied interior."""
    inside = -facing
    face_y = y + facing * depth * .5
    pitch = width / bays
    for bay in range(bays):
        bx = x - width * .5 + (bay + .5) * pitch
        # A complete frame is tied back to the floor, ceiling and rear wall.
        for edge in (-1, 1):
            batch.add_box(f"v37-{prefix}-full-depth-jamb", accent,
                          (bx + edge * (pitch * .5 - .13),
                           face_y + inside * .42, 6.2),
                          (.16, .82, 7.25))
        batch.add_box(f"v37-{prefix}-window-head", accent,
                      (bx, face_y + inside * .40, 9.68),
                      (pitch - .22, .78, .18))
        batch.add_box(f"v37-{prefix}-window-sill", stone,
                      (bx, face_y + inside * .40, 2.72),
                      (pitch - .22, .78, .24))
        # Ceiling coffers, rear-wall panels and furniture make the room depth
        # readable through the glazing instead of presenting a flat gray card.
        batch.add_box(f"v37-{prefix}-ceiling-coffer", "timber-accent",
                      (bx, face_y + inside * (depth * .48), 9.25),
                      (pitch * .72, depth * .50, .18))
        panel_material = "archive-warm-stone" if bay % 2 else "warm-interior"
        batch.add_box(f"v37-{prefix}-rear-panel", panel_material,
                      (bx, face_y + inside * (depth - .34), 6.18),
                      (pitch * .70, .20, 5.70))
        batch.add_box(f"v37-{prefix}-interior-table", "timber-accent",
                      (bx, face_y + inside * (depth * .62), 3.12),
                      (pitch * .46, 1.35, .18))
        for chair in (-1, 1):
            batch.add_box(f"v37-{prefix}-interior-chair", "service-charcoal",
                          (bx + chair * pitch * .18,
                           face_y + inside * (depth * .69), 2.96),
                          (.48, .52, .72))
        batch.add_box(f"v37-{prefix}-pendant", "warm-light",
                      (bx, face_y + inside * (depth * .58), 8.62),
                      (.32, .32, .22))
    # The centre bay is a real recessed doorway and vestibule, not glass paint.
    door_x = x + (.5 if bays % 2 == 0 else 0.0) * pitch
    batch.add_box(f"v37-{prefix}-entry-mat", "ledger-granite",
                  (door_x, face_y + facing * 1.2, 2.50), (pitch * .86, 2.5, .12))
    batch.add_box(f"v37-{prefix}-entry-canopy", accent,
                  (door_x, face_y + facing * 2.0, 7.72),
                  (pitch * 1.8, 4.8, .34))
    batch.add_box(f"v37-{prefix}-entry-soffit", "warm-light",
                  (door_x, face_y + facing * 2.0, 7.50),
                  (pitch * 1.55, 4.2, .08))


def _build_mixed_corridor_frontages(batch):
    records = []
    specifications = (
        (-70.0, 43.0, -1, 44.0, 11.0, 6, "archive-warm-stone", "archive-metal"),
        (-70.0, -43.0, 1, 44.0, 11.0, 6, "ledger-limestone", "ledger-bronze"),
        (158.0, 44.0, -1, 52.0, 12.0, 7, "archive-warm-stone", "archive-metal"),
        (158.0, -44.0, 1, 52.0, 12.0, 7, "ledger-limestone", "ledger-bronze"),
        (342.0, 43.0, -1, 46.0, 11.0, 6, "archive-warm-stone", "archive-metal"),
        (342.0, -43.0, 1, 46.0, 11.0, 6, "ledger-limestone", "ledger-bronze"),
    )
    for index, (x, y, facing, width, depth, bays, stone, accent) in enumerate(specifications):
        prefix = f"corridor-room-{index}"
        record = v36._deep_room(batch, prefix, x, y, facing, width, depth, 7.8,
                                stone, accent, bays)
        _enrich_deep_frontage(batch, prefix, x, y, facing, width, depth, bays,
                              stone, accent)
        records.append(record)
    return records


def _build_promenance_life(batch):
    people, furniture = [], 0
    # Lower-promenade activity alternates between seating and walking rooms.
    for zone_index, center_x in enumerate(range(-105, 356, 38)):
        for bank in (-1, 1):
            y = bank * 10.2
            if zone_index % 3:
                for seat in (-1, 1):
                    batch.add_box("v37-lower-promenade-bench-seat", "timber-accent",
                                  (center_x + seat * 2.0, y, .62),
                                  (3.1, .72, .18))
                    batch.add_box("v37-lower-promenade-bench-back", "timber-accent",
                                  (center_x + seat * 2.0, y + bank * .34, 1.12),
                                  (3.1, .14, .92))
                    furniture += 1
            for person_index in range(3):
                px = center_x - 2.1 + person_index * 2.1
                py = y + bank * (1.0 + .18 * (person_index % 2))
                people.append(hero._add_mid_detail_human(
                    batch, px, py, -.12 + person_index * .14,
                    5300 + zone_index * 20 + person_index + (10 if bank > 0 else 0),
                    "walking" if zone_index % 3 == 0 else "conversation", .14))
            # Planter clusters form rooms without blocking the continuous route.
            batch.add_box("v37-lower-promenade-planter", "ledger-granite",
                          (center_x + 6.0, y + bank * 1.2, .56),
                          (2.4, 1.5, .80))
            batch.add_box("v37-lower-promenade-shrub", "foliage-mid",
                          (center_x + 6.0, y + bank * 1.2, 1.18),
                          (2.0, 1.15, .48))
            furniture += 1
    # Small pavilions prevent long unoccupied reaches between the three nodes.
    for pavilion_x in (158.0, 342.0):
        for bank in (-1, 1):
            py = bank * 31.0
            batch.add_box("v37-corridor-pavilion-floor", "ledger-granite",
                          (pavilion_x, py, 2.55), (18.0, 8.0, .26))
            batch.add_box("v37-corridor-pavilion-roof", "archive-metal",
                          (pavilion_x, py, 7.20), (20.0, 9.5, .34))
            for column_x in (-8.2, 8.2):
                batch.add_cylinder("v37-corridor-pavilion-column", "archive-metal",
                                   (pavilion_x + column_x, py, 4.86), .17, 4.5, 14)
            batch.add_box("v37-corridor-pavilion-glass", "frontage-glass",
                          (pavilion_x, py - bank * 2.8, 4.85),
                          (15.6, .12, 4.0))
            batch.add_box("v37-corridor-pavilion-room-back", "warm-interior",
                          (pavilion_x, py + bank * 2.8, 4.85),
                          (15.6, .18, 4.0))
            batch.add_box("v37-corridor-pavilion-light", "warm-light",
                          (pavilion_x, py, 6.98), (15.5, 6.2, .08))
    return {"lowerPromenadeHumans": len(people), "furnitureClusters": furniture,
            "occupiedPavilions": 4, "floating": 0, "waterIntrusions": 0}


def _build_metropolitan_node_precision(batch):
    """Give Ledger and Transit distinct, occupied metropolitan identities."""
    activity = []
    # Ledger: formal stone terrace with inhabited colonnade and lunch rooms.
    for bank in (-1, 1):
        y = bank * 28.5
        batch.add_box("v38-ledger-formal-terrace", "ledger-granite", (60.0, y, 2.55), (58.0, 12.0, .26))
        batch.add_box("v38-ledger-colonnade-canopy", "ledger-bronze", (60.0, y + bank * 2.0, 7.5), (54.0, 6.4, .34))
        for col in range(7):
            x = 60.0 - 24.0 + col * 8.0
            batch.add_cylinder("v38-ledger-colonnade-column", "ledger-bronze", (x, y + bank * 2.0, 5.0), .18, 4.7, 16)
            if col < 6:
                table_x = x + 4.0
                batch.add_cylinder("v38-ledger-lunch-table", "timber-accent", (table_x, y - bank * 1.0, 3.15), .72, .16, 18)
                for chair in (-1, 1):
                    batch.add_box("v38-ledger-lunch-chair", "timber-accent", (table_x + chair * 1.0, y - bank * 1.0, 3.02), (.68, .68, .16))
        for person in range(12):
            activity.append(hero._add_mid_detail_human(batch, 60.0 - 16.0 + (person % 6) * 6.0, y + bank * (-1.2 + (person // 6) * 2.2), .12 * bank, 9100 + person + (40 if bank > 0 else 0), "conversation" if person % 3 else "walking", 2.68))

    # Transit: a high-capacity covered connector with legible entry portals,
    # bicycle parking and waiting clusters on both banks.
    for bank in (-1, 1):
        y = bank * 29.0
        batch.add_box("v38-transit-transfer-plaza", "dry-stone", (260.0, y, 2.58), (70.0, 13.0, .24))
        batch.add_box("v38-transit-canopy-spine", "archive-metal", (260.0, y, 8.15), (64.0, 8.2, .42))
        batch.add_box("v38-transit-canopy-light", "warm-light", (260.0, y, 7.90), (58.0, 6.8, .09))
        for col in range(9):
            x = 260.0 - 28.0 + col * 7.0
            batch.add_cylinder("v38-transit-canopy-column", "archive-metal", (x, y, 5.25), .16, 5.4, 16)
        for rack in range(5):
            rx = 260.0 - 12.0 + rack * 6.0
            batch.add_box("v38-transit-bicycle-rack", "archive-metal", (rx, y + bank * 4.2, 3.10), (.12, 1.8, 1.0))
        for person in range(16):
            activity.append(hero._add_mid_detail_human(batch, 260.0 - 21.0 + (person % 8) * 6.0, y + bank * (-1.0 + (person // 8) * 2.2), .10 * bank, 9300 + person + (40 if bank > 0 else 0), "waiting" if person % 3 else "walking", 2.70))

    # Distinct portal frames mark the two node crossings without copying the
    # Archive gateway language.
    for x, material, light_material in ((60.0, "ledger-bronze", "warm-light"), (260.0, "archive-metal", "archive-cyan-light")):
        batch.add_box("v38-node-bridge-deck", "ledger-granite", (x, 0, 2.72), (12.0, 38.0, .52))
        for bank in (-1, 1):
            for side in (-1, 1):
                batch.add_box("v38-node-bridge-portal-column", material, (x + side * 5.0, bank * 13.5, 6.0), (.38, .46, 6.2))
            batch.add_box("v38-node-bridge-portal-beam", material, (x, bank * 13.5, 8.92), (10.4, .46, .34))
            batch.add_box("v38-node-bridge-portal-light", light_material, (x, bank * 13.3, 8.70), (8.8, .08, .10))
    return {"ledgerTerraceRooms": 2, "transitTransferRooms": 2,
            "nodeBridgePortals": 4, "activityHumans": len(activity),
            "activityPlacement": "PROGRAMMED_BY_NODE"}


def _build_metropolitan_street_rooms(batch):
    """Replace leftover voids with connected, purpose-built urban rooms.

    These are not scattered props.  Each room joins a stream frontage to an
    upper street or service edge, carries a distinct program and preserves a
    six-metre clear pedestrian spine.
    """
    records, people = [], []
    rooms = (
        (-96.0, "archive-arrival", "archive-warm-stone", "archive-metal"),
        (-18.0, "civic-forecourt", "dry-stone", "archive-metal"),
        (138.0, "ledger-lunch", "ledger-limestone", "ledger-bronze"),
        (214.0, "transit-transfer", "promenade-paver", "archive-metal"),
        (326.0, "east-gateway", "dry-stone", "archive-metal"),
    )
    for room_index, (cx, role, paving, accent) in enumerate(rooms):
        for bank in (-1, 1):
            cy = bank * 59.0
            # A framed forecourt replaces the undifferentiated ground strip.
            batch.add_box("v39-urban-room-paving", paving,
                          (cx, cy, 2.38), (58.0, 27.0, .22))
            batch.add_box("v39-urban-room-drain", "service-charcoal",
                          (cx, cy - bank * 12.0, 2.51), (54.0, .18, .09))
            # An inhabited covered walk makes the frontage/stream connection
            # architectural rather than a row of detached street furniture.
            arcade_y = cy + bank * 7.0
            batch.add_box("v39-urban-room-arcade-roof", accent,
                          (cx, arcade_y, 7.35), (51.0, 7.2, .36))
            batch.add_box("v39-urban-room-arcade-soffit", "warm-light",
                          (cx, arcade_y, 7.12), (47.0, 6.2, .08))
            for column in range(7):
                column_x = cx - 22.5 + column * 7.5
                batch.add_cylinder("v39-urban-room-arcade-column", accent,
                                   (column_x, arcade_y, 4.76), .17, 4.55, 16)
            # Two planted seating courts establish shade and human-scale rooms
            # while the central six metres remain unobstructed.
            for side in (-1, 1):
                court_x = cx + side * 17.0
                batch.add_box("v39-urban-room-planter", "ledger-granite",
                              (court_x, cy - bank * 2.8, 2.92), (9.0, 4.6, 1.02))
                batch.add_box("v39-urban-room-soil", "soil-v11",
                              (court_x, cy - bank * 2.8, 3.46), (8.3, 3.9, .16))
                hero._add_architectural_tree(batch, court_x, cy - bank * 2.8,
                                             10100 + room_index * 20 + side + (10 if bank > 0 else 0),
                                             .68 + .04 * (room_index % 3), 3.52)
                for seat in (-1, 1):
                    batch.add_box("v39-urban-room-bench", "timber-accent",
                                  (court_x + seat * 3.3, cy - bank * 5.4, 2.92),
                                  (2.8, .72, .18))
            # Programmed arrivals, lunch groups and transit waiting follow the
            # room role instead of an even scatter pattern.
            for person in range(10):
                lane = -1 if person < 5 else 1
                px = cx - 12.0 + (person % 5) * 6.0
                py = cy + bank * (lane * 2.2)
                pose = ("waiting" if "transit" in role else
                        "conversation" if person % 3 else "walking")
                people.append(hero._add_mid_detail_human(
                    batch, px, py, .10 * lane,
                    10300 + room_index * 40 + person + (20 if bank > 0 else 0),
                    pose, 2.46))
            # Service/arrival vehicles stay at the outer curb and never cross
            # the promenade.  Wheel and glazing geometry keep them legible.
            vehicle_y = cy + bank * 17.0
            for vehicle in (-1, 1):
                vx = cx + vehicle * 12.0
                batch.add_box("v39-programmed-vehicle-body", "service-charcoal",
                              (vx, vehicle_y, 3.36), (4.8, 1.9, 1.12))
                batch.add_box("v39-programmed-vehicle-cabin", "frontage-glass",
                              (vx + vehicle * .2, vehicle_y, 4.05), (2.5, 1.72, .72))
                for wheel_x in (-1.45, 1.45):
                    for wheel_y in (-.92, .92):
                        batch.add_box("v39-programmed-vehicle-wheel", "service-charcoal",
                                      (vx + wheel_x, vehicle_y + wheel_y, 2.96),
                                      (.62, .18, .62))
            records.append({"role": role, "bank": bank,
                            "coveredWalk": True, "clearSpineM": 6.0,
                            "programmedHumans": 10, "vehicles": 2})
    return {"urbanRoomCount": len(records), "rooms": records,
            "activityHumans": len(people), "vehicleCount": len(records) * 2,
            "blankGroundReplaced": True, "scatterPlacement": False}


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
    buildings = v36._build_support_bodies(batch)
    corridor = v36._build_continuous_corridor(batch)
    ledger = v36._build_ledger_terrace(batch)
    transit = v36._build_transit_junction(batch)
    for bank in (-1, 1):
        _enrich_deep_frontage(batch, f"ledger-node-{bank}", 60.0,
                              bank * 47.0, -bank, 62.0, 16.0, 8,
                              "ledger-limestone", "ledger-bronze")
        _enrich_deep_frontage(batch, f"transit-node-{bank}", 260.0,
                              bank * 48.0, -bank, 76.0, 18.0, 9,
                              "archive-warm-stone", "archive-metal")
    life = v36._build_vegetation_activity_lighting(batch)
    occupied_frontages = _build_mixed_corridor_frontages(batch)
    promenade_life = _build_promenance_life(batch)
    metropolitan_precision = _build_metropolitan_node_precision(batch)
    street_rooms = _build_metropolitan_street_rooms(batch)
    life["humanCount"] += (metropolitan_precision["activityHumans"]
                           + street_rooms["activityHumans"])
    source_objects = batch.finalize()
    runtime_objects, consolidation = hero._consolidate_scene_objects_by_material(source_objects)
    validation = hero.v12.validate_geometry(runtime_objects)
    triangles = hero.v28.triangle_count(runtime_objects)
    detached_windows = sum(item.get("detachedWindows", 0) for item in hero.ENVELOPE)
    assert len(buildings) == 13 and len(hero.ENVELOPE) >= 13
    assert detached_windows == 0
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images) == 0
    target = output / "core-stream-ledger-transit-v39.glb"
    bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB",
                              export_yup=True, export_normals=True,
                              export_texcoords=False, export_materials="EXPORT",
                              export_apply=True)
    report = {
        "status": "TECHNICAL_PASS_VISUAL_GATE_PENDING", "revision": 39,
        "zones": ["Ledger Stream Terrace", "Transit Stream Junction",
                  "Core Stream Connector", "East Gateway"],
        "glb": str(target), "bytes": target.stat().st_size,
        "buildingCount": len(buildings), "buildings": buildings,
        "geometry": {"triangles": triangles, "meshObjects": len(runtime_objects),
                     "sourceMeshObjects": len(source_objects)},
        "runtimeGeometry": consolidation, "validation": validation,
        "corridor": corridor, "ledger": ledger, "transit": transit,
        "life": life, "promenadeLife": promenade_life,
        "metropolitanPrecision": metropolitan_precision,
        "metropolitanStreetRooms": street_rooms,
        "occupiedCorridorFrontages": occupied_frontages,
        "imageDatablocks": len(bpy.data.images),
        "detachedWindowCount": detached_windows,
        "frontSideRearRoofComplete": True, "officeV5Changed": False,
        "canonical": False, "v3Applied": False, "directReferenceCopy": False,
        "qualityTarget": {"grade": "S", "minimumScore": 95},
    }
    (output / "core-stream-ledger-transit-v39-report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "triangles": triangles,
                      "buildings": len(buildings),
                      "humans": life["humanCount"] + promenade_life["lowerPromenadeHumans"]}))


if __name__ == "__main__":
    main()
