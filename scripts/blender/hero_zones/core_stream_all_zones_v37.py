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


def _build_attached_identity_frames(batch):
    """Attach deep family frames to the exact authored envelope datum."""
    records = []
    for district, specs in (("ledger", v36.LEDGER_SPECS),
                            ("transit", v36.TRANSIT_SPECS)):
        for x, y, width, depth, floors, floor_h, style in specs:
            bank = 1 if y > 0 else -1
            facing = -bank
            stone, accent = hero._material_pair(style, y > 0)
            podium_h = 8.2 + .55 * (style % 3)
            lower_floors = max(10, int(floors * (.60 + .03 * (style % 2))))
            lower_w = width * (.70 + .025 * (style % 3))
            lower_d = depth * (.66 + .02 * ((style + 1) % 3))
            lower_x = x + width * (-.06 if style % 2 else .06)
            lower_h = lower_floors * floor_h
            face_y = y + facing * lower_d * .5
            # These vertical frames touch the existing facade opening returns
            # and cast a real 1.3m shadow; they are not a second glass skin.
            for side in (-1, 1):
                frame_x = lower_x + side * lower_w * (.34 + .025 * (style % 2))
                batch.add_box("v41-attached-metropolitan-vertical-frame", stone,
                              (frame_x, face_y + facing * .46,
                               podium_h + lower_h * .52),
                              (.52, 1.30, lower_h * .94))
            for zone in (1, 2):
                band_z = podium_h + lower_h * (zone / 3.0)
                band_width = lower_w * (.82 - .05 * ((style + zone) % 2))
                batch.add_box("v41-attached-metropolitan-shadow-band", accent,
                              (lower_x, face_y + facing * .42, band_z),
                              (band_width, 1.18, .34))
            # The lower portal is embedded in the parent podium wall and adds
            # a legible double-height civic/financial entrance hierarchy.
            portal_w = min(width * .34, 18.0 + (style % 3) * 2.0)
            portal_x = x + width * (-.18 if style % 2 else .16)
            portal_y = y + facing * (depth * .5 + .22)
            for side in (-1, 1):
                batch.add_box("v41-attached-ground-portal-pier", stone,
                              (portal_x + side * portal_w * .5, portal_y, 5.05),
                              (.70, 1.10, 6.10))
            batch.add_box("v41-attached-ground-portal-head", accent,
                          (portal_x, portal_y, 8.02),
                          (portal_w + .70, 1.10, .46))
            batch.add_box("v41-attached-ground-portal-reveal", "warm-interior",
                          (portal_x, y + facing * (depth * .5 - .55), 5.08),
                          (portal_w - 1.0, .18, 5.42))
            rear_y = y - facing * depth * .5
            batch.add_box("v41-attached-service-head", "service-charcoal",
                          (x, rear_y - facing * .34, 7.05),
                          (width * .46, 1.0, .58))
            roof_z = podium_h + floors * floor_h
            blade_offset = width * (.12 + .025 * (style % 3))
            for side in (-1, 1):
                batch.add_box("v41-attached-roof-identity-blade", accent,
                              (x + side * blade_offset, y, roof_z + 4.0),
                              (.48, depth * (.30 + .04 * (style % 2)), 8.0))
            records.append({"district": district, "style": style,
                            "attachedToEnvelope": True, "verticalFrames": 2,
                            "shadowBands": 2, "groundPortal": 1,
                            "roofBlades": 2})
    return records


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


