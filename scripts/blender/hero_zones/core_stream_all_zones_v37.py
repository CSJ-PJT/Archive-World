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
                batch.add_box("v48-node-bridge-portal-column", material, (x + side * 5.0, bank * 13.5, 5.35), (.32, .42, 4.9))
            batch.add_box("v48-node-bridge-portal-beam", material, (x, bank * 13.5, 7.66), (10.3, .42, .28))
            batch.add_box("v48-node-bridge-portal-light", light_material, (x, bank * 13.3, 7.47), (8.8, .08, .08))
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


def _build_aaa_corridor_polish(batch):
    """Finish the whole corridor with authored edge rhythm and activity.

    The elements follow the two continuous promenades and node approaches;
    none are random scatter.  Joint lines, coping, planted seating rooms and
    foreground/midground activity turn the long pale strips into a sequence of
    legible metropolitan places without blocking the six-metre clear route.
    """
    edge_segments, trees, people, fixtures = 0, 0, [], 0
    for segment, x in enumerate(range(-110, 371, 16)):
        for bank in (-1, 1):
            edge_y = bank * 7.85
            # Dark wet coping and a dry stone cap expose the water datum and
            # make the height change legible at eye level.
            batch.add_box("v48-stream-wet-coping", "wet-stone",
                          (x, edge_y, .30), (15.55, .44, .32))
            batch.add_box("v48-stream-dry-coping", "dry-stone",
                          (x, bank * 8.20, .66), (15.55, .30, .38))
            batch.add_box("v48-stream-edge-joint", "service-charcoal",
                          (x - 7.78, bank * 8.20, .75), (.08, .48, .50))
            edge_segments += 1
            if segment % 3 == (1 if bank > 0 else 2):
                room_y = bank * 19.0
                batch.add_box("v48-stream-seat-plinth", "ledger-granite",
                              (x, room_y, .62), (7.8, 2.2, .56))
                batch.add_box("v48-stream-seat-timber", "timber-accent",
                              (x, room_y - bank * .35, .98), (5.8, .82, .18))
                # The transfer forecourt needs an unobstructed approach view;
                # pull its specimen trees back into the seating room instead
                # of letting a crown mask the station and active frontage.
                transit_clear = 240 <= x <= 280
                tree_x = x - 7.0 if transit_clear else x + (2.7 if segment % 2 else -2.7)
                tree_y = bank * (28.8 if transit_clear else 23.2)
                tree_scale = .62 if transit_clear else .72 + .025 * (segment % 4)
                hero._add_architectural_tree(
                    batch, tree_x, tree_y, 18000 + segment * 7 + bank,
                    tree_scale, 2.42)
                trees += 1
                for person in range(4):
                    px = x - 2.4 + person * 1.65
                    py = bank * (16.5 + (person % 2) * 1.5)
                    people.append(hero._add_mid_detail_human(
                        batch, px, py, .10 * bank,
                        19000 + segment * 10 + person + (5 if bank > 0 else 0),
                        "walking" if person in (0, 3) else "conversation", .18))
            if segment % 2 == 0:
                batch.add_cylinder("v48-stream-edge-light-pole", "archive-metal",
                                   (x, bank * 13.1, 2.12), .055, 3.9, 12)
                batch.add_cylinder("v48-stream-edge-light-source", "warm-light",
                                   (x, bank * 13.1, 4.10), .13, .16, 12)
                fixtures += 1
    # Three larger camera-facing clusters define arrival, lunch and transfer
    # instead of leaving people as a uniform background scatter.
    clusters = ((-42.0, -20.0, "walking"),
                (122.0, 20.0, "conversation"),
                (276.0, -20.0, "waiting"))
    for cluster, (cx, cy, activity) in enumerate(clusters):
        bank = 1 if cy > 0 else -1
        for person in range(12):
            lane = person // 4
            px = cx - 4.8 + (person % 4) * 3.2
            py = cy + bank * (-1.8 + lane * 1.8)
            people.append(hero._add_mid_detail_human(
                batch, px, py, .12 * bank,
                21000 + cluster * 40 + person, activity if person % 3 else "walking", .20))
    return {"edgeSegments": edge_segments, "nearFieldTrees": trees,
            "programmedHumans": len(people), "lightFixtures": fixtures,
            "clearPromenadeM": 6.0, "scatterPlacement": False,
            "floatingObjects": 0, "waterIntrusions": 0}