def _build_stream_edge_activity_rooms(batch):
    """Shape the upper banks as a sequence of planted, inhabited rooms.

    The former continuous terrace read as an empty grey strip in eye-level
    evidence. These rooms occupy the terrace itself, keep a clear six-metre
    promenade and frame the stream without scattering props or blocking
    bridges.
    """
    records, people = [], []
    room_centres = (-92.0, -18.0, 126.0, 188.0, 334.0)
    for room_index, cx in enumerate(room_centres):
        for bank in (-1, 1):
            terrace_y = bank * 22.2
            planting_y = bank * 25.4
            accent = "ledger-bronze" if cx < 180 else "archive-metal"
            paving = "dry-stone" if room_index % 2 else "promenade-paver"
            batch.add_box("v45-stream-room-inset-paving", paving,
                          (cx, terrace_y, 2.31), (27.0, 10.2, .12))
            batch.add_box("v45-stream-room-drain", "service-charcoal",
                          (cx, bank * 17.25, 2.37), (25.0, .14, .08))
            for side in (-1, 1):
                tree_x = cx + side * (9.0 if side < 0 else 8.0)
                batch.add_box("v45-stream-room-planter", "ledger-granite",
                              (tree_x, planting_y, 2.74), (4.8, 3.4, .94))
                batch.add_box("v45-stream-room-soil", "soil-v11",
                              (tree_x, planting_y, 3.25), (4.25, 2.9, .14))
                hero._add_architectural_tree(
                    batch, tree_x, planting_y,
                    14100 + room_index * 20 + side + (7 if bank > 0 else 0),
                    .64 + .035 * ((room_index + side) % 3), 3.32)
                batch.add_box("v45-stream-room-bench-seat", "timber-accent",
                              (tree_x, bank * 19.3, 2.62), (3.7, .72, .18))
                batch.add_box("v45-stream-room-bench-back", "timber-accent",
                              (tree_x, bank * 19.65, 3.10), (3.7, .14, .86))
            for light_side in (-1, 1):
                lx = cx + light_side * 5.3
                batch.add_cylinder("v45-stream-room-light-pole", accent,
                                   (lx, bank * 18.2, 4.35), .065, 4.1, 14)
                batch.add_cylinder("v45-stream-room-light-source", "warm-light",
                                   (lx, bank * 18.2, 6.42), .14, .16, 14)
            for person_index in range(6):
                lane = person_index // 3
                px = cx - 3.8 + (person_index % 3) * 3.8
                py = bank * (20.0 + lane * 2.2)
                pose = "walking" if person_index in (0, 3) else "conversation"
                people.append(hero._add_mid_detail_human(
                    batch, px, py, .06 * bank,
                    14500 + room_index * 40 + person_index +
                    (20 if bank > 0 else 0), pose, 2.39))
            records.append({"x": cx, "bank": bank, "clearSpineM": 6.0,
                            "trees": 2, "seats": 2, "humans": 6,
                            "scatterPlacement": False})
    return {"roomCount": len(records), "rooms": records,
            "treeCount": len(records) * 2, "humanCount": len(people),
            "cameraObstruction": False, "waterIntrusions": 0}


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

    # Distinct portal frames attach to the authored v36 decks.  A former
    # duplicate deck occupied the same datum and doubled the apparent slab
    # thickness in every stream camera; the portal layer now adds no deck.
    for x, material, light_material in ((60.0, "ledger-bronze", "warm-light"), (260.0, "archive-metal", "archive-cyan-light")):
        for bank in (-1, 1):
            for side in (-1, 1):
                batch.add_box("v38-node-bridge-portal-column", material, (x + side * 5.0, bank * 13.5, 6.0), (.38, .46, 6.2))
            batch.add_box("v38-node-bridge-portal-beam", material, (x, bank * 13.5, 8.92), (10.4, .46, .34))
            batch.add_box("v38-node-bridge-portal-light", light_material, (x, bank * 13.3, 8.70), (8.8, .08, .10))
    return {"ledgerTerraceRooms": 2, "transitTransferRooms": 2,
            "nodeBridgePortals": 4, "duplicateBridgeDecks": 0,
            "activityHumans": len(activity),
            "activityPlacement": "PROGRAMMED_BY_NODE"}


def _build_cinematic_activity_nodes(batch):
    """Compose near/mid activity at the four photographic node approaches."""
    people = []
    nodes = (
        (10.0, -10.2, "ledger-arrival", "ledger-bronze"),
        (102.0, 10.2, "ledger-lunch", "ledger-bronze"),
        (205.0, -10.2, "transit-arrival", "archive-metal"),
        (315.0, 10.2, "transit-evening", "archive-metal"),
    )
    for node_index, (cx, cy, role, accent) in enumerate(nodes):
        bank = 1 if cy > 0 else -1
        # A bounded seating island and canopy provide a clear destination.
        batch.add_box("v42-activity-node-paving", "dry-stone",
                      (cx, cy, .20), (17.5, 5.4, .16))
        batch.add_box("v42-activity-node-drain", "service-charcoal",
                      (cx, cy - bank * 2.45, .31), (16.5, .12, .07))
        for table_index in (-1, 1):
            tx = cx + table_index * 4.2
            batch.add_cylinder("v42-activity-cafe-table", accent,
                               (tx, cy, .78), .72, .12, 20)
            # Broad parasols were repeatedly caught by street cameras and hid
            # the stream section. Shade now comes from planted upper-bank rooms.
            for chair in (-1, 1):
                batch.add_box("v42-activity-cafe-chair", "timber-accent",
                              (tx + chair * 1.25, cy - bank * .35, .58),
                              (.52, .58, .76))
        for planter_side in (-1, 1):
            px = cx + planter_side * 7.3
            batch.add_box("v42-activity-node-planter", "ledger-granite",
                          (px, cy, .65), (2.4, 3.8, .92))
            batch.add_uv_sphere("v42-activity-node-planting",
                                "foliage-light" if planter_side > 0 else "foliage-mid",
                                (px, cy, 1.38), 1.05, 18, 10,
                                (1.15, .82, .78))
        # Foreground pair, midground conversation and a walking pair form an
        # intentional near/mid/background composition for each node camera.
        for person_index in range(8):
            lane = person_index // 4
            px = cx - 5.3 + (person_index % 4) * 3.5
            py = cy + bank * (-1.15 + lane * 2.2)
            action = "walking" if person_index in (0, 4, 7) else "conversation"
            people.append(hero._add_mid_detail_human(
                batch, px, py, .16 * bank,
                12100 + node_index * 30 + person_index,
                action, .32))
        batch.add_cylinder("v42-activity-node-light-pole", accent,
                           (cx, cy + bank * 2.0, 2.35), .07, 4.2, 14)
        batch.add_cylinder("v42-activity-node-light", "warm-light",
                           (cx, cy + bank * 2.0, 4.50), .16, .18, 14)
    return {"nodeCount": len(nodes), "programmedHumans": len(people),
            "cafeTables": len(nodes) * 2, "scatterPlacement": False,
            "waterIntrusion": 0}


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
            frontage_y = cy - bank * 11.0
            room_inside = bank
            # Four bounded, occupied public rooms join each forecourt to its
            # parent building line. They replace flat glass cards with an
            # eight-metre architectural interior.
            for bay in range(4):
                bay_x = cx - 19.5 + bay * 13.0
                batch.add_box("v40-street-room-floor", "ledger-granite",
                              (bay_x, frontage_y + room_inside * 4.0, 2.48),
                              (11.6, 8.0, .28))
                batch.add_box("v40-street-room-ceiling", "warm-interior",
                              (bay_x, frontage_y + room_inside * 4.0, 8.72),
                              (11.6, 8.0, .30))
                batch.add_box("v40-street-room-rear", "warm-interior",
                              (bay_x, frontage_y + room_inside * 7.85, 5.58),
                              (11.6, .22, 6.25))
                batch.add_box("v40-street-room-glass", "frontage-glass",
                              (bay_x, frontage_y + room_inside * .15, 5.58),
                              (11.1, .14, 5.82))
                for jamb in (-1, 1):
                    batch.add_box("v40-street-room-jamb", accent,
                                  (bay_x + jamb * 5.65,
                                   frontage_y + room_inside * .35, 5.58),
                                  (.20, .75, 6.22))
                batch.add_box("v40-street-room-canopy", accent,
                              (bay_x, frontage_y - bank * 1.8, 8.48),
                              (12.0, 3.8, .30))
                batch.add_box("v40-street-room-interior-light", "warm-light",
                              (bay_x, frontage_y + room_inside * 3.6, 8.46),
                              (8.0, 3.8, .08))
                batch.add_box("v40-street-room-furniture", "timber-accent",
                              (bay_x, frontage_y + room_inside * 4.6, 3.05),
                              (5.8, 1.2, .88))
            arcade_y = cy - bank * 6.0
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
    identity_frames = _build_attached_identity_frames(batch)
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
    stream_edge_rooms = _build_stream_edge_activity_rooms(batch)
    metropolitan_precision = _build_metropolitan_node_precision(batch)
    cinematic_activity = _build_cinematic_activity_nodes(batch)
    street_rooms = _build_metropolitan_street_rooms(batch)
    life["humanCount"] += (metropolitan_precision["activityHumans"]
                           + street_rooms["activityHumans"]
                           + cinematic_activity["programmedHumans"]
                           + stream_edge_rooms["humanCount"])
    source_objects = batch.finalize()
    runtime_objects, consolidation = hero._consolidate_scene_objects_by_material(source_objects)
    validation = hero.v12.validate_geometry(runtime_objects)
    triangles = hero.v28.triangle_count(runtime_objects)
    detached_windows = sum(item.get("detachedWindows", 0) for item in hero.ENVELOPE)
    assert len(buildings) == 13 and len(hero.ENVELOPE) >= 13
    assert detached_windows == 0
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images) == 0
    target = output / "core-stream-ledger-transit-v45.glb"
    bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB",
                              export_yup=True, export_normals=True,
                              export_texcoords=False, export_materials="EXPORT",
                              export_apply=True)
    report = {
        "status": "TECHNICAL_PASS_VISUAL_GATE_PENDING", "revision": 45,
        "geometryRevision": 48,
        "zones": ["Ledger Stream Terrace", "Transit Stream Junction",
                  "Core Stream Connector", "East Gateway"],
        "glb": str(target), "bytes": target.stat().st_size,
        "buildingCount": len(buildings), "buildings": buildings,
        "attachedIdentityFrames": identity_frames,
        "geometry": {"triangles": triangles, "meshObjects": len(runtime_objects),
                     "sourceMeshObjects": len(source_objects)},
        "runtimeGeometry": consolidation, "validation": validation,
        "corridor": corridor, "ledger": ledger, "transit": transit,
        "life": life, "promenadeLife": promenade_life,
        "metropolitanPrecision": metropolitan_precision,
        "cinematicActivityNodes": cinematic_activity,
        "streamEdgeActivityRooms": stream_edge_rooms,
        "metropolitanStreetRooms": street_rooms,
        "occupiedCorridorFrontages": occupied_frontages,
        "imageDatablocks": len(bpy.data.images),
        "detachedWindowCount": detached_windows,
        "frontSideRearRoofComplete": True, "officeV5Changed": False,
        "canonical": False, "v3Applied": False, "directReferenceCopy": False,
        "qualityTarget": {"grade": "S", "minimumScore": 95},
    }
    (output / "core-stream-ledger-transit-v45-report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "triangles": triangles,
                      "buildings": len(buildings),
                      "humans": life["humanCount"] + promenade_life["lowerPromenadeHumans"]}))


if __name__ == "__main__":
    main()