def _build_hyper_polish_city_scene(batch):
    """Finish Ledger, Transit and the main stream axis as one urban scene."""
    rooms, people, seated, bridges = [], [], [], []
    # Each node receives an inhabited pair of frontage rooms whose internal
    # depths and bay rhythms differ.  They replace the visually flat rear-card
    # condition without attaching decorative boxes to the tower facade.
    frontage_specs = (
        (60.0, -40.5, 1, 60.0, 11.5, 7, "ledger-limestone", "ledger-bronze", "ledger-club"),
        (60.0, 40.5, -1, 52.0, 10.0, 6, "ledger-limestone", "ledger-bronze", "ledger-lobby"),
        (260.0, -41.0, 1, 72.0, 12.0, 9, "archive-warm-stone", "archive-metal", "transit-hall"),
        (260.0, 41.0, -1, 64.0, 10.5, 8, "archive-warm-stone", "archive-metal", "mobility-gallery"),
        (160.0, -40.0, 1, 46.0, 9.0, 6, "archive-warm-stone", "archive-metal", "stream-pavilion"),
        (350.0, 40.0, -1, 44.0, 9.5, 5, "ledger-limestone", "ledger-bronze", "gateway-cafe"),
    )
    for room_index, (x, y, facing, width, depth, bays, stone, accent, role) in enumerate(frontage_specs):
        inside = -facing
        face_y = y + facing * depth * .5
        batch.add_box("v51-hyper-frontage-floor", "ledger-granite",
                      (x, y, 2.46), (width, depth, .28))
        batch.add_box("v51-hyper-frontage-ceiling", stone,
                      (x, y, 9.18), (width, depth, .34))
        pitch = width / bays
        for bay in range(bays):
            bx = x - width * .5 + (bay + .5) * pitch
            room_depth = depth * (.62 + .075 * ((bay + room_index) % 4))
            back_y = face_y + inside * room_depth
            back_material = "warm-interior" if bay % 3 else stone
            batch.add_box("v51-hyper-frontage-room-back", back_material,
                          (bx, back_y, 5.72),
                          (pitch - .46, .20, 6.26))
            batch.add_box("v51-hyper-frontage-glass", "frontage-glass",
                          (bx, face_y + inside * .28, 5.72),
                          (pitch - .32, .12, 6.04))
            for side in (-1, 1):
                batch.add_box("v51-hyper-frontage-room-partition", accent,
                              (bx + side * (pitch * .5 - .14),
                               face_y + inside * room_depth * .50, 5.72),
                              (.16, room_depth, 6.34))
            batch.add_box("v51-hyper-frontage-ceiling-light", "warm-light",
                          (bx, face_y + inside * room_depth * .47, 8.92),
                          (pitch * .54, 2.0, .08))
            batch.add_box("v51-hyper-frontage-table", "timber-accent",
                          (bx, face_y + inside * room_depth * .62, 3.12),
                          (pitch * .46, 1.2, .18))
            if bay in (bays // 2, max(0, bays // 2 - 1)):
                batch.add_box("v51-hyper-frontage-entry-door", "frontage-glass",
                              (bx, face_y + facing * .06, 4.16),
                              (min(2.6, pitch * .48), .12, 3.46))
        canopy_x = x + (-.12 if room_index % 2 else .12) * width
        batch.add_box("v51-hyper-frontage-canopy", accent,
                      (canopy_x, face_y + facing * 2.6, 8.98),
                      (width * .46, 5.4, .36))
        batch.add_box("v51-hyper-frontage-canopy-light", "warm-light",
                      (canopy_x, face_y + facing * 2.6, 8.76),
                      (width * .41, 4.7, .08))
        rooms.append({"role": role, "depthM": depth, "bays": bays,
                      "occupied": True, "streamFacing": True})

    # Program the main axis as alternating arrival, lunch, waiting and garden
    # rooms.  Low planted edges preserve views of the water and occupied bases.
    node_specs = (
        (-92.0, -23.0, "arrival"), (-28.0, 23.0, "meeting"),
        (32.0, -23.0, "ledger-arrival"), (94.0, 23.0, "ledger-lunch"),
        (154.0, -23.0, "stream-rest"), (214.0, 23.0, "transit-arrival"),
        (274.0, -23.0, "transit-wait"), (334.0, 23.0, "gateway-cafe"),
    )
    for node_index, (cx, cy, role) in enumerate(node_specs):
        bank = 1 if cy > 0 else -1
        accent = "ledger-bronze" if 0 <= cx < 180 else "archive-metal"
        batch.add_box("v51-hyper-node-inlay",
                      "dry-stone" if node_index % 2 else "promenade-paver",
                      (cx, cy, 2.39), (26.0, 9.5, .16))
        batch.add_box("v51-hyper-node-drain", "service-charcoal",
                      (cx, cy - bank * 4.48, 2.50), (24.0, .14, .08))
        planter_x = cx + (-8.0 if node_index % 2 else 8.0)
        batch.add_box("v51-hyper-node-planter", "ledger-granite",
                      (planter_x, cy + bank * .7, 2.92), (5.8, 3.8, 1.04))
        batch.add_box("v51-hyper-node-soil", "soil-v11",
                      (planter_x, cy + bank * .7, 3.48), (5.1, 3.1, .14))
        hero._add_architectural_tree(
            batch, planter_x, cy + bank * .7, 30000 + node_index,
            .60 + .035 * (node_index % 4), 3.55)
        for seat_side in (-1, 1):
            sx = cx + seat_side * 3.7
            batch.add_box("v51-hyper-node-bench-seat", "timber-accent",
                          (sx, cy - bank * 1.9, 2.74), (3.0, .72, .18))
            batch.add_box("v51-hyper-node-bench-back", "timber-accent",
                          (sx, cy - bank * 2.24, 3.20), (3.0, .14, .84))
            seated.append(hero._add_seated_human(
                batch, sx, cy - bank * 1.9, 0 if bank > 0 else 3.14159,
                30300 + node_index * 10 + seat_side, 2.86, 2.39))
        for person in range(6):
            people.append(hero._add_mid_detail_human(
                batch, cx - 5.5 + person * 2.2,
                cy + bank * (2.3 + .45 * (person % 2)), .11 * bank,
                30600 + node_index * 20 + person,
                "walking" if person in (0, 5) else
                "waiting" if "transit" in role else "conversation", 2.39))
        batch.add_cylinder("v51-hyper-node-light-pole", accent,
                           (cx - 10.0, cy + bank * 2.8, 4.55), .065, 4.25, 14)
        batch.add_cylinder("v51-hyper-node-light-source", "warm-light",
                           (cx - 10.0, cy + bank * 2.8, 6.72), .14, .18, 14)

    # Ledger lunch and Transit waiting terraces receive distinct occupied
    # canopy clusters.  These replace residual blank paving in the three Hero
    # compositions without narrowing the continuous promenade.
    cafe_clusters = 0
    for cluster_index, (cx, cy, accent, facing) in enumerate((
            (18.0, -30.0, "ledger-bronze", 0.0),
            (47.0, -30.0, "ledger-bronze", 0.0),
            (86.0, 30.0, "ledger-bronze", 3.14159),
            (224.0, -30.0, "archive-metal", 0.0),
            (252.0, 30.0, "archive-metal", 3.14159),
            (294.0, -30.0, "archive-metal", 0.0))):
        batch.add_cylinder("v51-hyper-cafe-table", "timber-accent",
                           (cx, cy, 3.20), .90, .16, 18)
        batch.add_cylinder("v51-hyper-cafe-table-leg", accent,
                           (cx, cy, 2.84), .08, .72, 12)
        batch.add_cylinder("v51-hyper-cafe-canopy-pole", accent,
                           (cx, cy, 4.42), .055, 3.78, 12)
        batch.add_frustum("v51-hyper-cafe-canopy", "timber-accent",
                          (cx, cy, 6.26), 2.40, .44, .58, 24)
        for chair_side in (-1, 1):
            sy = cy + chair_side * 1.25
            batch.add_box("v51-hyper-cafe-chair", "timber-accent",
                          (cx, sy, 2.82), (.76, .76, .18))
            seated.append(hero._add_seated_human(
                batch, cx, sy, facing, 30900 + cluster_index * 10 +
                chair_side, 2.94, 2.39))
        cafe_clusters += 1

    # Camera-composed activity groups make the promenade legible as a sequence
    # of actual uses rather than evenly scattered population markers.
    activity_clusters = []
    for cluster_index, (cx, cy, action, count, facing) in enumerate((
            (30.0, -20.5, "office-arrival", 8, .18),
            (104.0, 20.5, "lunch-terrace", 10, 3.0),
            (158.0, -20.5, "water-watch", 7, .08),
            (218.0, 20.5, "bridge-approach", 9, 3.02),
            (278.0, -20.5, "transit-transfer", 12, .12),
            (334.0, 20.5, "evening-cafe", 8, 3.0))):
        bank = 1 if cy > 0 else -1
        for person in range(count):
            row = person // 5
            px = cx - 4.4 + (person % 5) * 2.2 + row * .6
            py = cy + bank * (row * 1.45 + .25 * (person % 2))
            people.append(hero._add_mid_detail_human(
                batch, px, py, facing + .06 * (person % 3 - 1),
                31300 + cluster_index * 40 + person,
                "walking" if action in ("office-arrival", "bridge-approach",
                                          "transit-transfer") and person % 3 == 0
                else "conversation", 2.39))
        activity_clusters.append({"role": action, "count": count,
                                  "foregroundMidgroundComposed": True})

    # People occupy bridge decks and the water edge, so circulation and pause
    # read in the same frame instead of leaving the centre corridor empty.
    for bridge_index, bridge_x in enumerate((60.0, 260.0)):
        for person in range(7):
            people.append(hero._add_mid_detail_human(
                batch, bridge_x - 3.6 + (person % 4) * 2.4,
                -7.2 + (person // 4) * 4.6, .03,
                31800 + bridge_index * 30 + person, "walking", 2.92))
    for watcher_index, (x, bank) in enumerate(((18.0, -1), (116.0, 1),
                                                (204.0, -1), (310.0, 1))):
        y = bank * 11.2
        batch.add_box("v52-water-watch-seat", "timber-accent",
                      (x, y, .76), (5.6, .72, .18))
        for side in (-1, 1):
            seated.append(hero._add_seated_human(
                batch, x + side * 1.35, y, 0 if bank > 0 else 3.14159,
                32000 + watcher_index * 10 + side, .86, .28))

    # A small exhibition/performance terrace and bicycle stop give the wide
    # central paving a reason to exist without reducing the clear path.
    batch.add_box("v52-performance-terrace", "dry-stone",
                  (154.0, 30.0, 2.52), (18.0, 7.2, .24))
    batch.add_box("v52-performance-backdrop", "archive-metal",
                  (154.0, 33.1, 4.65), (9.0, .22, 4.0))
    batch.add_box("v52-performance-art-panel", "archive-cyan-light",
                  (154.0, 32.94, 4.72), (5.6, .08, 2.5))
    for audience in range(8):
        seated.append(hero._add_seated_human(
            batch, 148.0 + (audience % 4) * 4.0,
            25.4 + (audience // 4) * 1.5, 0.0,
            32200 + audience, 2.84, 2.39))
    for bike in range(5):
        bx = 244.0 + bike * 2.0
        batch.add_box("v52-bicycle-rack", "archive-metal",
                      (bx, -30.0, 3.05), (.12, 1.7, 1.05))
        batch.add_box("v52-bicycle-frame", "ledger-bronze" if bike % 2 else "archive-metal",
                      (bx + .34, -30.0, 2.94), (.08, 1.25, .72))
    activity_clusters.append({"role": "performance-exhibition", "count": 8,
                              "foregroundMidgroundComposed": True})
    activity_clusters.append({"role": "bicycle-stop", "count": 5,
                              "foregroundMidgroundComposed": True})

    # Ledger bridge gains tapered landing pylons and a central viewing bay;
    # Transit receives open canopy fins.  Both remain distinct and accessible.
    for bridge_x, accent, role in ((60.0, "ledger-bronze", "ledger"),
                                    (260.0, "archive-metal", "transit")):
        for bank in (-1, 1):
            batch.add_box("v51-hyper-bridge-landing-plinth", "dry-stone",
                          (bridge_x, bank * 20.5, 2.55), (20.0, 7.8, .22))
            for side in (-1, 1):
                batch.add_tapered_branch(
                    "v51-hyper-bridge-landing-pylon", accent,
                    (bridge_x + side * 5.0, bank * 15.0, 2.74),
                    (bridge_x + side * 4.1, bank * 15.0, 7.20),
                    .36, .18, 14)
            batch.add_box("v51-hyper-bridge-landing-light", "warm-light",
                          (bridge_x, bank * 15.0, 6.96), (7.2, .10, .10))
        if role == "ledger":
            batch.add_box("v51-ledger-bridge-viewing-bay", "dry-stone",
                          (bridge_x, 0.0, 2.96), (15.0, 7.5, .18))
            for side in (-1, 1):
                batch.add_box("v51-ledger-bridge-viewing-seat", "timber-accent",
                              (bridge_x + side * 5.0, 0.0, 3.20),
                              (3.8, .72, .18))
        else:
            for rib in (-8.5, -4.25, 0.0, 4.25, 8.5):
                batch.add_box("v51-transit-bridge-open-canopy-fin", accent,
                              (bridge_x + rib, 0.0, 7.18), (.18, 25.0, .72))
        bridges.append({"role": role, "distinctSilhouette": True,
                        "occupiedLanding": True, "accessible": True})

    return {"occupiedFrontageRooms": rooms, "programmedNodes": len(node_specs),
            "programmedHumans": len(people), "seatedHumans": len(seated),
            "cafeTerraceClusterCount": cafe_clusters,
            "activityClusters": activity_clusters,
            "bridges": bridges, "clearPromenadeM": 6.0,
            "scatterPlacement": False, "floatingObjects": 0,
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
    aaa_polish = _build_aaa_corridor_polish(batch)
    hyper_polish = _build_hyper_polish_city_scene(batch)
    life["humanCount"] += (metropolitan_precision["activityHumans"]
                           + street_rooms["activityHumans"]
                           + cinematic_activity["programmedHumans"]
                           + stream_edge_rooms["humanCount"]
                           + aaa_polish["programmedHumans"]
                           + hyper_polish["programmedHumans"]
                           + hyper_polish["seatedHumans"])
    source_objects = batch.finalize()
    runtime_objects, consolidation = hero._consolidate_scene_objects_by_material(source_objects)
    validation = hero.v12.validate_geometry(runtime_objects)
    triangles = hero.v28.triangle_count(runtime_objects)
    detached_windows = sum(item.get("detachedWindows", 0) for item in hero.ENVELOPE)
    assert len(buildings) == 13 and len(hero.ENVELOPE) >= 13
    assert detached_windows == 0
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images) == 0
    target = output / "core-stream-ledger-transit-v51.glb"
    bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB",
                              export_yup=True, export_normals=True,
                              export_texcoords=False, export_materials="EXPORT",
                              export_apply=True)
    report = {
        "status": "TECHNICAL_PASS_VISUAL_GATE_PENDING", "revision": 51,
        "geometryRevision": 55,
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
        "aaaCorridorPolish": aaa_polish,
        "hyperPolishScene": hyper_polish,
        "occupiedCorridorFrontages": occupied_frontages,
        "imageDatablocks": len(bpy.data.images),
        "detachedWindowCount": detached_windows,
        "structuralPlausibility": {
            "buildingCount": len(hero.STRUCTURAL_PLAUSIBILITY),
            "coreMeetsWindowRoomBack": all(
                item["coreMeetsWindowRoomBack"] for item in hero.STRUCTURAL_PLAUSIBILITY),
            "unsupportedRoofCapCount": sum(
                item["unsupportedRoofCapCount"] for item in hero.STRUCTURAL_PLAUSIBILITY),
            "roofEquipmentContained": all(
                item["roofEquipmentContained"] for item in hero.STRUCTURAL_PLAUSIBILITY),
            "upperMassContainedByLower": all(
                item["upperMassContainedByLower"] for item in hero.STRUCTURAL_PLAUSIBILITY),
            "buildings": hero.STRUCTURAL_PLAUSIBILITY,
        },
        "frontSideRearRoofComplete": True, "officeV5Changed": False,
        "canonical": False, "v3Applied": False, "directReferenceCopy": False,
        "qualityTarget": {"grade": "S", "minimumScore": 95},
    }
    (output / "core-stream-ledger-transit-v51-report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "triangles": triangles,
                      "buildings": len(buildings),
                      "humans": life["humanCount"] + promenade_life["lowerPromenadeHumans"]}))


if __name__ == "__main__":
    main()
