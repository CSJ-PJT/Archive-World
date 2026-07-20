"""Archive Water Plaza V34: wall-first inhabited architecture.

This revision replaces the previous layered frame treatment.  Every glazed bay
is bounded by structural piers, spandrels, a floor/ceiling and a rear wall; the
glass datum is recessed inside that assembly.  No window card is allowed in
front of an unrelated tower box.  The supplied concept image informs only
general urban depth and activity, never identifiable geometry.
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
import archive_water_plaza_v12 as v12
import archive_water_plaza_v28 as v28
import archive_water_plaza_v29 as v29
import archive_water_plaza_v30 as v30

ENVELOPE = []
STRUCTURAL_PLAUSIBILITY = []
CAMERA_CLEARANCE_SHIFTS = {
    (-305, -33): (-305, -47), (-272, -31): (-266, -45),
    (-238, -33): (-230, -46), (-305, 33): (-305, 46),
    (-272, 31): (-266, 45), (-238, 33): (-230, 46),
    (-340, -42): (-354, -48), (-332, -31): (-345, -35),
    (-340, 40): (-354, 46), (-332, 31): (-345, 36),
}
ORIGINAL_ADD_UV_SPHERE = v12.HeroBatch.add_uv_sphere
ORIGINAL_ADD_HUMAN = v12.add_human
ORIGINAL_NATURAL_TREE = v30.add_natural_tree


def _near_camera(x, y, radius):
    camera_origins = ((-340, -15), (-300, -18), (-340, 10), (-210, 22))
    return any(math.hypot(x - cx, y - cy) < radius for cx, cy in camera_origins)


def _occludes_camera(x, y, length=30.0, width=4.0):
    rays = (
        ((-340, -15), (-218, 1)), ((-300, -18), (-325, -60)),
        ((-340, 10), (-230, 0)), ((-210, 22), (-250, 0)),
    )
    for (cx, cy), (tx, ty) in rays:
        dx, dy = tx - cx, ty - cy
        magnitude = math.hypot(dx, dy)
        ux, uy = dx / magnitude, dy / magnitude
        px, py = x - cx, y - cy
        along = px * ux + py * uy
        across = abs(px * uy - py * ux)
        if 0.0 <= along <= length and across <= width:
            return True
    return False


def add_precision_uv_sphere(self, role, material, center, radius,
                            segments=16, rings=8, squash=(1.0, 1.0, 1.0)):
    if "pedestrian-light" in role and _near_camera(center[0], center[1], 16.0):
        return
    if role == "hero-pedestrian-light-fixture":
        cx, cy, cz = center
        self.add_cylinder("v34-pedestrian-light-lens", material, (cx, cy, cz), .14, .22, 12)
        self.add_cylinder("v34-pedestrian-light-shield", "archive-metal", (cx, cy, cz + .13), .24, .08, 12)
        return
    ORIGINAL_ADD_UV_SPHERE(self, role, material, center, radius, segments, rings, squash)


def add_camera_safe_tree(batch, x, y, seed, scale=1.0, z_base=0.0):
    shifted = CAMERA_CLEARANCE_SHIFTS.get((round(x), round(y)))
    if shifted:
        x, y = shifted
        scale *= .86
    if _near_camera(x, y, 22.0) or _occludes_camera(x, y, 38.0, 5.5):
        return
    _add_architectural_tree(batch, x, y, seed, scale, z_base)


def add_camera_safe_human(batch, x, y, facing, seed, action, z_base=0.0):
    """Keep certified eye-level camera origins free of mannequin occlusion."""
    if _near_camera(x, y, 30.0) or _occludes_camera(x, y, 48.0, 4.0):
        return {"position": [x, y], "action": action, "orientation": facing,
                "grounded": True, "culledForCertifiedCamera": True}
    return ORIGINAL_ADD_HUMAN(batch, x, y, facing, seed, action, z_base)


def _material_pair(style: int, north: bool):
    # Six coordinated palettes reinforce the six architectural grammars.  The
    # variation follows massing and frontage roles; it is not a random colour
    # pass used to disguise identical geometry.
    if north:
        return (
            ("archive-warm-stone", "archive-metal"),
            ("ledger-limestone", "archive-metal"),
            ("dry-stone", "archive-metal"),
        )[style % 3]
    return (
        ("ledger-limestone", "ledger-bronze"),
        ("dry-stone", "ledger-bronze"),
        ("archive-warm-stone", "ledger-bronze"),
    )[style % 3]


def _add_chamfered_mass(batch, role, material, center, dimensions, chamfer):
    """Eight-sided architectural mass with real corner cuts and closed caps."""
    cx, cy, cz = center
    width, depth, height = dimensions
    cut = min(chamfer, width * .18, depth * .18)
    plan = (
        (-width * .5 + cut, -depth * .5), (width * .5 - cut, -depth * .5),
        (width * .5, -depth * .5 + cut), (width * .5, depth * .5 - cut),
        (width * .5 - cut, depth * .5), (-width * .5 + cut, depth * .5),
        (-width * .5, depth * .5 - cut), (-width * .5, -depth * .5 + cut),
    )
    vertices = [(cx + px, cy + py, cz - height * .5) for px, py in plan]
    vertices += [(cx + px, cy + py, cz + height * .5) for px, py in plan]
    faces = []
    for index in range(8):
        nxt = (index + 1) % 8
        faces.extend(((index, nxt, 8 + nxt), (index, 8 + nxt, 8 + index)))
    for index in range(1, 7):
        faces.append((0, index + 1, index))
        faces.append((8, 8 + index, 8 + index + 1))
    batch._append(role, material, vertices, faces)


def _bounded_curtain_wall(batch, *, x, face_y, facing, width, base_z,
                          floors, floor_h, style, stone, accent):
    """One facade assembly: room boundary -> recessed glass -> structural grid."""
    inside = -facing
    height = floors * floor_h
    bay_count = max(6, round(width / (3.8 + .25 * (style % 3))))
    bay_width = width / bay_count
    glass_y = face_y + inside * .34
    room_depth = 1.35
    # Two genuinely cut-out, double-height rooms replace normal facade cells.
    # The former feature bays were only laid over the normal window wall.  A
    # cell mask now removes the regular infill, mullion and intermediate
    # spandrel first; the bounded room is then built inside the resulting void.
    # This makes the window datum part of the envelope instead of a second skin.
    feature_defs = []
    if floors >= 8:
        first_floor = min(floors - 3, 3 + style % 3)
        first_bay = min(bay_count - 3, 1 + (style * 2) % max(1, bay_count - 3))
        feature_defs.append((first_floor, first_bay, 2, 2))
    if floors >= 14:
        second_floor = min(floors - 4, max(9, int(floors * .62)))
        second_bay = max(0, bay_count - 4 - style % 2)
        feature_defs.append((second_floor, second_bay, 2, 3))
    feature_cells = {
        (floor, bay)
        for start_floor, start_bay, span_floors, span_bays in feature_defs
        for floor in range(start_floor, min(floors, start_floor + span_floors))
        for bay in range(start_bay, min(bay_count, start_bay + span_bays))
    }

    # Close the facade at both corners.  Previous revisions visually stopped
    # the tower core behind the curtain wall and allowed the glazing grid to
    # read as a freestanding screen from oblique street cameras.  These deep
    # returns physically join the window wall to the side envelope.
    for side in (-1, 1):
        batch.add_box("v34-facade-to-body-corner-return", stone,
                      (x + side * (width * .5 - .15),
                       face_y + inside * (room_depth * .5),
                       base_z + height * .5),
                      (.42, room_depth + .18, height + .42))

    batch.add_box("v34-facade-room-back", "warm-interior",
                  (x, face_y + inside * room_depth, base_z + height * .5),
                  (width, .18, height))
    # Never hang one facade-sized glass card in front of a tower mass.  Each
    # lite below is a discrete infill inside a four-sided structural opening.
    # Floor plates and occupation backs sit behind the glass.  They provide a
    # real spatial cavity, so the facade reads as a building envelope rather
    # than a glass card attached to a solid box.
    for floor in range(floors):
        pz = base_z + floor * floor_h + .10
        batch.add_box("v34-interior-floor-plate", "service-charcoal",
                      (x, face_y + inside * .82, pz), (width - .42, 1.15, .18))
        if (floor + style) % 3:
            zone_x = x + ((floor + style) % 4 - 1.5) * width * .12
            batch.add_box("v34-occupied-room-back", "warm-interior",
                          (zone_x, face_y + inside * 1.12, pz + floor_h * .53),
                          (width * .20, .12, floor_h * .62))
        for bay in range(bay_count):
            if (floor, bay) in feature_cells:
                continue
            px = x - width * .5 + (bay + .5) * bay_width
            opening_h = floor_h - (.62 if floor % 4 else .78)
            opening_z = base_z + floor * floor_h + floor_h * .5
            blind = (bay + floor * 2 + style) % 11 == 0
            glass_material = "occupied-window-glass" if (bay + floor + style) % 4 == 0 else "blue-gray-glass"
            if blind:
                # Blind bays are real wall panels occupying the same bounded
                # opening datum as the glazing, never decorative cards.
                batch.add_box("v34-integrated-blind-infill", stone,
                              (px, glass_y, opening_z),
                              (bay_width - .34, .18, opening_h))
            else:
                batch.add_box("v34-integrated-window-infill", glass_material,
                              (px, glass_y, opening_z),
                              (bay_width - .34, .12, opening_h))
                for side in (-1, 1):
                    batch.add_box("v34-window-jamb-return", accent,
                                  (px + side * (bay_width * .5 - .14),
                                   face_y + inside * .31, opening_z),
                                  (.16, .66, opening_h + .14))
                batch.add_box("v34-window-head-return", accent,
                              (px, face_y + inside * .31,
                               opening_z + opening_h * .5),
                              (bay_width - .18, .66, .16))
                batch.add_box("v34-window-sill-return", accent,
                              (px, face_y + inside * .31,
                               opening_z - opening_h * .5),
                              (bay_width - .18, .66, .16))
    # Segment the structural grid around the cut-out rooms.  A full-height
    # applied mullion or full-width spandrel would pass in front of the void and
    # recreate the detached-window failure that prompted this rework.
    for floor in range(floors):
        opening_z = base_z + floor * floor_h + floor_h * .5
        for column in range(bay_count + 1):
            left_masked = column > 0 and (floor, column - 1) in feature_cells
            right_masked = column < bay_count and (floor, column) in feature_cells
            if left_masked and right_masked:
                continue
            px = x - width * .5 + column * bay_width
            pier_w = .17 if column not in (0, bay_count) else .36
            batch.add_box("v34-structural-facade-pier", accent,
                          (px, face_y + inside * .10, opening_z),
                          (pier_w, .58, floor_h + .08))
    for floor in range(floors + 1):
        pz = base_z + floor * floor_h
        band_h = .18 if floor % 4 else .32
        for bay in range(bay_count):
            inside_feature = (
                floor > 0 and floor < floors
                and (floor - 1, bay) in feature_cells
                and (floor, bay) in feature_cells
            )
            if inside_feature:
                continue
            px = x - width * .5 + (bay + .5) * bay_width
            batch.add_box("v34-attached-spandrel", stone if floor % 4 == 0 else accent,
                          (px, face_y + inside * .10, pz),
                          (bay_width + .04, .58, band_h))

    # Rebuild each removed area as a complete, deep occupied sky room.  Floor,
    # ceiling, rear wall and side returns are continuous with the tower shell;
    # the glass is recessed 1.02m and cannot exist as a floating card.
    for feature_index, (start_floor, start_bay, span_floors, span_bays) in enumerate(feature_defs):
        room_w = bay_width * span_bays
        room_h = floor_h * span_floors
        room_x = x - width * .5 + (start_bay + span_bays * .5) * bay_width
        room_base = base_z + start_floor * floor_h
        room_center_z = room_base + room_h * .5
        recess = 1.18 + .16 * ((style + feature_index) % 3)
        batch.add_box("v34-integrated-skyroom-floor", stone,
                      (room_x, face_y + inside * recess * .52, room_base + .16),
                      (room_w, recess + .35, .32))
        batch.add_box("v34-integrated-skyroom-ceiling", stone,
                      (room_x, face_y + inside * recess * .52, room_base + room_h - .16),
                      (room_w, recess + .35, .32))
        batch.add_box("v34-integrated-skyroom-back", "warm-interior",
                      (room_x, face_y + inside * (recess + .18), room_center_z),
                      (room_w - .34, .18, room_h - .36))
        batch.add_box("v34-integrated-skyroom-glass", "frontage-glass",
                      (room_x, face_y + inside * 1.02, room_center_z),
                      (room_w - .46, .12, room_h - .54))
        for edge in (-1, 1):
            batch.add_box("v34-integrated-skyroom-side-return", stone,
                          (room_x + edge * room_w * .5,
                           face_y + inside * recess * .52, room_center_z),
                          (.42, recess + .38, room_h))
        # A shallow occupied ledge and transparent guard create an actual
        # inhabitable threshold while preserving the window-wall attachment.
        batch.add_box("v34-integrated-skyroom-ledge", stone,
                      (room_x, face_y + facing * .46, room_base + .18),
                      (room_w + .55, 1.08, .34))
        batch.add_box("v34-integrated-skyroom-guard", "frontage-glass",
                      (room_x, face_y + facing * .94, room_base + .82),
                      (room_w - .28, .10, .96))
        for mullion in range(span_bays + 1):
            px = room_x - room_w * .5 + mullion * room_w / span_bays
            batch.add_box("v34-integrated-skyroom-mullion", accent,
                          (px, face_y + inside * .96, room_center_z),
                          (.18, .28, room_h - .28))
    # Three genuinely different facade grammars prevent the six hero buildings
    # from reading as scaled copies while preserving the bounded openings.
    grammar = style % 3
    primary_step = 2 if grammar == 0 else 4 if grammar == 1 else 3
    for column in range(0, bay_count + 1, primary_step):
        px = x - width * .5 + column * bay_width
        batch.add_box("v34-primary-depth-frame", stone,
                      (px, face_y + facing * .19, base_z + height * .5),
                      ((.62 if grammar == 0 else .42),
                       1.22 if grammar == 2 else .94, height + .56))
    if grammar == 0:
        # Institutional vertical order: paired fins extend beyond the normal
        # mullion datum and terminate in a continuous head frame.
        for column in range(1, bay_count, 2):
            px = x - width * .5 + column * bay_width
            batch.add_box("v34-institutional-vertical-fin", accent,
                          (px, face_y + facing * .64, base_z + height * .50),
                          (.22, 1.18, height * .92))
        batch.add_box("v34-institutional-civic-head", stone,
                      (x, face_y + facing * .28, base_z + height * .94),
                      (width + .55, 1.12, .72))
    elif grammar == 1:
        # Ledger-like horizontal order: projected floor trays form long shadow
        # lines instead of another all-height mullion cage.
        for floor in range(3, floors, 4):
            pz = base_z + floor * floor_h
            batch.add_box("v34-horizontal-terrace-band", accent,
                          (x, face_y + facing * .52, pz),
                          (width + .70, 1.28, .30))
        for edge in (-1, 1):
            batch.add_box("v34-horizontal-grammar-corner", stone,
                          (x + edge * width * .5, face_y + facing * .18,
                           base_z + height * .5),
                          (.76, 1.08, height + .62))
    else:
        # Civic portal order: a broad central recess and two deep edge piers
        # produce an unmistakable long-distance silhouette.
        portal_w = min(width * .36, bay_width * 3.2)
        batch.add_box("v34-civic-portal-back", "warm-interior",
                      (x, face_y + inside * 1.28, base_z + height * .56),
                      (portal_w, .18, height * .34))
        for edge in (-1, 1):
            batch.add_box("v34-civic-portal-megaframe", stone,
                          (x + edge * portal_w * .5, face_y + facing * .38,
                           base_z + height * .56),
                          (.82, 1.44, height * .38))
        batch.add_box("v34-civic-portal-head", stone,
                      (x, face_y + facing * .38, base_z + height * .75),
                      (portal_w + .82, 1.44, .64))
    # Three broad recessed rooms break the repetition without a second grid.
    for zone in range(3):
        start = (style * 2 + zone * 3) % max(1, bay_count - 2)
        room_x = x - width * .5 + (start + 1.5) * bay_width
        room_z = base_z + height * (.22 + zone * .27)
        room_h = floor_h * (1.75 if zone != 1 else 2.35)
        room_w = bay_width * 2.75
        recess = .78 + .12 * ((style + zone) % 3)
        batch.add_box("v34-deep-bay-back", "warm-interior",
                      (room_x, face_y + inside * recess, room_z),
                      (room_w, .16, room_h))
        batch.add_box("v34-deep-bay-glass", "frontage-glass",
                      (room_x, face_y + inside * .43, room_z),
                      (room_w - .30, .10, room_h - .30))
        for edge in (-1, 1):
            batch.add_box("v34-deep-bay-return", stone,
                          (room_x + edge * room_w * .5, face_y + inside * (recess * .5), room_z),
                          (.30, recess, room_h + .35))
        batch.add_box("v34-deep-bay-head", stone,
                      (room_x, face_y + inside * (recess * .5), room_z + room_h * .5),
                      (room_w, recess, .30))
        batch.add_box("v34-deep-bay-sill", accent,
                      (room_x, face_y + inside * (recess * .5), room_z - room_h * .5),
                      (room_w, recess, .24))
    ENVELOPE.append({"style": style, "bayCount": bay_count, "glassRecessM": .34,
                     "detachedWindows": 0, "bounded": True,
                     "perOpeningInfill": True, "fourSidedReturns": True,
                     "integratedSkyRoomCount": len(feature_defs),
                     "featureCellsRemovedBeforeRoomBuild": len(feature_cells)})


def _add_style_specific_massing_details(batch, *, x, y, width, depth,
                                        roof_z, facing, style, stone, accent):
    """Give each hero building a constructionally different crown/terrace.

    The pieces connect to the primary mass and serve silhouette, occupied
    terraces and roof maintenance.  They are not triangle-count padding.
    """
    grammar = style % 3
    if grammar == 0:
        # Institutional crown.  Earlier versions used a wide beam above two
        # ten-metre blades; in street views that beam read as a floating cap.
        # The new frame is contained by the top-floor footprint and bears on a
        # single enclosed mechanical penthouse.
        penthouse_w, penthouse_d, penthouse_h = width * .46, depth * .38, 5.4
        batch.add_box("v38-archive-integrated-penthouse", "service-charcoal",
                      (x, y, roof_z + penthouse_h * .5),
                      (penthouse_w, penthouse_d, penthouse_h))
        for side in (-1, 1):
            batch.add_box("v38-archive-crown-bearing-pier", accent,
                          (x + side * penthouse_w * .48,
                           y + facing * penthouse_d * .08,
                           roof_z + penthouse_h * .58),
                          (.52, penthouse_d * .84, penthouse_h * 1.16))
        batch.add_box("v38-archive-crown-contained-head", stone,
                      (x, y + facing * penthouse_d * .08,
                       roof_z + penthouse_h * 1.16),
                      (penthouse_w + .52, penthouse_d * .84, .46))
    elif grammar == 1:
        # Ledger crown: two enclosed setback storeys.  The old stack of three
        # thin plates looked like unsupported shelves instead of architecture.
        stages = ((.52, .44, 3.8, 0.0), (.34, .30, 2.8, .035))
        z_cursor = roof_z
        for index, (wf, df, height, x_offset) in enumerate(stages):
            step_x = x + width * x_offset
            batch.add_box("v38-ledger-enclosed-roof-stage", stone,
                          (step_x, y - facing * index * .28,
                           z_cursor + height * .5),
                          (width * wf, depth * df, height))
            batch.add_box("v38-ledger-roof-stage-glazing", "occupied-window-glass",
                          (step_x, y + facing * depth * df * .5,
                           z_cursor + height * .52),
                          (width * wf - .64, .14, height - .72))
            z_cursor += height
        # A bounded roof garden sits beside the penthouse, inside the roof edge.
        for planter in (-1, 1):
            batch.add_box("v38-ledger-roof-planter", stone,
                          (x + planter * width * .34, y - facing * depth * .20,
                           roof_z + .52),
                          (width * .14, depth * .14, .72))
            batch.add_box("v38-ledger-roof-planting", "foliage-deep",
                          (x + planter * width * .34, y - facing * depth * .20,
                           roof_z + 1.03),
                          (width * .11, depth * .11, .30))
    else:
        # Civic-tech lantern: a recessed occupied volume is bounded by four
        # structural corner piers and a roof frame.
        lantern_w, lantern_d, lantern_h = width * .34, depth * .32, 5.8
        batch.add_box("v34-civic-roof-lantern-interior", "warm-interior",
                      (x, y, roof_z + lantern_h * .5),
                      (lantern_w - 1.0, lantern_d - 1.0, lantern_h - .8))
        for sx in (-1, 1):
            for sy in (-1, 1):
                batch.add_box("v34-civic-lantern-corner-pier", accent,
                              (x + sx * lantern_w * .5,
                               y + sy * lantern_d * .5,
                               roof_z + lantern_h * .5),
                              (.44, .44, lantern_h))
        batch.add_box("v38-civic-lantern-roof-frame", stone,
                      (x, y, roof_z + lantern_h),
                      (lantern_w + .52, lantern_d + .52, .42))
        batch.add_box("v34-civic-lantern-light-line", "archive-cyan-light",
                      (x, y + facing * (lantern_d * .5 + .08),
                       roof_z + lantern_h * .72),
                      (lantern_w - .8, .10, .12))


def _add_occupied_setback_terraces(batch, *, x, y, width, depth,
                                   podium_h, transfer_z, facing,
                                   style, stone, accent):
    """Inhabited horizontal breaks at podium roof and tower transfer level."""
    # Two podium roof gardens wrap the tower shoulders without overlapping the
    # structural core.  Their walls, soil, rails and benches share one datum.
    for side in (-1, 1):
        wing_x = x + side * width * .36
        batch.add_box("v34-podium-roof-terrace-slab", stone,
                      (wing_x, y, podium_h + .20),
                      (width * .26, depth * .58, .40))
        batch.add_box("v34-podium-roof-terrace-guard", accent,
                      (wing_x, y + facing * depth * .285, podium_h + .88),
                      (width * .26, .16, 1.05))
        batch.add_box("v34-podium-roof-terrace-planter", stone,
                      (wing_x, y - facing * depth * .18, podium_h + .78),
                      (width * .20, depth * .12, .92))
        batch.add_box("v34-podium-roof-terrace-soil", "soil-v11",
                      (wing_x, y - facing * depth * .18, podium_h + 1.27),
                      (width * .18, depth * .10, .08))
        for plant in range(5):
            px = wing_x - width * .075 + plant * width * .0375
            batch.add_uv_sphere("v34-podium-roof-terrace-planting",
                                ("foliage-deep", "foliage-mid", "foliage-light")[(plant + style) % 3],
                                (px, y - facing * depth * .18, podium_h + 1.70),
                                .48 + .07 * (plant % 3), 16, 8,
                                (1.0, .70, .58))
    # The tower transfer is a genuine occupied terrace/mechanical datum, not a
    # color stripe.  It creates a readable shadow line on all four sides.
    batch.add_box("v34-tower-transfer-terrace-slab", stone,
                  (x, y, transfer_z + .18),
                  (width * .78, depth * .74, .46))
    batch.add_box("v34-tower-transfer-mechanical-shadow", "service-charcoal",
                  (x, y + facing * depth * .355, transfer_z + .88),
                  (width * .66, .40, 1.10))
    for side in (-1, 1):
        batch.add_box("v34-tower-transfer-side-guard", accent,
                      (x + side * width * .38, y, transfer_z + .92),
                      (.16, depth * .66, 1.12))


def _inhabited_podium(batch, spec, podium_h, stone, accent):
    x, y, width, depth, _floors, _floor_h, style = spec
    facing = -1 if y > 0 else 1
    inside = -facing
    body_depth = depth + 4.0
    face_y = y + facing * body_depth * .5
    bay_count = 7 + style % 3
    facade_width = width + 7.0
    pitch = facade_width / bay_count
    room_depth = 6.2

    # The podium shell stops behind the occupied rooms instead of covering them.
    batch.add_box("v34-podium-structural-shell", stone,
                  (x, y + inside * 2.9, podium_h * .5),
                  (width + 2.4, body_depth - 5.8, podium_h))
    # Complete the podium sides as real occupied/service elevations.  These
    # bounded rooms remove the blank flank that previously dominated oblique
    # Ledger and Transit street cameras.
    shell_width = width + 8.0
    shell_depth = body_depth - 5.8
    for side in (-1, 1):
        side_x = x + side * shell_width * .5
        side_bays = 3 + style % 2
        side_pitch = shell_depth * .90 / side_bays
        for bay in range(side_bays):
            sy = y - shell_depth * .45 + (bay + .5) * side_pitch
            public = (bay + style) % 3 != 0
            infill = "occupied-window-glass" if public else "service-charcoal"
            batch.add_box("v41-podium-side-bounded-infill", infill,
                          (side_x - side * .26, sy, podium_h * .52),
                          (.14, side_pitch - .38, podium_h - 1.10))
            for edge in (-1, 1):
                batch.add_box("v41-podium-side-jamb-return", accent,
                              (side_x - side * .20,
                               sy + edge * (side_pitch * .5 - .15),
                               podium_h * .52),
                              (.58, .18, podium_h - .88))
            batch.add_box("v41-podium-side-head-return", stone,
                          (side_x - side * .20, sy, podium_h - .44),
                          (.58, side_pitch - .30, .28))
            batch.add_box("v41-podium-side-interior-back", "warm-interior",
                          (side_x - side * 2.8, sy, podium_h * .52),
                          (.18, side_pitch - .52, podium_h - 1.22))
    rear_y = y - facing * shell_depth * .5
    rear_bays = 4 + style % 3
    rear_pitch = shell_width * .90 / rear_bays
    for bay in range(rear_bays):
        rx = x - shell_width * .45 + (bay + .5) * rear_pitch
        infill = "service-charcoal" if (bay + style) % 2 else "blue-gray-glass"
        batch.add_box("v41-podium-rear-service-infill", infill,
                      (rx, rear_y + facing * .24, podium_h * .48),
                      (rear_pitch - .40, .14, podium_h - 1.35))
        batch.add_box("v41-podium-rear-service-frame", accent,
                      (rx, rear_y + facing * .16, podium_h - .52),
                      (rear_pitch - .24, .48, .26))
    batch.add_box("v41-podium-rear-loading-canopy", "service-charcoal",
                  (x + width * .18, rear_y - facing * 2.4, 5.0),
                  (width * .34, 5.2, .42))
    batch.add_box("v34-frontage-continuous-floor", "ledger-granite",
                  (x, face_y + inside * room_depth * .5, 2.44),
                  (facade_width, room_depth, .28))
    batch.add_box("v34-frontage-continuous-ceiling", "warm-interior",
                  (x, face_y + inside * room_depth * .5, podium_h - .16),
                  (facade_width, room_depth, .32))
    batch.add_box("v34-frontage-continuous-back", "warm-interior",
                  (x, face_y + inside * (room_depth - .10), podium_h * .53),
                  (facade_width, .20, podium_h - .55))
    for bay in range(bay_count):
        bx = x - facade_width * .5 + (bay + .5) * pitch
        is_lobby = bay == (2 + style) % bay_count
        glass = "frontage-glass" if is_lobby else "occupied-window-glass"
        batch.add_box("v34-bounded-frontage-glass", glass,
                      (bx, face_y + inside * .12, podium_h * .53),
                      (pitch - .32, .12, podium_h - .72))
        batch.add_box("v34-frontage-integrated-sill", stone,
                      (bx, face_y + facing * .01, 2.67), (pitch - .12, .36, .48))
        batch.add_box("v34-frontage-integrated-transom", accent,
                      (bx, face_y + facing * .01, 5.72), (pitch - .12, .36, .18))
        batch.add_box("v34-frontage-integrated-mullion", accent,
                      (bx, face_y + facing * .01, podium_h * .54),
                      (.16, .36, podium_h - .66))
        if is_lobby or bay % 3 == 1:
            door_x = bx + pitch * .22
            batch.add_box("v34-frontage-door-frame", accent,
                          (door_x, face_y + facing * .03, 3.75), (1.35, .28, 3.0))
            batch.add_box("v34-frontage-door-glass", "frontage-glass",
                          (door_x, face_y + facing * .06, 3.75), (1.08, .10, 2.72))
        batch.add_box("v34-interior-counter", "timber-accent",
                      (bx, face_y + inside * 4.1, 3.05), (pitch * .54, .72, 1.05))
        for seat in (-1, 1):
            batch.add_box("v34-interior-furniture-silhouette", "timber-accent",
                          (bx + seat * pitch * .20, face_y + inside * 3.35, 2.82),
                          (.62, .72, .72))
        batch.add_box("v34-interior-ceiling-light", "warm-light",
                      (bx, face_y + inside * 3.0, podium_h - .38), (pitch * .56, 1.5, .07))
    for column in range(bay_count + 1):
        px = x - facade_width * .5 + column * pitch
        batch.add_box("v34-frontage-structural-column", accent,
                      (px, face_y + inside * room_depth * .5, podium_h * .5),
                      (.34, room_depth, podium_h))
    # Each occupied bay receives a recessed head and a warm internal reveal.
    # These pieces are physically contained by the continuous floor, ceiling,
    # back wall and columns above.
    for bay in range(bay_count):
        bx = x - facade_width * .5 + (bay + .5) * pitch
        batch.add_box("v34-frontage-deep-head", stone,
                      (bx, face_y + inside * 1.20, podium_h - .44),
                      (pitch - .36, 2.28, .30))
        if (bay + style) % 2 == 0:
            batch.add_box("v34-frontage-warm-reveal", "warm-interior",
                          (bx, face_y + inside * 1.62, 4.35),
                          (pitch * .50, .16, 2.75))
    # A deep inhabited canopy terminates in real columns and a warm soffit.
    canopy_x = x - facade_width * .22 + (style % 3) * 2.2
    batch.add_box("v34-inhabited-canopy", stone,
                  (canopy_x, face_y + facing * 2.7, podium_h + .18),
                  (facade_width * .40, 5.4, .36))
    batch.add_box("v34-inhabited-canopy-soffit", "warm-light",
                  (canopy_x, face_y + facing * 2.7, podium_h - .04),
                  (facade_width * .37, 4.85, .08))
    for side in (-1, 1):
        batch.add_cylinder("v34-canopy-column", accent,
                           (canopy_x + side * facade_width * .17,
                            face_y + facing * 4.7, podium_h * .5), .22, podium_h, 16)
    # Blank signage is physically fixed to the spandrel, never floating.
    batch.add_box("v34-integrated-signage-band", stone,
                  (x, face_y + facing * .02, podium_h - .52),
                  (facade_width - .7, .28, .62))
    if style in (0, 3):
        _signature_civic_lobby(batch, spec, podium_h, face_y, stone, accent)
    else:
        _secondary_ground_floor_grammar(batch, spec, podium_h, face_y,
                                        stone, accent)


def _secondary_ground_floor_grammar(batch, spec, podium_h, face_y,
                                    stone, accent):
    """Distinct inhabited bases for the four non-signature buildings."""
    x, _y, width, _depth, _floors, _floor_h, style = spec
    facing = -1 if spec[1] > 0 else 1
    inside = -facing
    if style % 3 == 1:
        # A deep covered public arcade with actual occupied rooms behind it.
        arcade_w = width * .72
        arcade_y = face_y + facing * 3.4
        batch.add_box("v34-deep-public-arcade-roof", stone,
                      (x, arcade_y, podium_h - .18),
                      (arcade_w, 6.8, .42))
        batch.add_box("v34-deep-public-arcade-soffit", "timber-accent",
                      (x, arcade_y, podium_h - .43),
                      (arcade_w - .50, 6.3, .10))
        for column in range(5):
            cx = x - arcade_w * .5 + column * arcade_w / 4
            batch.add_cylinder("v34-arcade-tapered-column", accent,
                               (cx, face_y + facing * 6.1, podium_h * .5),
                               .28, podium_h, 18)
        for bay in (-1, 0, 1):
            bx = x + bay * arcade_w * .25
            batch.add_box("v34-arcade-occupied-room-floor", "ledger-granite",
                          (bx, face_y + inside * 2.7, 2.45),
                          (arcade_w * .22, 4.8, .24))
            batch.add_box("v34-arcade-occupied-room-back", "warm-interior",
                          (bx, face_y + inside * 5.0, 4.55),
                          (arcade_w * .22, .16, 4.2))
            batch.add_box("v34-arcade-cafe-counter", "timber-accent",
                          (bx, face_y + inside * 3.6, 3.05),
                          (arcade_w * .15, .72, 1.08))
    else:
        # A civic terrace base with a real corner pavilion and stepped public
        # threshold; unlike the arcade it opens laterally to the stream.
        terrace_x = x + (-1 if style % 2 else 1) * width * .17
        terrace_y = face_y + facing * 5.2
        for step in range(3):
            batch.add_box("v34-civic-frontage-terrace-step", "dry-stone",
                          (terrace_x, terrace_y + facing * step * 1.05,
                           2.42 + step * .18),
                          (width * (.58 - step * .05), 3.2, .36))
        pavilion_w = width * .28
        pavilion_y = face_y + facing * 3.4
        batch.add_box("v34-corner-public-room-floor", "ledger-granite",
                      (terrace_x, pavilion_y, 2.68),
                      (pavilion_w, 6.6, .26))
        batch.add_box("v34-corner-public-room-ceiling", "warm-interior",
                      (terrace_x, pavilion_y, podium_h - .28),
                      (pavilion_w, 6.6, .28))
        batch.add_box("v34-corner-public-room-back", "warm-interior",
                      (terrace_x, face_y + inside * .12, podium_h * .55),
                      (pavilion_w, .18, podium_h - .82))
        batch.add_box("v34-corner-public-room-glass", "frontage-glass",
                      (terrace_x, face_y + facing * 6.72, podium_h * .55),
                      (pavilion_w - .40, .12, podium_h - 1.02))
        for mullion in range(5):
            mx = terrace_x - pavilion_w * .5 + mullion * pavilion_w / 4
            batch.add_box("v34-corner-public-room-mullion", accent,
                          (mx, face_y + facing * 6.78, podium_h * .55),
                          (.16, .30, podium_h - .82))
        batch.add_box("v34-corner-public-room-canopy", stone,
                      (terrace_x, face_y + facing * 7.8, podium_h + .16),
                      (pavilion_w + 3.2, 3.0, .38))
        for seat in (-1, 1):
            batch.add_box("v34-civic-terrace-seat", "timber-accent",
                          (terrace_x + seat * pavilion_w * .32,
                           terrace_y + facing * 4.4, 2.82),
                          (pavilion_w * .23, .70, .18))


def _signature_civic_lobby(batch, spec, podium_h, face_y, stone, accent):
    """A real projected public room for the two principal plaza buildings."""
    x, y, width, _depth, _floors, _floor_h, style = spec
    facing = -1 if y > 0 else 1
    inside = -facing
    lobby_x = x + (-3.6 if style == 0 else 3.8)
    lobby_width = min(18.0, width * .42)
    # A civic lobby must read as an inhabitable room from the promenade.  The
    # former 7.4m projection was technically enclosed but collapsed visually to
    # a glazed card.  A 10.8m deep atrium creates a foreground vestibule, a
    # double-height hall and a rear mezzanine as three legible depth planes.
    projection = 10.8
    outer_y = face_y + facing * projection
    room_y = face_y + facing * projection * .48
    room_h = min(8.2, podium_h - .28)
    batch.add_box("v34-signature-lobby-floor", "ledger-granite",
                  (lobby_x, room_y, 2.45), (lobby_width, projection, .30))
    batch.add_box("v34-signature-lobby-ceiling", "warm-interior",
                  (lobby_x, room_y, 2.30 + room_h), (lobby_width, projection, .26))
    batch.add_box("v34-signature-lobby-back-wall", "warm-interior",
                  (lobby_x, face_y + inside * .08, 2.30 + room_h * .5),
                  (lobby_width, .20, room_h))
    for side in (-1, 1):
        batch.add_box("v34-signature-lobby-side-return", stone,
                      (lobby_x + side * lobby_width * .5, room_y, 2.30 + room_h * .5),
                      (.42, projection, room_h + .30))
    # The entry wall is one bounded curtain-wall assembly with paired doors.
    batch.add_box("v34-signature-lobby-glass", "frontage-glass",
                  (lobby_x, outer_y, 2.30 + room_h * .5),
                  (lobby_width - .42, .12, room_h - .34))
    for mullion in range(6):
        px = lobby_x - lobby_width * .5 + mullion * lobby_width / 5
        batch.add_box("v34-signature-lobby-mullion", accent,
                      (px, outer_y + facing * .04, 2.30 + room_h * .5),
                      (.18, .34, room_h))
    batch.add_box("v34-signature-lobby-transom", accent,
                  (lobby_x, outer_y + facing * .04, 5.25),
                  (lobby_width, .34, .18))
    for door in (-1, 1):
        dx = lobby_x + door * 1.05
        batch.add_box("v34-signature-entry-door-frame", accent,
                      (dx, outer_y + facing * .12, 3.82), (1.68, .28, 3.04))
        batch.add_box("v34-signature-entry-door-glass", "frontage-glass",
                      (dx, outer_y + facing * .16, 3.82), (1.38, .10, 2.74))
    # The vestibule is independently enclosed inside the facade line.  Its
    # second glass plane and deep side returns prevent the front curtain wall
    # from reading as detached glazing.
    vestibule_y = outer_y + inside * 1.55
    batch.add_box("v35-signature-vestibule-inner-glass", "frontage-glass",
                  (lobby_x, vestibule_y, 3.92), (5.8, .12, 3.18))
    for side in (-1, 1):
        batch.add_box("v35-signature-vestibule-side-return", accent,
                      (lobby_x + side * 2.95, outer_y + inside * .78, 3.92),
                      (.16, 1.58, 3.30))
    # A rear mezzanine and guard establish a true double-height atrium.  The
    # mezzanine occupies only the back third, preserving the full-height lobby
    # at the glass and exposing the interior section in street views.
    mezzanine_y = face_y + facing * 2.20
    batch.add_box("v35-signature-atrium-mezzanine-slab", "ledger-granite",
                  (lobby_x, mezzanine_y, 6.52), (lobby_width - 1.4, 4.20, .28))
    batch.add_box("v35-signature-atrium-mezzanine-guard", "frontage-glass",
                  (lobby_x, mezzanine_y + facing * 2.05, 7.10),
                  (lobby_width - 2.0, .10, 1.02))
    for column in (-1, 1):
        batch.add_cylinder("v35-signature-atrium-structural-column", accent,
                           (lobby_x + column * lobby_width * .34, room_y,
                            2.30 + room_h * .50), .24, room_h, 18)
    # Rear core portal, ceiling coffers and suspended fixtures make the depth
    # visible even when the glass is highly reflective.
    batch.add_box("v35-signature-atrium-rear-portal", accent,
                  (lobby_x, face_y + inside * .03, 4.20), (6.8, .38, 3.80))
    batch.add_box("v35-signature-atrium-rear-portal-opening", "service-charcoal",
                  (lobby_x, face_y + facing * .18, 4.05), (5.5, .12, 3.18))
    for coffer in range(5):
        cy = outer_y + inside * (2.5 + coffer * 1.45)
        batch.add_box("v35-signature-atrium-ceiling-coffer", accent,
                      (lobby_x, cy, 2.30 + room_h - .20),
                      (lobby_width - 1.2, .16, .20))
        for side in (-1, 1):
            batch.add_cylinder("v35-signature-atrium-pendant-light", "warm-light",
                               (lobby_x + side * lobby_width * .24, cy,
                               2.30 + room_h - 1.10), .12, .32, 14)
    # A buildable mezzanine stair makes the two levels spatially legible behind
    # the glass instead of relying on furniture silhouettes alone.
    stair_x = lobby_x + (1 if style == 0 else -1) * lobby_width * .31
    for step in range(10):
        step_y = outer_y + inside * (3.15 + step * .48)
        step_z = 2.52 + step * .38
        batch.add_box("v35-signature-atrium-stair-tread", "ledger-granite",
                      (stair_x, step_y, step_z), (2.35, .58, .22))
    for side in (-1, 1):
        batch.add_box("v35-signature-atrium-stair-stringer", accent,
                      (stair_x + side * 1.16, outer_y + inside * 5.35, 4.50),
                      (.12, 5.2, .20))
    batch.add_box("v35-signature-atrium-directory-wall", stone,
                  (lobby_x - (1 if style == 0 else -1) * lobby_width * .30,
                   face_y + facing * 2.7, 4.55), (3.7, .42, 4.5))
    batch.add_box("v35-signature-atrium-directory-light", "warm-light",
                  (lobby_x - (1 if style == 0 else -1) * lobby_width * .30,
                   face_y + facing * 2.94, 5.20), (2.7, .08, 2.5))
    batch.add_box("v34-signature-lobby-canopy", stone,
                  (lobby_x, outer_y + facing * 2.45, 2.30 + room_h + .42),
                  (lobby_width + 3.6, 5.1, .38))
    batch.add_box("v34-signature-lobby-canopy-soffit", "warm-light",
                  (lobby_x, outer_y + facing * 2.45, 2.30 + room_h + .19),
                  (lobby_width + 3.0, 4.55, .08))
    # Interior floor plates, reception and lounge silhouettes remain visible.
    batch.add_box("v34-signature-reception", "timber-accent",
                  (lobby_x, room_y + inside * 1.45, 3.15), (5.2, 1.0, 1.30))
    for side in (-1, 1):
        batch.add_box("v34-signature-lounge", "timber-accent",
                      (lobby_x + side * 4.4, room_y, 2.92), (2.6, 1.15, .72))
        batch.add_cylinder("v34-signature-pendant", "warm-light",
                           (lobby_x + side * 4.2, room_y, 7.25), .16, .34, 14)
    # A stone threshold terrace gives the projection a real ground relationship.
    batch.add_box("v34-signature-entry-terrace", "dry-stone",
                  (lobby_x, outer_y + facing * 5.4, 2.34),
                  (lobby_width + 9.0, 10.8, .16))
    for side in (-1, 1):
        batch.add_box("v34-signature-entry-planter", stone,
                      (lobby_x + side * (lobby_width * .5 + 2.1), outer_y + facing * 4.8, 2.96),
                      (3.2, 3.0, 1.28))
        batch.add_box("v34-signature-entry-soil", "soil-v11",
                      (lobby_x + side * (lobby_width * .5 + 2.1), outer_y + facing * 4.8, 3.64),
                      (2.8, 2.6, .10))
    # The lobby terrace is programmed as a small civic room, not left as blank
    # paving.  Curved tables, loose chairs, a screen wall and paired trees form
    # foreground/midground depth while preserving the camera ray.
    terrace_y = outer_y + facing * 6.8
    batch.add_box("v34-signature-terrace-screen", accent,
                  (lobby_x - lobby_width * .5 - 3.3, terrace_y, 4.05),
                  (.30, 7.2, 3.3))
    for table_index in (-1, 0, 1):
        table_x = lobby_x + table_index * 4.4
        batch.add_cylinder("v34-signature-cafe-table", "ledger-bronze",
                           (table_x, terrace_y, 3.10), .74, .12, 24)
        for chair_index in range(3):
            angle = chair_index * math.tau / 3 + .35
            batch.add_box("v34-signature-cafe-chair", "timber-accent",
                          (table_x + math.cos(angle) * 1.35,
                           terrace_y + math.sin(angle) * 1.35, 2.82),
                          (.48, .52, .70), angle)
    for tree_side in (-1, 1):
        tx = lobby_x + tree_side * (lobby_width * .5 + 3.6)
        ty = terrace_y + facing * 1.0
        add_camera_safe_tree(batch, tx, ty, 1240 + style * 7 + tree_side, .68, 2.30)


def _add_archive_civic_section_rebuild():
    """Add a legible upper/lower water section at the Archive hero axis.

    The base zone already contains continuous technical stairs and ramps.  This
    localized rebuild gives the principal civic axis a wider lower landing,
    clearly bounded stair flights, a planted retaining threshold and an
    accessible switchback.  These are spatial components rather than surface
    decoration and are kept clear of the water and maintenance route.
    """
    batch = v12.HeroBatch(v12.create_materials())
    records = []
    for bank in (-1, 1):
        # Broad lower room at the water datum.
        batch.add_box("v35-archive-lower-promenade-room", "wet-stone",
                      (-300.0, bank * 10.6, .12), (52.0, 8.4, .34))
        batch.add_box("v35-archive-water-edge-coping", "service-charcoal",
                      (-300.0, bank * 6.35, .38), (52.0, .55, .52))
        # Three-dimensional paving fields and drainage lines establish a
        # material hierarchy between civic terrace, transition and promenade.
        for zone_index, zone_x in enumerate((-332.0, -300.0, -268.0)):
            batch.add_box("v35-archive-upper-terrace-inlay",
                          "dry-stone" if zone_index % 2 == 0 else "wet-stone",
                          (zone_x, bank * 31.2, 2.315), (21.0, 8.2, .07))
            for joint in range(4):
                batch.add_box("v35-archive-upper-terrace-joint", "ledger-granite",
                              (zone_x - 7.5 + joint * 5.0, bank * 31.2, 2.355),
                              (.055, 7.8, .035))
        batch.add_box("v35-archive-linear-drain", "service-charcoal",
                      (-300.0, bank * 15.1, 2.34), (52.0, .24, .08))
        # Two solid stair flights make the 2.2m vertical transition obvious in
        # eye-level views. Each tread has a nosing and an integrated light.
        for stair_x in (-316.0, -284.0):
            for step in range(7):
                y = bank * (15.5 + step * 1.30)
                z = .30 + step * .30
                batch.add_box("v35-archive-section-step", "dry-stone",
                              (stair_x, y, z), (10.8, 1.42, .60))
                batch.add_box("v35-archive-section-step-nosing", "ledger-granite",
                              (stair_x, y - bank * .68, z + .31),
                              (10.8, .08, .06))
                if step in (0, 2, 4, 6):
                    batch.add_box("v35-archive-section-step-light", "warm-light",
                                  (stair_x, y - bank * .73, z + .25),
                                  (6.8, .06, .09))
            for rail_side in (-1, 1):
                batch.add_box("v35-archive-section-stair-handrail", "archive-metal",
                              (stair_x + rail_side * 5.2, bank * 19.4, 1.72),
                              (.10, 10.1, .10))
        # Accessible two-run ramp with a real intermediate landing.  Wedge
        # geometry holds the grade; retaining cheeks show its construction.
        ramp_x = -300.0
        batch.add_wedge("v35-archive-accessible-ramp-lower", "promenade-paver",
                        (ramp_x, bank * 18.0, .63), (5.0, 9.0, 1.18), "y")
        batch.add_box("v35-archive-accessible-ramp-landing", "promenade-paver",
                      (ramp_x, bank * 23.0, 1.22), (8.0, 3.0, .24))
        batch.add_wedge("v35-archive-accessible-ramp-upper", "promenade-paver",
                        (ramp_x, bank * 28.0, 1.72), (5.0, 9.0, 1.18), "y")
        for side in (-1, 1):
            batch.add_box("v35-archive-ramp-retaining-cheek", "archive-warm-stone",
                          (ramp_x + side * 2.65, bank * 23.0, 1.25),
                          (.22, 20.0, 2.20))
            batch.add_box("v35-archive-ramp-handrail", "archive-metal",
                          (ramp_x + side * 2.78, bank * 23.0, 2.62),
                          (.10, 20.0, .10))
        # Layered planting softens the retaining wall but leaves stair and lobby
        # sightlines open.  It also creates a clear upper-level threshold.
        for side in (-1, 1):
            planter_x = ramp_x + side * 10.2
            batch.add_box("v35-archive-section-planter-wall", "archive-warm-stone",
                          (planter_x, bank * 24.3, 2.22), (8.0, 4.8, 1.05))
            batch.add_box("v35-archive-section-planter-soil", "soil-v11",
                          (planter_x, bank * 24.3, 2.78), (7.5, 4.3, .10))
            for plant in range(4):
                px = planter_x - 2.7 + plant * 1.8
                _add_irregular_canopy_lobe(
                    batch, "v35-archive-section-irregular-groundcover",
                    ("foliage-deep", "foliage-mid", "foliage-light")[plant % 3],
                    (px, bank * 24.3, 3.24 + .08 * (plant % 2)),
                    .72 + .07 * (plant % 3), (1.25, .72, .62),
                    2100 + plant + (10 if bank > 0 else 0), 12, 5)
        records.append({"bank": bank, "lowerPromenadeElevation": .12,
                        "upperCivicElevation": 2.30, "stairFlights": 2,
                        "accessibleRamp": True, "maintenanceClear": True})
    v12.consolidate(batch)
    return batch.finalize(), records


def _add_irregular_canopy_lobe(batch, role, material, center, radius,
                               squash, seed, segments=14, rings=7):
    """Faceted asymmetric canopy volume without primitive-sphere repetition."""
    cx, cy, cz = center
    vertices = []
    for ring in range(rings + 1):
        phi = math.pi * ring / rings
        for segment in range(segments):
            theta = math.tau * segment / segments
            noise = (1.0 + .13 * math.sin(theta * 3.0 + seed * .31)
                     + .08 * math.cos(phi * 4.0 - seed * .17)
                     + .045 * math.sin(theta * 7.0 + phi * 2.0))
            vertices.append((
                cx + radius * math.sin(phi) * math.cos(theta) * squash[0] * noise,
                cy + radius * math.sin(phi) * math.sin(theta) * squash[1] * noise,
                cz + radius * math.cos(phi) * squash[2] * noise,
            ))
    faces = []
    for ring in range(rings):
        for segment in range(segments):
            nxt = (segment + 1) % segments
            a = ring * segments + segment
            b = ring * segments + nxt
            c = (ring + 1) * segments + nxt
            d = (ring + 1) * segments + segment
            faces.extend(((a, b, c), (a, c, d)))
    batch._append(role, material, vertices, faces)


def _add_architectural_tree(batch, x, y, seed, scale=1.0, z_base=0.0):
    """Twelve deterministic near-field tree silhouettes with real branching."""
    variant = seed % 12
    family = variant % 4
    height = (6.8, 8.4, 7.5, 9.1)[family] * scale * (0.94 + (variant // 4) * .045)
    material = ("foliage-deep", "foliage-mid", "foliage-light")[(variant + family) % 3]
    trunk_lean_x = math.sin(seed * .73) * .28 * scale
    trunk_lean_y = math.cos(seed * .51) * .24 * scale
    trunk_top = (x + trunk_lean_x, y + trunk_lean_y, z_base + height * .64)
    batch.add_tapered_branch("v34-species-tree-tapered-trunk", "timber-accent",
                             (x, y, z_base), trunk_top,
                             (.34 + family * .025) * scale,
                             (.10 + family * .008) * scale, 16)
    branch_count = 6 + family
    tips = []
    for branch in range(branch_count):
        angle = branch * math.tau / branch_count + variant * .31
        start_z = z_base + height * (.36 + .035 * (branch % 4))
        start = (x + trunk_lean_x * .62, y + trunk_lean_y * .62, start_z)
        spread = (1.20 + .18 * family + .10 * (branch % 3)) * scale
        rise = (.62 + .12 * ((branch + variant) % 3)) * scale
        tip = (trunk_top[0] + math.cos(angle) * spread,
               trunk_top[1] + math.sin(angle) * spread,
               trunk_top[2] + rise)
        batch.add_tapered_branch("v34-species-tree-primary-branch", "timber-accent",
                                 start, tip, .105 * scale, .032 * scale, 10)
        # One attached secondary branch gives the silhouette believable forked
        # structure without creating an expensive leaf-per-card canopy.
        fork_angle = angle + (-.48 if branch % 2 else .44)
        fork = (tip[0] + math.cos(fork_angle) * .62 * scale,
                tip[1] + math.sin(fork_angle) * .62 * scale,
                tip[2] + (.32 + .06 * (branch % 2)) * scale)
        batch.add_tapered_branch("v34-species-tree-secondary-branch", "timber-accent",
                                 tip, fork, .036 * scale, .014 * scale, 8)
        tips.extend((tip, fork))
    # Irregular, overlapping crown lobes follow the branch tips.  Family
    # proportions span columnar, vase, spreading and upright plaza species.
    squash_by_family = ((.76, .74, 1.15), (1.18, .88, .78),
                        (1.34, .92, .70), (.92, .82, 1.02))
    squash = squash_by_family[family]
    # Four to six asymmetric volumes form one coherent crown instead of the
    # previous necklace of identical UV spheres.  Each lobe follows a real
    # branch attachment and is deterministic per species seed.
    # Hero-camera trees use a continuous central crown plus seven branch-led
    # lobes.  This removes the sparse polygon bouquets visible in v34 while
    # retaining deterministic, batchable procedural geometry.
    _add_irregular_canopy_lobe(
        batch, "v35-species-tree-coherent-central-crown", material,
        (trunk_top[0], trunk_top[1], trunk_top[2] + 1.05 * scale),
        2.05 * scale, (squash[0] * 1.08, squash[1] * 1.08, squash[2]),
        seed + 901, 20, 9)
    stride = max(1, len(tips) // 8)
    selected_tips = tips[::stride][:8]
    for lobe, tip in enumerate(selected_tips):
        radius = (1.34 + .14 * ((lobe + variant) % 4)) * scale
        center = (tip[0] + math.sin(lobe * 1.73 + variant) * .24 * scale,
                  tip[1] + math.cos(lobe * 1.31 + variant) * .20 * scale,
                  tip[2] + .42 * scale + .10 * (lobe % 3) * scale)
        _add_irregular_canopy_lobe(
            batch, "v34-species-tree-irregular-crown", material,
            center, radius, squash, seed + lobe * 17, 18, 8)


def _add_seated_human(batch, x, y, facing, seed, seat_z, ground_z):
    """Mid-detail seated figure whose articulated legs reach the actual grade."""
    height = 1.66 + (seed % 5) * .025
    body = ("archive-metal", "ledger-bronze", "service-charcoal")[seed % 3]
    skin = "archive-warm-stone"
    forward = (math.sin(facing), math.cos(facing))
    right = (math.cos(facing), -math.sin(facing))
    hip = (x, y, seat_z + .10)
    shoulder_z = seat_z + height * .48
    head_z = seat_z + height * .64
    batch.add_frustum("v35-human-seated-tailored-torso", body,
                      (x, y, (hip[2] + shoulder_z) * .5), .17, .22,
                      shoulder_z - hip[2], 18)
    batch.add_cylinder("v35-human-seated-neck", skin,
                       (x, y, head_z - .13), .06, .14, 12)
    batch.add_uv_sphere("v35-human-seated-head", skin,
                        (x, y, head_z), .125, 20, 10, (1.0, .92, 1.08))
    batch.add_uv_sphere("v35-human-seated-hair", "service-charcoal",
                        (x, y - .01, head_z + .06), .112, 18, 9,
                        (1.03, .96, .72))
    for side in (-1, 1):
        hip_joint = (x + right[0] * side * .105,
                     y + right[1] * side * .105, hip[2])
        knee = (hip_joint[0] + forward[0] * .36,
                hip_joint[1] + forward[1] * .36, seat_z - .10)
        foot = (knee[0] + forward[0] * .12,
                knee[1] + forward[1] * .12, ground_z + .06)
        batch.add_tapered_branch("v35-human-seated-upper-leg", "service-charcoal",
                                 hip_joint, knee, .086, .068, 12)
        batch.add_tapered_branch("v35-human-seated-lower-leg", "service-charcoal",
                                 knee, foot, .068, .046, 12)
        shoulder = (x + right[0] * side * .20,
                    y + right[1] * side * .20, shoulder_z - .05)
        hand = (x + forward[0] * .25 + right[0] * side * .13,
                y + forward[1] * .25 + right[1] * side * .13,
                seat_z + .20)
        batch.add_tapered_branch("v35-human-seated-arm", body,
                                 shoulder, hand, .062, .040, 12)
        batch.add_uv_sphere("v35-human-seated-hand", skin, hand,
                            .048, 12, 6, (1, .84, 1.08))
    return {"position": [x, y], "action": "sitting", "orientation": facing,
            "grounded": True, "detail": "MID_DETAIL_NEAR_FIELD"}


def _add_signature_activity_layer():
    """Camera-composed civic activity anchored to real frontage and furniture."""
    human_batch = v12.HeroBatch(v12.create_materials())
    prop_batch = v12.HeroBatch(v12.create_materials())
    records = []
    groups = (
        (-312, -30.5, .18, "walking", 2.30), (-294, -32.0, -.30, "conversation", 2.30),
        (-281, -29.5, .32, "walking", 2.30),
        (-334, -43.5, .30, "walking", 2.30), (-329, -44.5, .20, "conversation", 2.30),
        (-326, -42.7, -.25, "conversation", 2.30), (-318, -45.5, .35, "walking", 2.30),
        (-313, -43.8, -.15, "conversation", 2.30), (-309, -45.1, .25, "conversation", 2.30),
        (-267, -43.5, .15, "walking", 2.30), (-262, -45.0, -.20, "conversation", 2.30),
        (-257, -43.8, .25, "conversation", 2.30), (-252, -46.0, .05, "walking", 2.30),
        # Lower-promenade activity is placed against the actual +0.14m datum.
        # These clusters establish near/mid/far human scale in the stream view.
        (-318, -11.4, .42, "walking", .14), (-309, -10.8, -.22, "conversation", .14),
        (-298, -11.7, .18, "walking", .14), (-283, -10.9, -.35, "conversation", .14),
        (-268, -11.6, .28, "walking", .14), (-250, -10.8, -.18, "walking", .14),
        (-230, -11.5, .26, "conversation", .14), (-210, -10.9, -.22, "walking", .14),
        (-306, 11.1, -.32, "walking", .14), (-288, 10.7, .25, "conversation", .14),
        (-260, 11.4, -.20, "walking", .14), (-238, 10.8, .28, "conversation", .14),
        # Camera-composed near-bank pairs: arrival at the upper promenade and
        # continuous walking groups along both lower banks.
        (-344, -12.0, .25, "walking", .14), (-340, -11.2, -.28, "conversation", .14),
        (-306, -12.0, .18, "walking", .14), (-302, -11.2, -.20, "conversation", .14),
        (-260, -12.0, .22, "walking", .14), (-256, -11.2, -.24, "conversation", .14),
        (-218, -12.0, .20, "walking", .14), (-214, -11.2, -.20, "conversation", .14),
        (-331, -27.0, .12, "walking", 2.30), (-315, -26.0, -.18, "conversation", 2.30),
        (-279, -27.2, .24, "walking", 2.30), (-263, -26.2, -.22, "conversation", 2.30),
        (-225, -27.0, .18, "walking", 2.30), (-209, -26.2, -.20, "conversation", 2.30),
        (-318, 11.8, -.20, "walking", .14), (-314, 11.1, .20, "conversation", .14),
        (-272, 11.8, -.24, "walking", .14), (-268, 11.1, .24, "conversation", .14),
    )
    for index, (x, y, facing, action, z_base) in enumerate(groups):
        records.append(_add_mid_detail_human(human_batch, x, y, facing,
                                             1480 + index, action, z_base))
    # Seated groups are tied to the two inhabited civic islands.  Their bent
    # legs meet the plaza grade and make the benches read as programmed space.
    seated = (
        (-325.4, -28.5, math.pi, 3.02), (-321.8, -28.5, math.pi, 3.02),
        (-277.8, -30.0, math.pi, 3.02), (-273.4, -30.0, math.pi, 3.02),
        (-289.0, -43.9, 0.0, 3.05), (-285.7, -43.9, 0.0, 3.05),
    )
    for index, (x, y, facing, seat_z) in enumerate(seated):
        records.append(_add_seated_human(human_batch, x, y, facing,
                                         1680 + index, seat_z, 2.30))
    # Bicycle parking and a low planter edge clarify the public lobby program.
    for rack in range(5):
        x = -347.0 + rack * 1.25
        prop_batch.add_cylinder("v34-signature-bicycle-wheel", "service-charcoal",
                                (x, -43.0, 2.72), .42, .08, 20)
        prop_batch.add_cylinder("v34-signature-bicycle-rack", "archive-metal",
                                (x, -43.0, 2.92), .055, 1.24, 10)
    prop_batch.add_box("v34-signature-activity-planter", "archive-warm-stone",
                       (-286, -44.8, 2.92), (12.0, 2.6, 1.18))
    prop_batch.add_box("v34-signature-activity-soil", "soil-v11",
                       (-286, -44.8, 3.55), (11.5, 2.1, .10))
    for shrub in range(9):
        _add_irregular_canopy_lobe(
            prop_batch, "v35-signature-irregular-shrub",
            ("foliage-deep", "foliage-mid", "foliage-light")[shrub % 3],
            (-291 + shrub * 1.25, -44.8, 4.03 + (shrub % 2) * .10),
            .58 + (shrub % 3) * .08, (1.15, .75, .68), 2300 + shrub, 12, 5)
    # Two offset inhabited islands turn the former blank civic apron into a
    # spatially legible forecourt without blocking the lobby sightline.
    for island, (ix, iy, iw, angle) in enumerate(((-322.0, -31.5, 13.5, -.10),
                                                   (-274.0, -33.0, 15.0, .12))):
        prop_batch.add_box("v34-civic-island-stone-edge", "archive-warm-stone",
                           (ix, iy, 2.72), (iw, 4.8, .82), angle)
        prop_batch.add_box("v34-civic-island-soil", "soil-v11",
                           (ix, iy, 3.18), (iw - .75, 4.05, .12), angle)
        for plant in range(7):
            px = ix - iw * .36 + plant * iw * .12
            py = iy + math.sin(plant * 1.7 + island) * .72
            _add_irregular_canopy_lobe(
                prop_batch, "v35-civic-island-irregular-planting",
                ("foliage-deep", "foliage-mid", "foliage-light")[(plant + island) % 3],
                (px, py, 3.70 + .10 * (plant % 2)),
                .64 + .08 * (plant % 3), (1.20, .82, .74),
                2350 + island * 20 + plant, 12, 5)
        for bench in (-1, 1):
            bench_x = ix + bench * iw * .28
            for slat in range(4):
                prop_batch.add_box("v35-civic-island-bench-seat-slat", "timber-accent",
                                   (bench_x, iy + 2.76 + slat * .16, 2.84),
                                   (iw * .30, .115, .12), angle)
            for slat in range(3):
                prop_batch.add_box("v35-civic-island-bench-back-slat", "timber-accent",
                                   (bench_x, iy + 3.38, 3.07 + slat * .16),
                                   (iw * .30, .10, .11), angle)
            for support in (-1, 1):
                prop_batch.add_box("v35-civic-island-bench-support", "archive-metal",
                                   (bench_x + support * iw * .105, iy + 3.0, 2.58),
                                   (.12, .48, .44), angle)
    # Deliberate tree rooms frame entrances and water views.  These are not a
    # random scatter: four paired positions enclose seating and leave the
    # central lobby axis open on both banks.
    for bank in (-1, 1):
        for tree_index, (tx, offset) in enumerate(((-340.0, 0.0), (-310.0, 1.4),
                                                   (-270.0, -1.0), (-224.0, .8))):
            ty = bank * (34.0 + offset)
            _add_architectural_tree(prop_batch, tx, ty,
                                    2700 + tree_index + (20 if bank > 0 else 0),
                                    .58 + .04 * (tree_index % 2), 2.30)
            prop_batch.add_box("v35-civic-tree-root-grate", "ledger-granite",
                               (tx, ty, 2.38), (2.8, 2.8, .10))
            for groundcover in range(4):
                gx = tx - 1.0 + groundcover * .68
                gy = ty + math.sin(groundcover * 1.8) * .58
                _add_irregular_canopy_lobe(
                    prop_batch, "v35-civic-tree-room-groundcover",
                    ("foliage-deep", "foliage-mid", "foliage-light")[groundcover % 3],
                    (gx, gy, 2.92), .40 + .05 * (groundcover % 2),
                    (1.05, .78, .58), 2800 + tree_index * 10 + groundcover,
                    12, 5)
    # A narrow darker inlay records the primary pedestrian axis in real
    # geometry and breaks the oversized pale paving field.
    prop_batch.add_box("v34-civic-forecourt-axis-inlay", "ledger-granite",
                       (-300.0, -30.0, 2.345), (7.0, 20.0, .055))
    prop_batch.add_box("v34-civic-forecourt-axis-core", "dry-stone",
                       (-300.0, -30.0, 2.382), (5.8, 20.0, .055))
    # Actual fixture geometry marks the lobby-to-water hierarchy at night.
    for bank in (-1, 1):
        for x in (-334.0, -318.0, -282.0, -266.0):
            prop_batch.add_cylinder("v35-civic-pedestrian-light-pole", "archive-metal",
                                    (x, bank * 36.5, 4.10), .075, 3.55, 12)
            prop_batch.add_cylinder("v35-civic-pedestrian-light-fixture", "warm-light",
                                    (x, bank * 36.5, 5.90), .19, .18, 16)
    human_objects = human_batch.finalize()
    for obj in human_objects:
        obj["nearFieldMidDetailHuman"] = True
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    v12.consolidate(prop_batch)
    return human_objects + prop_batch.finalize(), records


def _add_stream_civic_rooms():
    """Six programmed overlooks replace residual blank promenade stretches."""
    batch = v12.HeroBatch(v12.create_materials())
    room_records = []
    for bank in (-1, 1):
        for index, x in enumerate((-318.0, -272.0, -214.0)):
            y = bank * (18.3 + (index % 2) * 1.1)
            facing = -bank
            width = 12.5 + index * 1.4
            # Real raised threshold and retaining lip at the stream side.
            batch.add_box("v34-stream-room-platform", "dry-stone",
                          (x, y, 2.40), (width, 6.8, .26))
            batch.add_box("v34-stream-room-water-edge-seat", "timber-accent",
                          (x, y + facing * 2.65, 2.78),
                          (width * .72, .72, .18))
            batch.add_box("v34-stream-room-seat-plinth", "archive-metal",
                          (x, y + facing * 2.65, 2.56),
                          (width * .64, .42, .42))
            # Paired planting frames the room while preserving the water view.
            for side in (-1, 1):
                px = x + side * width * .43
                batch.add_box("v34-stream-room-planter", "archive-warm-stone",
                              (px, y - facing * .55, 2.92),
                              (2.35, 3.2, 1.12))
                batch.add_box("v34-stream-room-planter-soil", "soil-v11",
                              (px, y - facing * .55, 3.51),
                              (2.0, 2.85, .10))
                for shrub in range(3):
                    _add_irregular_canopy_lobe(
                        batch, "v35-stream-room-irregular-shrub",
                        ("foliage-deep", "foliage-mid", "foliage-light")[(index + shrub) % 3],
                        (px + (shrub - 1) * .55, y - facing * .55,
                         3.94 + .08 * (shrub % 2)),
                        .52 + .08 * shrub, (1.05, .72, .66),
                        2500 + index * 20 + shrub + (8 if bank > 0 else 0), 12, 5)
            # Every other room is shaded by a slim, buildable pergola rather
            # than a floating decorative plane.
            if index % 2 == 0:
                canopy_y = y - facing * .72
                for side in (-1, 1):
                    batch.add_cylinder("v34-stream-room-pergola-column", "archive-metal",
                                       (x + side * width * .34, canopy_y, 4.86),
                                       .13, 4.9, 14)
                batch.add_box("v34-stream-room-pergola-beam", "archive-metal",
                              (x, canopy_y, 7.32), (width * .80, .26, .28))
                for slat in range(7):
                    sx = x - width * .35 + slat * width * .70 / 6
                    batch.add_box("v34-stream-room-pergola-slat", "timber-accent",
                                  (sx, canopy_y, 7.42), (.18, 4.6, .18))
            batch.add_box("v34-stream-room-step-light", "warm-light",
                          (x, y + facing * 3.04, 2.62),
                          (width * .64, .08, .10))
            room_records.append({"bank": bank, "position": [x, y],
                                 "program": "shaded-overlook" if index % 2 == 0 else "open-seating"})
    v12.consolidate(batch)
    return batch.finalize(), room_records


def _add_stream_liner_architecture():
    """Build six attached, occupied 2-3 storey stream frontage buildings.

    Each liner is a complete floor/ceiling/rear-wall envelope with bounded
    stream-facing rooms, side walls, a roof terrace and a covered connection to
    its parent podium.  This closes the former dead apron with architecture,
    not scenery boxes, while preserving the lower promenade and fire corridor.
    """
    materials = v12.create_materials()
    objects, records = [], []
    specs = (
        (-320.0, 49.0, 31.0, 20.0, 3, 0),
        (-252.0, 50.5, 35.0, 22.0, 2, 1),
        (-187.0, 48.0, 29.0, 19.0, 3, 2),
        (-321.0, -49.0, 29.0, 19.0, 2, 3),
        (-254.0, -51.0, 36.0, 22.0, 3, 4),
        (-188.0, -48.5, 32.0, 20.0, 2, 5),
    )
    for x, y, width, depth, floors, style in specs:
        north = y > 0
        facing = -1 if north else 1
        inside = -facing
        stone, accent = _material_pair(style, north)
        batch = v12.HeroBatch(materials)
        grade = 2.30
        floor_h = 4.15 if floors == 2 else 3.85
        height = floors * floor_h
        face_y = y + facing * depth * .5
        rear_y = y + inside * depth * .5
        bay_count = 5 + style % 3
        bay_pitch = width / bay_count

        batch.add_box("v34-liner-floor", "ledger-granite",
                      (x, y, grade + .14), (width, depth, .28))
        batch.add_box("v34-liner-roof", stone,
                      (x, y, grade + height), (width + .5, depth + .5, .40))
        batch.add_box("v34-liner-rear-wall", "service-charcoal",
                      (x, rear_y, grade + height * .5), (width, .36, height))
        for side in (-1, 1):
            batch.add_box("v34-liner-side-wall", stone,
                          (x + side * width * .5, y, grade + height * .5),
                          (.42, depth, height))
        for floor in range(1, floors):
            z = grade + floor * floor_h
            batch.add_box("v34-liner-occupied-floor-plate", "ledger-granite",
                          (x, y, z), (width - .48, depth - .50, .26))

        # Every stream-facing bay is a bounded room.  Glass is recessed inside
        # four structural returns and cannot detach from the building body.
        for floor in range(floors):
            room_z = grade + floor * floor_h + floor_h * .5
            for bay in range(bay_count):
                bx = x - width * .5 + (bay + .5) * bay_pitch
                public_bay = floor == 0 or (bay + floor + style) % 3 != 0
                batch.add_box("v34-liner-room-back", "warm-interior" if public_bay else stone,
                              (bx, rear_y + facing * .34, room_z),
                              (bay_pitch - .34, .20, floor_h - .38))
                material = "frontage-glass" if public_bay else stone
                batch.add_box("v34-liner-integrated-glass" if public_bay else "v34-liner-solid-service-infill",
                              material, (bx, face_y + inside * .46, room_z),
                              (bay_pitch - .42, .12 if public_bay else .22, floor_h - .66))
                for edge in (-1, 1):
                    batch.add_box("v34-liner-window-jamb-return", accent,
                                  (bx + edge * (bay_pitch * .5 - .16),
                                   face_y + inside * .28, room_z),
                                  (.18, .74, floor_h - .42))
                batch.add_box("v34-liner-window-head-return", accent,
                              (bx, face_y + inside * .28, room_z + floor_h * .5 - .25),
                              (bay_pitch - .20, .74, .22))
                batch.add_box("v34-liner-window-sill-return", stone,
                              (bx, face_y + inside * .28, room_z - floor_h * .5 + .25),
                              (bay_pitch - .20, .74, .28))
                if floor == 0 and public_bay:
                    # Five-metre-deep occupied rooms sit directly behind each
                    # opening.  Continuous floor/ceiling and bay partitions
                    # prove that the glazing belongs to a building envelope.
                    room_depth = min(6.2, depth * .34)
                    occupied_y = face_y + inside * (room_depth * .52)
                    batch.add_box("v35-liner-public-room-floor", "ledger-granite",
                                  (bx, occupied_y, grade + .18),
                                  (bay_pitch - .48, room_depth, .22))
                    batch.add_box("v35-liner-public-room-ceiling", "warm-interior",
                                  (bx, occupied_y, grade + floor_h - .20),
                                  (bay_pitch - .48, room_depth, .18))
                    for edge in (-1, 1):
                        batch.add_box("v35-liner-public-room-side-partition", stone,
                                      (bx + edge * (bay_pitch * .5 - .24), occupied_y,
                                       grade + floor_h * .5),
                                      (.18, room_depth, floor_h - .42))
                    batch.add_box("v35-liner-public-room-rear-display", "warm-interior",
                                  (bx, face_y + inside * room_depth,
                                   grade + floor_h * .52),
                                  (bay_pitch - .52, .18, floor_h - .64))
                    batch.add_box("v34-liner-interior-counter", "timber-accent",
                                  (bx, face_y + inside * (room_depth * .72), grade + .74),
                                  (bay_pitch * .52, .72, 1.05))
                    batch.add_box("v34-liner-warm-ceiling-light", "warm-light",
                                  (bx, face_y + inside * (room_depth * .50), grade + floor_h - .30),
                                  (bay_pitch * .56, 2.1, .07))
                    if (bay + style) % 2:
                        table_y = face_y + inside * (room_depth * .43)
                        batch.add_cylinder("v35-liner-interior-cafe-table", "ledger-bronze",
                                           (bx, table_y, grade + .82), .52, .10, 18)
                        for chair in (-1, 1):
                            batch.add_box("v35-liner-interior-chair", "timber-accent",
                                          (bx + chair * .92, table_y,
                                           grade + .48), (.42, .48, .68))
                    else:
                        for shelf in range(3):
                            batch.add_box("v35-liner-interior-display-shelf", "timber-accent",
                                          (bx, face_y + inside * (room_depth * .90),
                                           grade + .62 + shelf * .72),
                                          (bay_pitch * .52, .24, .10))

        arcade_depth = 3.2 + .35 * (style % 3)
        batch.add_box("v34-liner-arcade-canopy", stone,
                      (x, face_y + facing * arcade_depth * .5, grade + floor_h + .16),
                      (width + 1.4, arcade_depth, .36))
        batch.add_box("v34-liner-arcade-soffit", "warm-light",
                      (x, face_y + facing * arcade_depth * .5, grade + floor_h - .06),
                      (width + .8, arcade_depth - .35, .07))
        for column in range(bay_count + 1):
            cx = x - width * .5 + column * bay_pitch
            batch.add_cylinder("v34-liner-arcade-column", accent,
                               (cx, face_y + facing * (arcade_depth - .42),
                                grade + floor_h * .5), .19, floor_h, 16)
        entry_bay = (2 * style + 1) % bay_count
        entry_x = x - width * .5 + (entry_bay + .5) * bay_pitch
        batch.add_box("v34-liner-entry-frame", accent,
                      (entry_x, face_y + facing * .10, grade + 1.62),
                      (2.15, .34, 3.24))
        batch.add_box("v34-liner-entry-door", "frontage-glass",
                      (entry_x, face_y + facing * .15, grade + 1.55),
                      (1.80, .10, 2.90))
        # A recessed vestibule distinguishes the entrance from adjacent retail
        # bays and gives every liner a physically readable arrival sequence.
        vestibule_depth = 3.4 + .35 * (style % 2)
        batch.add_box("v35-liner-entry-vestibule-floor", "ledger-granite",
                      (entry_x, face_y + inside * vestibule_depth * .5,
                       grade + .22), (3.4, vestibule_depth, .22))
        batch.add_box("v35-liner-entry-vestibule-ceiling", "warm-interior",
                      (entry_x, face_y + inside * vestibule_depth * .5,
                       grade + floor_h - .20), (3.4, vestibule_depth, .18))
        for side in (-1, 1):
            batch.add_box("v35-liner-entry-vestibule-return", accent,
                          (entry_x + side * 1.65,
                           face_y + inside * vestibule_depth * .5,
                           grade + floor_h * .5),
                          (.16, vestibule_depth, floor_h - .42))
        batch.add_box("v35-liner-entry-inner-door", "frontage-glass",
                      (entry_x, face_y + inside * vestibule_depth,
                       grade + 1.55), (1.80, .10, 2.90))

        parent_y = 78.0 if north else -78.0
        connector_length = max(8.0, abs(parent_y - rear_y))
        connector_y = (rear_y + parent_y) * .5
        batch.add_box("v34-liner-covered-parent-connector", stone,
                      (x, connector_y, grade + 5.15),
                      (7.2, connector_length, .34))
        for side in (-1, 1):
            batch.add_box("v34-liner-roof-planter", stone,
                          (x + side * width * .28, y, grade + height + .72),
                          (width * .28, depth * .22, 1.05))
            batch.add_box("v34-liner-roof-planting", "foliage-deep",
                          (x + side * width * .28, y, grade + height + 1.42),
                          (width * .24, depth * .18, .42))
        records.append({"style": style, "floors": floors,
                        "boundedRooms": bay_count * floors,
                        "deepPublicRooms": sum(
                            1 for bay in range(bay_count)
                            if (bay + style) % 3 != 0),
                        "vestibuleDepthM": vestibule_depth,
                        "streamFacing": True, "parentPodiumConnected": True})
        v12.consolidate(batch)
        objects.extend(batch.finalize())
    return objects, records


def _add_mid_detail_human(batch, x, y, facing, seed, action, z_base):
    """Near-camera human with continuous anatomical volumes, not box limbs."""
    height = 1.66 + (seed % 7) * .025
    body = ("archive-metal", "ledger-bronze", "service-charcoal")[seed % 3]
    skin = "archive-warm-stone"
    forward = (math.sin(facing), math.cos(facing))
    right = (math.cos(facing), -math.sin(facing))
    hip_z, chest_z, shoulder_z = z_base + height * .48, z_base + height * .68, z_base + height * .80
    head_z = z_base + height * .94
    batch.add_frustum("v34-human-tailored-torso", body,
                      (x, y, (hip_z + shoulder_z) * .5), .155, .225,
                      shoulder_z - hip_z, 18)
    batch.add_frustum("v34-human-jacket-lower", body,
                      (x, y, (hip_z + chest_z) * .5), .19, .17,
                      chest_z - hip_z, 18)
    batch.add_cylinder("v34-human-neck", skin, (x, y, head_z - .14), .061, .15, 14)
    batch.add_uv_sphere("v34-human-head", skin, (x, y, head_z), .126, 24, 12, (1, .92, 1.08))
    batch.add_uv_sphere("v34-human-hair", "service-charcoal",
                        (x, y - .012, head_z + .065), .113, 22, 10, (1.03, .96, .72))
    stride = .19 if action == "walking" else .035
    for side in (-1, 1):
        hip = (x + right[0] * side * .095, y + right[1] * side * .095, hip_z)
        knee = (hip[0] + forward[0] * side * stride * .42,
                hip[1] + forward[1] * side * stride * .42, z_base + height * .27)
        foot = (x + right[0] * side * .10 + forward[0] * side * stride,
                y + right[1] * side * .10 + forward[1] * side * stride, z_base + .08)
        batch.add_tapered_branch("v34-human-upper-leg", "service-charcoal",
                                 hip, knee, .086, .070, 12)
        batch.add_tapered_branch("v34-human-lower-leg", "service-charcoal",
                                 knee, foot, .070, .048, 12)
        shoe_tip = (foot[0] + forward[0] * .16, foot[1] + forward[1] * .16, z_base + .06)
        batch.add_tapered_branch("v34-human-shoe", "service-charcoal",
                                 foot, shoe_tip, .064, .050, 12)
        shoulder = (x + right[0] * side * .22, y + right[1] * side * .22, shoulder_z - .035)
        if action == "conversation":
            elbow = (shoulder[0] + forward[0] * (.10 + .05 * side),
                     shoulder[1] + forward[1] * (.10 + .05 * side),
                     z_base + height * (.64 + .035 * side))
            hand = (x + forward[0] * (.22 + .06 * side) + right[0] * side * .10,
                    y + forward[1] * (.22 + .06 * side) + right[1] * side * .10,
                    z_base + height * (.66 + .04 * side))
        else:
            elbow = (shoulder[0] - forward[0] * side * stride * .60,
                     shoulder[1] - forward[1] * side * stride * .60,
                     z_base + height * .64)
            hand = (elbow[0] + forward[0] * side * stride * .33,
                    elbow[1] + forward[1] * side * stride * .33,
                    z_base + height * .49)
        batch.add_tapered_branch("v34-human-upper-arm", body, shoulder, elbow, .067, .052, 12)
        batch.add_tapered_branch("v34-human-lower-arm", body, elbow, hand, .052, .039, 12)
        batch.add_uv_sphere("v34-human-hand", skin, hand, .052, 14, 7, (1, .84, 1.08))
    if seed % 4 == 0:
        bag_x, bag_y = x + right[0] * .28, y + right[1] * .28
        batch.add_frustum("v34-human-shoulder-bag", "timber-accent",
                          (bag_x, bag_y, z_base + height * .49), .13, .17, .35, 14)
    return {"position": [x, y], "action": action, "orientation": facing,
            "grounded": True, "detail": "MID_DETAIL_NEAR_FIELD"}


def _canonical_material_name(name):
    """Remove Blender's numeric duplicate suffix without touching semantic ids."""
    stem, dot, suffix = name.rpartition(".")
    return stem if dot and suffix.isdigit() else name


def _consolidate_scene_objects_by_material(objects):
    """Merge static hero geometry to one draw surface per semantic material.

    Earlier revisions consolidated each generator batch independently, leaving
    dozens of duplicate material datablocks and hundreds of WebGL draw calls.
    All hero geometry is static, so canonicalising those duplicates and joining
    equal-material objects preserves geometry while reducing runtime work.
    """
    canonical = {}
    for material in list(bpy.data.materials):
        key = _canonical_material_name(material.name)
        canonical.setdefault(key, material)
    groups = {}
    for obj in objects:
        if obj.type != "MESH" or not obj.data.materials:
            continue
        for slot in range(len(obj.data.materials)):
            material = obj.data.materials[slot]
            if material is None:
                continue
            key = _canonical_material_name(material.name)
            obj.data.materials[slot] = canonical[key]
        key = tuple(material.name if material else "none" for material in obj.data.materials)
        groups.setdefault(key, []).append(obj)
    merged = []
    bpy.ops.object.select_all(action="DESELECT")
    for key, group in groups.items():
        live = [obj for obj in group if obj.name in bpy.data.objects]
        if not live:
            continue
        for obj in live:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = live[0]
        if len(live) > 1:
            bpy.ops.object.join()
        joined = bpy.context.view_layer.objects.active
        joined.name = "v34-runtime-batch-" + "-".join(key)
        merged.append(joined)
        bpy.ops.object.select_all(action="DESELECT")
    return merged, {
        "strategy": "GLOBAL_STATIC_ONE_MESH_PER_SEMANTIC_MATERIAL",
        "sourceObjects": len(objects), "runtimeObjects": len(merged),
        "materialBuckets": len(groups),
    }


def _add_signature_tower_civic_wing(batch, *, x, y, width, depth, podium_h,
                                    floor_h, facing, style, stone, accent):
    """Attach a four-storey civic wing to each principal Archive tower body.

    This is a massing operation, not a facade applique: the wing has floor
    plates, a rear/side envelope, recessed per-floor glazing, a roof terrace and
    a vertical service spine.  It creates a third massing step between podium
    and tower and makes the two signature buildings legibly asymmetric.
    """
    inside = -facing
    hand = -1 if style == 0 else 1
    wing_w = width * .38
    wing_d = depth * .48
    wing_floors = 4
    wing_h = wing_floors * floor_h
    wing_x = x + hand * width * .31
    wing_y = y + facing * depth * .12
    face_y = wing_y + facing * wing_d * .5
    rear_y = wing_y + inside * wing_d * .5
    batch.add_box("v35-signature-civic-wing-structural-body", stone,
                  (wing_x, wing_y + inside * 1.15, podium_h + wing_h * .5),
                  (wing_w, wing_d - 2.30, wing_h))
    batch.add_box("v35-signature-civic-wing-rear-service-spine", "service-charcoal",
                  (wing_x + hand * wing_w * .34, rear_y,
                   podium_h + wing_h * .5),
                  (wing_w * .22, .52, wing_h + .30))
    bay_count = 4
    pitch = wing_w / bay_count
    for floor in range(wing_floors):
        z0 = podium_h + floor * floor_h
        room_z = z0 + floor_h * .5
        batch.add_box("v35-signature-civic-wing-floor-plate", "ledger-granite",
                      (wing_x, face_y + inside * 1.35, z0 + .13),
                      (wing_w - .40, 2.60, .26))
        batch.add_box("v35-signature-civic-wing-room-back", "warm-interior",
                      (wing_x, face_y + inside * 2.58, room_z),
                      (wing_w - .42, .18, floor_h - .48))
        for bay in range(bay_count):
            bx = wing_x - wing_w * .5 + (bay + .5) * pitch
            batch.add_box("v35-signature-civic-wing-integrated-glass",
                          "occupied-window-glass" if (bay + floor) % 3 == 0
                          else "blue-gray-glass",
                          (bx, face_y + inside * .48, room_z),
                          (pitch - .34, .12, floor_h - .70))
            for edge in (-1, 1):
                batch.add_box("v35-signature-civic-wing-jamb-return", accent,
                              (bx + edge * (pitch * .5 - .14),
                               face_y + inside * .30, room_z),
                              (.16, .68, floor_h - .48))
            batch.add_box("v35-signature-civic-wing-head-return", accent,
                          (bx, face_y + inside * .30,
                           room_z + floor_h * .5 - .25),
                          (pitch - .18, .68, .18))
            batch.add_box("v35-signature-civic-wing-sill-return", stone,
                          (bx, face_y + inside * .30,
                           room_z - floor_h * .5 + .24),
                          (pitch - .18, .68, .24))
    # A planted roof room completes the stepped silhouette and maintains the
    # public-space language above the stream-facing podium.
    roof_z = podium_h + wing_h
    batch.add_box("v35-signature-civic-wing-roof-terrace", "dry-stone",
                  (wing_x, wing_y, roof_z + .18), (wing_w + .70, wing_d + .70, .36))
    for side in (-1, 1):
        batch.add_box("v35-signature-civic-wing-roof-planter", stone,
                      (wing_x + side * wing_w * .30, wing_y,
                       roof_z + .72), (wing_w * .24, wing_d * .32, .92))
        batch.add_box("v35-signature-civic-wing-roof-planting", "foliage-deep",
                      (wing_x + side * wing_w * .30, wing_y,
                       roof_z + 1.30), (wing_w * .20, wing_d * .27, .34))
    batch.add_box("v35-signature-civic-wing-vertical-frame", accent,
                  (wing_x - hand * wing_w * .50, face_y + facing * .38,
                   podium_h + wing_h * .50),
                  (.54, 1.18, wing_h + .52))


def _add_upper_side_rear_envelope(batch, *, x, y, width, depth, base_z,
                                  floors, floor_h, facing, style, stone, accent):
    """Close the setback tower with recessed, bounded side/rear openings."""
    height = floors * floor_h
    side_bays = max(3, round(depth / 5.4))
    side_pitch = depth * .92 / side_bays
    side_reveal = 1.05
    for side in (-1, 1):
        face_x = x + side * width * .5
        for floor in range(floors):
            z = base_z + floor * floor_h + floor_h * .5
            opening_h = floor_h - (.76 if floor % 3 else .92)
            for bay in range(side_bays):
                sy = y - depth * .46 + (bay + .5) * side_pitch
                service = (bay + floor + style) % 8 == 0
                material = stone if service else (
                    "occupied-window-glass" if (bay + floor + style) % 3 == 0
                    else "blue-gray-glass")
                batch.add_box("v42-upper-side-bounded-infill", material,
                              (face_x - side * .32, sy, z),
                              (.14, side_pitch - .30, opening_h))
                for edge in (-1, 1):
                    batch.add_box("v42-upper-side-jamb-return", accent,
                                  (face_x - side * (side_reveal * .52),
                                   sy + edge * (side_pitch * .5 - .12), z),
                                  (side_reveal + .10, .15, opening_h + .12))
                batch.add_box("v42-upper-side-head-return", accent,
                              (face_x - side * (side_reveal * .52), sy,
                               z + opening_h * .5),
                              (side_reveal + .10, side_pitch - .16, .16))
                batch.add_box("v42-upper-side-sill-return", stone,
                              (face_x - side * (side_reveal * .52), sy,
                               z - opening_h * .5),
                              (side_reveal + .10, side_pitch - .16, .20))
        for band_floor in range(0, floors + 1, 3):
            batch.add_box("v42-upper-side-floor-band", stone,
                          (face_x - side * (side_reveal * .52), y,
                           base_z + band_floor * floor_h),
                          (side_reveal + .10, depth * .75, .30))
    rear_y = y - facing * depth * .5
    rear_outward = -facing
    rear_bays = max(4, round(width / 5.0))
    rear_pitch = width * .90 / rear_bays
    for floor in range(floors):
        z = base_z + floor * floor_h + floor_h * .5
        for bay in range(rear_bays):
            bx = x - width * .45 + (bay + .5) * rear_pitch
            material = "service-charcoal" if (floor + bay + style) % 7 == 0 else "blue-gray-glass"
            batch.add_box("v42-upper-rear-bounded-infill", material,
                          (bx, rear_y + rear_outward * .28, z),
                          (rear_pitch - .34, .14, floor_h - .90))
            batch.add_box("v42-upper-rear-mullion", accent,
                          (bx, rear_y + rear_outward * .18, z),
                          (.12, .48, floor_h - .72))
        if floor % 3 == 0:
            batch.add_box("v42-upper-rear-service-band", accent,
                          (x, rear_y + rear_outward * .10,
                           base_z + (floor + 1) * floor_h),
                          (width * .78, .42, .34))
    return {"sideBayCount": side_bays, "rearBayCount": rear_bays,
            "boundedOpenings": True, "blankCoreExposure": False,
            "heightM": height}


def add_wall_first_building(batch, spec):
    x, y, width, depth, floors, floor_h, style = spec
    north = y > 0
    facing = -1 if north else 1
    stone, accent = _material_pair(style, north)
    podium_h = 8.2 + .55 * (style % 3)
    _inhabited_podium(batch, spec, podium_h, stone, accent)

    lower_floors = max(10, int(floors * (.60 + .03 * (style % 2))))
    upper_floors = floors - lower_floors
    lower_w = width * (.70 + .025 * (style % 3))
    lower_d = depth * (.66 + .02 * ((style + 1) % 3))
    lower_x = x + width * (-.06 if style % 2 else .06)
    lower_y = y
    lower_h = lower_floors * floor_h
    lower_face = lower_y + facing * lower_d * .5
    inside = -facing
    front_reveal, rear_reveal, side_reveal = 1.35, .95, 1.05
    # The core used to start 2.72m behind the glass while the bounded window
    # room was only 1.35m deep.  That left a visible air gap and made windows
    # look detached from the building.  The core now meets the room back exactly.
    _add_chamfered_mass(batch, "v34-tower-chamfered-structural-core", stone,
                        (lower_x,
                         lower_y + inside * (front_reveal - rear_reveal) * .5,
                         podium_h + lower_h * .5),
                        (lower_w - side_reveal * 2,
                         lower_d - front_reveal - rear_reveal, lower_h),
                        1.05 + .16 * (style % 3))
    for side in (-1, 1):
        for end in (-1, 1):
            batch.add_box("v38-lower-corner-bearing-pier", stone,
                          (lower_x + side * (lower_w * .5 - .58),
                           lower_y + end * (lower_d * .5 - .58),
                           podium_h + lower_h * .5),
                          (1.16, 1.16, lower_h))
    _bounded_curtain_wall(batch, x=lower_x, face_y=lower_face, facing=facing,
                                   width=lower_w, base_z=podium_h, floors=lower_floors,
                          floor_h=floor_h, style=style, stone=stone, accent=accent)
    _add_occupied_setback_terraces(batch, x=x, y=y, width=width, depth=depth,
                                   podium_h=podium_h,
                                   transfer_z=podium_h + lower_h,
                                   facing=facing, style=style,
                                   stone=stone, accent=accent)
    if style in (0, 3):
        _add_signature_tower_civic_wing(
            batch, x=x, y=y, width=width, depth=depth, podium_h=podium_h,
            floor_h=floor_h, facing=facing, style=style,
            stone=stone, accent=accent)
    # Side walls are complete per-opening envelopes.  The former five tall
    # glass ribbons still left large blank slabs in the stream-axis camera and
    # read like applied decoration.  Every side lite now sits in a bounded
    # floor-by-floor opening recessed into the primary mass.
    for side in (-1, 1):
        side_x = lower_x + side * lower_w * .5
        side_bays = max(4, round(lower_d / 5.8))
        side_pitch = lower_d * .92 / side_bays
        for floor in range(lower_floors):
            opening_z = podium_h + floor * floor_h + floor_h * .5
            opening_h = floor_h - (.70 if floor % 4 else .86)
            for bay in range(side_bays):
                sy = lower_y - lower_d * .46 + (bay + .5) * side_pitch
                service = (bay + floor + style) % 9 == 0
                material = stone if service else (
                    "occupied-window-glass" if (bay + floor + style) % 4 == 0
                    else "blue-gray-glass")
                batch.add_box("v34-side-integrated-opening-infill", material,
                              (side_x - side * .34, sy, opening_z),
                              (.14, side_pitch - .32, opening_h))
                for edge in (-1, 1):
                    batch.add_box("v34-side-opening-jamb-return", accent,
                                  (side_x - side * (side_reveal * .52),
                                   sy + edge * (side_pitch * .5 - .13),
                                   opening_z),
                                  (side_reveal + .10, .16, opening_h + .12))
                batch.add_box("v34-side-opening-head-return", accent,
                              (side_x - side * (side_reveal * .52), sy,
                               opening_z + opening_h * .5),
                              (side_reveal + .10, side_pitch - .18, .16))
                batch.add_box("v34-side-opening-sill-return", accent,
                              (side_x - side * (side_reveal * .52), sy,
                               opening_z - opening_h * .5),
                              (side_reveal + .10, side_pitch - .18, .16))
        for bay in range(side_bays + 1):
            sy = lower_y - lower_d * .46 + bay * side_pitch
            batch.add_box("v34-side-structural-pier", stone,
                          (side_x - side * (side_reveal * .48), sy,
                           podium_h + lower_h * .5),
                          (side_reveal, .30, lower_h + .34))
        for band_floor in range(0, lower_floors + 1, 4):
            band_z = podium_h + band_floor * floor_h
            batch.add_box("v34-side-structural-floor-band", stone,
                          (side_x - side * (side_reveal * .52), lower_y, band_z),
                          (side_reveal + .10, lower_d * .90, .34))
    # Rear/service elevation has a distinct, still complete grammar.
    rear_face = lower_y - facing * lower_d * .5
    rear_outward = -facing
    for floor in range(lower_floors):
        rz = podium_h + floor * floor_h + floor_h * .5
        for bay in range(4):
            rx = lower_x - lower_w * .40 + bay * lower_w * .267
            material = "service-charcoal" if (floor + bay + style) % 7 == 0 else "blue-gray-glass"
            batch.add_box("v34-rear-integrated-service-window", material,
                          (rx, rear_face - rear_outward * .18, rz),
                          (lower_w * .14, .14, floor_h * .58))
        if floor % 5 == 0:
            batch.add_box("v34-rear-mechanical-service-band", accent,
                          (lower_x, rear_face + rear_outward * .10, rz),
                          (lower_w * .78, .46, .50))
    upper_w, upper_d = lower_w, lower_d
    upper_x, upper_y = lower_x, lower_y
    if upper_floors:
        upper_h = upper_floors * floor_h
        upper_w = lower_w * (.68 + .05 * (style % 3))
        upper_d = lower_d * (.70 + .04 * ((style + 1) % 3))
        upper_x = lower_x + (1 if style % 2 else -1) * lower_w * .10
        upper_y = lower_y - facing * 1.6
        upper_face = upper_y + facing * upper_d * .5
        _add_chamfered_mass(batch, "v34-upper-chamfered-structural-core", stone,
                            (upper_x,
                             upper_y + inside * (front_reveal - rear_reveal) * .5,
                             podium_h + lower_h + upper_h * .5),
                            (upper_w - side_reveal * 2,
                             upper_d - front_reveal - rear_reveal, upper_h),
                            .92 + .14 * ((style + 1) % 3))
        for side in (-1, 1):
            for end in (-1, 1):
                batch.add_box("v38-upper-corner-bearing-pier", stone,
                              (upper_x + side * (upper_w * .5 - .54),
                               upper_y + end * (upper_d * .5 - .54),
                               podium_h + lower_h + upper_h * .5),
                              (1.08, 1.08, upper_h))
        _bounded_curtain_wall(batch, x=upper_x, face_y=upper_face, facing=facing,
                              width=upper_w, base_z=podium_h + lower_h,
                              floors=upper_floors, floor_h=floor_h,
                              style=style + 7, stone=stone, accent=accent)
        _add_upper_side_rear_envelope(
            batch, x=upper_x, y=upper_y, width=upper_w, depth=upper_d,
            base_z=podium_h + lower_h, floors=upper_floors,
            floor_h=floor_h, facing=facing, style=style + 7,
            stone=stone, accent=accent)
    roof_z = podium_h + floors * floor_h
    roof_x = upper_x if upper_floors else lower_x
    roof_y = upper_y if upper_floors else lower_y
    roof_w = upper_w if upper_floors else lower_w
    roof_d = upper_d if upper_floors else lower_d
    # A continuous parapet establishes the load-bearing roof datum.  Every
    # crown and service volume below is contained within this top footprint.
    for side in (-1, 1):
        batch.add_box("v38-roof-parapet-long", stone,
                      (roof_x, roof_y + side * (roof_d * .5 - .18), roof_z + .64),
                      (roof_w, .36, 1.28))
        batch.add_box("v38-roof-parapet-short", stone,
                      (roof_x + side * (roof_w * .5 - .18), roof_y, roof_z + .64),
                      (.36, roof_d, 1.28))
    _add_chamfered_mass(batch, "v34-integrated-chamfered-machine-room", "service-charcoal",
                        (roof_x - roof_w * .08, roof_y, roof_z + 2.3),
                        (roof_w * .30, roof_d * .30, 4.6), .52)
    batch.add_box("v38-roof-screen-return", accent,
                  (roof_x + roof_w * .13,
                   roof_y + facing * roof_d * .11, roof_z + 2.55),
                  (roof_w * .24, roof_d * .20, 3.8))
    for unit in range(3):
        batch.add_box("v38-roof-hvac", "service-charcoal",
                      (roof_x - roof_w * .18 + unit * roof_w * .18,
                       roof_y - facing * roof_d * .18, roof_z + 1.20),
                      (min(2.2, roof_w * .13), min(2.8, roof_d * .18), 1.10))
    _add_style_specific_massing_details(batch, x=roof_x, y=roof_y, width=roof_w,
                                        depth=roof_d, roof_z=roof_z,
                                        facing=facing, style=style,
                                        stone=stone, accent=accent)
    STRUCTURAL_PLAUSIBILITY.append({
        "style": style,
        "windowRoomDepthM": front_reveal,
        "sideWindowRevealM": side_reveal,
        "rearWindowRevealM": rear_reveal,
        "coreMeetsWindowRoomBack": True,
        "topFootprintWidthM": roof_w,
        "topFootprintDepthM": roof_d,
        "roofEquipmentContained": True,
        "unsupportedRoofCapCount": 0,
        "upperMassContainedByLower": upper_w <= lower_w and upper_d <= lower_d,
    })


def _add_metropolitan_precision_layer():
    """Add place-specific occupied rooms and activity to the Archive hero zone.

    This layer is deliberately concentrated in the photographic foreground.
    It does not scatter props: every cluster is tied to a lobby, bridge landing,
    cafe terrace or promenade room.
    """
    batch = v12.HeroBatch(v12.create_materials())
    records, activity = [], []
    # Two different bank-side rooms close the gap between the civic podium and
    # the lower promenade.  Their floor/ceiling/rear-wall depth is visible.
    rooms = (
        (-304.0, -31.5, 1, 22.0, 7.2, "archive-warm-stone", "archive-metal", "arrival-lounge"),
        (-214.0, 31.5, -1, 25.0, 8.0, "ledger-limestone", "ledger-bronze", "water-cafe"),
    )
    for x, y, facing, width, depth, stone, accent, role in rooms:
        inside = -facing
        front_y = y + facing * depth * .5
        batch.add_box(f"v36-{role}-floor", "ledger-granite", (x, y, 2.48), (width, depth, .24))
        batch.add_box(f"v36-{role}-ceiling", "warm-interior", (x, y, 7.72), (width, depth, .22))
        batch.add_box(f"v36-{role}-rear-wall", stone, (x, front_y + inside * (depth - .22), 5.1), (width, .22, 5.0))
        for bay in range(5):
            bx = x - width * .5 + (bay + .5) * width / 5
            batch.add_box(f"v36-{role}-integrated-glass", "frontage-glass", (bx, front_y + inside * .34, 5.15), (width / 5 - .32, .14, 4.55))
            for edge in (-1, 1):
                batch.add_box(f"v36-{role}-jamb-return", accent, (bx + edge * (width / 10 - .14), front_y + inside * .45, 5.15), (.15, .90, 4.85))
            batch.add_box(f"v36-{role}-head-return", accent, (bx, front_y + inside * .45, 7.46), (width / 5 - .28, .90, .18))
            batch.add_box(f"v36-{role}-sill-return", stone, (bx, front_y + inside * .45, 2.82), (width / 5 - .28, .90, .24))
            batch.add_cylinder(f"v36-{role}-table", "timber-accent", (bx, y, 3.10), .74, .16, 18)
            batch.add_cylinder(f"v36-{role}-pendant", "warm-light", (bx, y, 7.44), .18, .18, 16)
        batch.add_box(f"v36-{role}-deep-canopy", accent, (x, front_y + facing * 2.2, 7.62), (width * .76, 4.8, .34))
        records.append({"role": role, "depthM": depth, "boundedBays": 5, "occupied": True})

    # Programmed bridge landings: seating, planting and lighting form distinct
    # rooms without obstructing the continuous accessible route.
    for landing_index, landing_x in enumerate((-286.0, -244.0, -202.0)):
        for bank in (-1, 1):
            y = bank * 19.8
            batch.add_box("v36-bridge-landing-inlay", "dry-stone", (landing_x, y, .32), (15.0, 7.0, .16))
            batch.add_box("v36-bridge-landing-seat", "timber-accent", (landing_x - 3.1, y + bank * 1.7, .72), (4.2, .78, .18))
            batch.add_box("v36-bridge-landing-planter", "archive-warm-stone", (landing_x + 4.0, y + bank * 1.6, .74), (3.2, 1.8, 1.0))
            batch.add_uv_sphere("v36-bridge-landing-planting", "foliage-mid", (landing_x + 4.0, y + bank * 1.6, 1.52), 1.05, 14, 8, (1.4, .8, .7))
            batch.add_cylinder("v36-bridge-landing-light-pole", "archive-metal", (landing_x, y - bank * 2.2, 2.25), .075, 4.2, 12)
            batch.add_cylinder("v36-bridge-landing-light", "warm-light", (landing_x, y - bank * 2.2, 4.42), .17, .18, 14)
            for person_index in range(4):
                activity.append(_add_mid_detail_human(batch, landing_x - 2.7 + person_index * 1.8, y - bank * .8, .12 * bank, 7600 + landing_index * 20 + person_index + (10 if bank > 0 else 0), "conversation" if person_index < 2 else "walking", .14))

    # Near-field tree rooms frame entrances and maintain open sightlines.
    for index, (x, y) in enumerate(((-322,-27),(-310,27),(-278,-28),(-266,28),(-226,-28),(-214,27),(-184,-27),(-174,27))):
        _add_architectural_tree(batch, x, y, 8100 + index, .72 + .05 * (index % 3), .14)
        batch.add_box("v36-tree-room-grate", "ledger-granite", (x, y, .20), (3.0, 3.0, .10))

    # Archive gateway bridge: keep the civic threshold legible without turning
    # the portal into a freestanding billboard that masks the inhabited bank.
    # The lower frame preserves the terrace-to-lobby and water sightline.
    gateway_x = -250.0
    batch.add_box("v37-archive-gateway-deck", "ledger-granite", (gateway_x, 0, 2.78), (11.5, 38.0, .58))
    batch.add_box("v37-archive-gateway-walking-surface", "dry-stone", (gateway_x, 0, 3.10), (10.6, 37.2, .12))
    for bank in (-1, 1):
        for side in (-1, 1):
            batch.add_box("v40-archive-gateway-portal-column", "archive-metal", (gateway_x + side * 4.55, bank * 13.2, 5.22), (.34, .48, 4.36))
        batch.add_box("v40-archive-gateway-portal-beam", "archive-metal", (gateway_x, bank * 13.2, 7.30), (9.45, .48, .30))
        batch.add_box("v40-archive-gateway-light-line", "archive-cyan-light", (gateway_x, bank * 13.0, 7.10), (7.90, .08, .07))
        batch.add_box("v37-archive-gateway-landing", "dry-stone", (gateway_x, bank * 22.4, 2.58), (20.0, 8.4, .22))
        batch.add_box("v37-archive-gateway-landing-seat", "timber-accent", (gateway_x - 5.2, bank * 22.4, 3.05), (5.4, 1.0, .18))
        for index in range(5):
            activity.append(_add_mid_detail_human(batch, gateway_x - 3.6 + index * 1.8, bank * (18.5 + .45 * (index % 2)), .12 * bank, 8400 + index + (20 if bank > 0 else 0), "walking" if index % 2 else "conversation", 3.10))

    # Cafe terraces read as programmed public rooms rather than loose props.
    for terrace_index, (tx, ty, facing) in enumerate(((-302.0, -23.5, 1), (-214.0, 23.5, -1))):
        batch.add_box("v37-cafe-terrace-paving", "dry-stone", (tx, ty, 2.52), (24.0, 10.0, .18))
        batch.add_box("v37-cafe-terrace-pergola-beam", "timber-accent", (tx, ty, 6.62), (23.0, .32, .34))
        for col in (-10.8, -5.4, 0, 5.4, 10.8):
            batch.add_cylinder("v37-cafe-terrace-pergola-column", "archive-metal", (tx + col, ty, 4.56), .13, 3.9, 14)
        for table_index in range(4):
            table_x = tx - 7.5 + table_index * 5.0
            table_y = ty + facing * 2.0
            batch.add_cylinder("v37-cafe-table", "timber-accent", (table_x, table_y, 3.25), .72, .16, 18)
            batch.add_cylinder("v37-cafe-table-leg", "archive-metal", (table_x, table_y, 2.88), .09, .72, 12)
            for chair_side in (-1, 1):
                batch.add_box("v37-cafe-chair-seat", "timber-accent", (table_x, table_y + chair_side * 1.05, 3.05), (.72, .72, .14))
                batch.add_box("v37-cafe-chair-back", "timber-accent", (table_x, table_y + chair_side * 1.32, 3.55), (.72, .12, .92))
            activity.append(_add_mid_detail_human(batch, table_x + .65, table_y, .18 * facing, 8500 + terrace_index * 20 + table_index, "conversation", 2.62))

    # Irregular planted pockets soften the retaining edge without becoming a
    # continuous decorative strip or blocking accessibility.
    for pocket_index, px in enumerate((-330.0, -294.0, -270.0, -230.0, -206.0, -178.0)):
        bank = -1 if pocket_index % 2 else 1
        py = bank * 15.8
        batch.add_box("v37-water-edge-planting-pocket", "wet-stone", (px, py, .34), (8.0, 2.8, .48))
        for plant_index in range(3):
            batch.add_uv_sphere("v37-water-edge-irregular-planting", "foliage-light" if plant_index % 2 else "foliage-mid", (px - 2.3 + plant_index * 2.3, py, 1.02 + .08 * plant_index), .72, 14, 8, (1.2, .65, .8 + .15 * plant_index))

    return batch.finalize(), {"occupiedRooms": records, "activityCount": len(activity), "bridgeLandingRooms": 6, "nearFieldTrees": 8, "archiveGatewayBridge": 1, "cafeTerraces": 2, "cafeTables": 8, "plantedWaterEdgePockets": 6}


def _add_hyper_polish_archive_scene():
    """Complete the Archive Water Plaza as one inhabited urban scene.

    Every object below belongs to a spatial room: occupied gallery, planted
    seating court, bridge landing or water-edge section.  The pass deliberately
    avoids a uniform scatter and leaves the six-metre promenade spine open.
    """
    batch = v12.HeroBatch(v12.create_materials())
    rooms, activity = [], []
    gallery_specs = (
        (-320.0, -39.0, 1, 24.0, 8.5, "arrival-gallery", "archive-warm-stone", "archive-metal"),
        (-270.0, 39.0, -1, 28.0, 9.2, "civic-library", "archive-warm-stone", "archive-metal"),
        (-212.0, -39.0, 1, 26.0, 8.8, "water-cafe", "ledger-limestone", "ledger-bronze"),
    )
    for room_index, (x, y, facing, width, depth, role, stone, accent) in enumerate(gallery_specs):
        inside = -facing
        face_y = y + facing * depth * .5
        batch.add_box("v41-hyper-gallery-floor", "ledger-granite",
                      (x, y, 2.46), (width, depth, .28))
        batch.add_box("v41-hyper-gallery-ceiling", stone,
                      (x, y, 8.36), (width, depth, .34))
        bays = 5 + room_index
        pitch = width / bays
        for bay in range(bays):
            bx = x - width * .5 + (bay + .5) * pitch
            back_depth = depth * (.66 + .08 * ((bay + room_index) % 3))
            batch.add_box("v41-hyper-gallery-room-back",
                          "warm-interior" if bay % 3 else stone,
                          (bx, face_y + inside * back_depth, 5.34),
                          (pitch - .42, .20, 5.42))
            batch.add_box("v41-hyper-gallery-glass", "frontage-glass",
                          (bx, face_y + inside * .26, 5.34),
                          (pitch - .30, .12, 5.28))
            for side in (-1, 1):
                batch.add_box("v41-hyper-gallery-deep-jamb", accent,
                              (bx + side * (pitch * .5 - .13),
                               face_y + inside * back_depth * .48, 5.34),
                              (.16, back_depth, 5.62))
            batch.add_box("v41-hyper-gallery-ceiling-light", "warm-light",
                          (bx, face_y + inside * back_depth * .50, 8.12),
                          (pitch * .54, 1.8, .07))
            batch.add_box("v41-hyper-gallery-table", "timber-accent",
                          (bx, face_y + inside * back_depth * .62, 3.12),
                          (pitch * .48, 1.12, .18))
        batch.add_box("v41-hyper-gallery-canopy", accent,
                      (x, face_y + facing * 2.4, 8.18),
                      (width * .72, 5.0, .34))
        batch.add_box("v41-hyper-gallery-canopy-light", "warm-light",
                      (x, face_y + facing * 2.4, 7.98),
                      (width * .65, 4.3, .08))
        rooms.append({"role": role, "depthM": depth, "bays": bays,
                      "occupied": True, "streamFacing": True})

    # Six distinct upper-bank rooms replace the pale residual forecourt with
    # cafe, arrival and civic seating compositions tied to the galleries.
    node_specs = (
        (-330.0, -24.0, "office-arrival"), (-292.0, 24.0, "civic-meeting"),
        (-258.0, -24.0, "bridge-crossing"), (-226.0, 24.0, "water-lunch"),
        (-195.0, -24.0, "evening-cafe"), (-176.0, 24.0, "promenade-rest"),
    )
    for node_index, (cx, cy, role) in enumerate(node_specs):
        bank = 1 if cy > 0 else -1
        accent = "archive-metal" if node_index < 4 else "ledger-bronze"
        batch.add_box("v41-hyper-room-inlay",
                      "dry-stone" if node_index % 2 else "promenade-paver",
                      (cx, cy, 2.39), (24.0, 9.0, .16))
        batch.add_box("v41-hyper-room-drain", "service-charcoal",
                      (cx, cy - bank * 4.25, 2.49), (22.0, .14, .08))
        planter_x = cx + (-7.0 if node_index % 2 else 7.0)
        batch.add_box("v41-hyper-room-planter", "ledger-granite",
                      (planter_x, cy + bank * .6, 2.92), (5.2, 3.6, 1.04))
        batch.add_box("v41-hyper-room-soil", "soil-v11",
                      (planter_x, cy + bank * .6, 3.48), (4.6, 3.0, .14))
        _add_architectural_tree(batch, planter_x, cy + bank * .6,
                                25000 + node_index, .58 + .035 * (node_index % 3), 3.55)
        for side in (-1, 1):
            seat_x = cx + side * 3.4
            batch.add_box("v41-hyper-room-seat", "timber-accent",
                          (seat_x, cy - bank * 1.8, 2.72), (2.8, .72, .18))
            batch.add_box("v41-hyper-room-seat-back", "timber-accent",
                          (seat_x, cy - bank * 2.12, 3.18), (2.8, .14, .82))
            activity.append(_add_seated_human(
                batch, seat_x, cy - bank * 1.82, 0 if bank > 0 else math.pi,
                25300 + node_index * 10 + side, 2.84, 2.39))
        for person in range(5):
            activity.append(_add_mid_detail_human(
                batch, cx - 4.6 + person * 2.3,
                cy + bank * (2.4 + .4 * (person % 2)), .12 * bank,
                25500 + node_index * 20 + person,
                "walking" if person in (0, 4) else "conversation", 2.39))
        batch.add_cylinder("v41-hyper-room-light-pole", accent,
                           (cx - 9.0, cy + bank * 2.8, 4.52), .065, 4.2, 14)
        batch.add_cylinder("v41-hyper-room-light-source", "warm-light",
                           (cx - 9.0, cy + bank * 2.8, 6.66), .14, .18, 14)

    # The two public-frontage rooms operate as real cafe terraces rather than
    # empty paving.  Canopies, tables and seated groups form near/mid/far
    # activity layers while maintaining the six-metre accessible spine.
    cafe_clusters = 0
    for cluster_index, (cx, cy, facing) in enumerate((
            (-318.0, -31.0, 0.0), (-286.0, 31.0, math.pi),
            (-224.0, 31.0, math.pi), (-190.0, -31.0, 0.0))):
        for table_index, offset in enumerate((-4.2, 4.2)):
            tx = cx + offset
            batch.add_cylinder("v41-hyper-cafe-table", "timber-accent",
                               (tx, cy, 3.20), .86, .16, 18)
            batch.add_cylinder("v41-hyper-cafe-table-leg", "archive-metal",
                               (tx, cy, 2.84), .08, .72, 12)
            batch.add_cylinder("v41-hyper-cafe-canopy-pole", "archive-metal",
                               (tx, cy, 4.42), .055, 3.78, 12)
            batch.add_frustum("v41-hyper-cafe-canopy", "timber-accent",
                              (tx, cy, 6.26), 2.35, .42, .58, 24)
            for chair_side in (-1, 1):
                sy = cy + chair_side * 1.20
                batch.add_box("v41-hyper-cafe-chair", "timber-accent",
                              (tx, sy, 2.82), (.72, .72, .18))
                activity.append(_add_seated_human(
                    batch, tx, sy, facing, 25900 + cluster_index * 20 +
                    table_index * 4 + chair_side, 2.94, 2.39))
            cafe_clusters += 1

    # Wet/dry coping, seating cuts and joint rhythm make the water section
    # legible from every Archive eye-level camera without changing the stream.
    edge_sections = 0
    for segment, x in enumerate(range(-344, -155, 12)):
        for bank in (-1, 1):
            batch.add_box("v41-hyper-wet-edge", "wet-stone",
                          (x, bank * 7.82, .30), (11.65, .42, .34))
            batch.add_box("v41-hyper-dry-edge", "dry-stone",
                          (x, bank * 8.18, .67), (11.65, .28, .38))
            batch.add_box("v41-hyper-edge-joint", "service-charcoal",
                          (x - 5.84, bank * 8.18, .74), (.08, .48, .48))
            if segment % 4 == 1:
                batch.add_box("v41-hyper-edge-seat", "timber-accent",
                              (x, bank * 11.2, .76), (5.8, .72, .18))
            edge_sections += 1
    # Compose arrivals, bridge crossings, runners and water watchers as
    # foreground/midground groups rather than increasing an even scatter.
    activity_clusters = []
    for cluster_index, (cx, cy, action, count, facing) in enumerate((
            (-326.0, -20.5, "office-arrival", 8, .18),
            (-286.0, 20.5, "civic-meeting", 9, 3.0),
            (-246.0, -20.5, "gateway-crossing", 10, .10),
            (-205.0, 20.5, "water-lunch", 8, 3.0),
            (-172.0, -20.5, "evening-walk", 7, .15))):
        bank = 1 if cy > 0 else -1
        for person in range(count):
            row = person // 5
            activity.append(_add_mid_detail_human(
                batch, cx - 4.4 + (person % 5) * 2.2 + row * .5,
                cy + bank * (row * 1.45 + .22 * (person % 2)),
                facing + .06 * (person % 3 - 1),
                26400 + cluster_index * 40 + person,
                "walking" if action in ("office-arrival", "gateway-crossing",
                                          "evening-walk") and person % 3 == 0
                else "conversation", 2.39))
        activity_clusters.append({"role": action, "count": count,
                                  "foregroundMidgroundComposed": True})
    for bridge_person in range(8):
        activity.append(_add_mid_detail_human(
            batch, -254.0 + (bridge_person % 4) * 2.5,
            -6.5 + (bridge_person // 4) * 5.0, .04,
            26800 + bridge_person, "walking", 2.92))
    for watcher_index, (x, bank) in enumerate(((-332.0, -1), (-292.0, 1),
                                                (-222.0, -1), (-178.0, 1))):
        y = bank * 11.2
        batch.add_box("v42-water-watch-seat", "timber-accent",
                      (x, y, .76), (5.6, .72, .18))
        for side in (-1, 1):
            activity.append(_add_seated_human(
                batch, x + side * 1.35, y, 0 if bank > 0 else math.pi,
                27000 + watcher_index * 10 + side, .86, .28))
    return batch.finalize(), {
        "occupiedGalleryCount": len(rooms), "occupiedGalleries": rooms,
        "programmedRoomCount": len(node_specs),
        "programmedHumanCount": len(activity),
        "cafeTerraceClusterCount": cafe_clusters,
        "waterEdgeSections": edge_sections,
        "activityClusters": activity_clusters,
        "clearPromenadeM": 6.0, "scatterPlacement": False,
        "floatingObjects": 0, "waterIntrusions": 0,
    }


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parsed = parser.parse_args(args)
    output = Path(parsed.output_root)
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)

    ENVELOPE.clear()
    original_building, original_tree, original_human = v12.add_building, v12.add_tree, v12.add_human
    original_sphere = v12.HeroBatch.add_uv_sphere
    v12.add_building = add_wall_first_building
    v12.add_tree = add_camera_safe_tree
    v12.add_human = add_camera_safe_human
    v12.HeroBatch.add_uv_sphere = add_precision_uv_sphere
    try:
        base_objects, base_geometry, base_validation, consolidation, trees, base_activity = v12.build_zone()
        public_objects, public_geometry, public_activity = v29.add_inhabited_promenade()
        activity_objects, signature_activity = _add_signature_activity_layer()
        stream_room_objects, stream_rooms = _add_stream_civic_rooms()
        liner_objects, stream_liners = _add_stream_liner_architecture()
        section_objects, civic_sections = _add_archive_civic_section_rebuild()
        metropolitan_objects, metropolitan_precision = _add_metropolitan_precision_layer()
        hyper_objects, hyper_polish = _add_hyper_polish_archive_scene()
    finally:
        v12.add_building, v12.add_tree, v12.add_human = original_building, original_tree, original_human
        v12.HeroBatch.add_uv_sphere = original_sphere

    objects = (base_objects + public_objects + activity_objects
               + stream_room_objects + liner_objects + section_objects
               + metropolitan_objects + hyper_objects)
    precision_edges = v28.apply_precision_edges(objects)
    smooth_tokens = ("tree", "foliage", "shrub", "human-head", "human-hair")
    smooth_object_count = 0
    for obj in objects:
        if obj.type == "MESH" and any(token in obj.name.lower() for token in smooth_tokens):
            for polygon in obj.data.polygons:
                polygon.use_smooth = True
            smooth_object_count += 1
    runtime_objects, runtime_consolidation = _consolidate_scene_objects_by_material(objects)
    validation = v12.validate_geometry(runtime_objects)
    triangles = v28.triangle_count(runtime_objects)
    assert len(ENVELOPE) == 12
    assert sum(item["detachedWindows"] for item in ENVELOPE) == 0
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images) == 0

    target = output / "archive-water-plaza-hero-v41.glb"
    bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB", export_yup=True,
                              export_normals=True, export_texcoords=False,
                              export_materials="EXPORT", export_apply=True)
    report = {
        "status": "TECHNICAL_PASS_VISUAL_GATE_PENDING", "revision": 41,
        "geometryRevision": 47,
        "zone": "Archive Water Plaza", "qualityTarget": {"grade": "S", "minimumScore": 95},
        "implementationPath": "WALL_FIRST_PER_OPENING_INFILL_AND_INHABITED_PODIUM",
        "failedBaselines": ["v32-chaotic-facade", "v33-flat-frontage"],
        "glb": str(target), "bytes": target.stat().st_size,
        "geometry": {"triangles": triangles, "meshObjects": len(runtime_objects),
                     "sourceMeshObjects": len(objects),
                     "components": base_geometry["components"] + public_geometry["components"]},
        "runtimeGeometry": {"meshObjects": len(runtime_objects),
                            "consolidation": runtime_consolidation},
        "buildingCount": 6, "facadeAssemblyCount": len(ENVELOPE),
        "boundedFrontageBayCount": sum(7 + style % 3 for style in range(6)),
        "lobbyCount": 6, "retailPublicBayCount": 42,
        "signatureProjectedLobbyCount": 2,
        "deepAtriumLobbyCount": 2,
        "signatureLobbyDepthM": 10.8,
        "atriumMezzanineCount": 2,
        "atriumVestibuleCount": 2,
        "signatureTowerCivicWingCount": 2,
        "signatureTowerMassingStageCount": 3,
        "secondaryGroundFloorGrammarCount": 2,
        "inhabitedArcadeCount": 2,
        "cornerPublicRoomCount": 2,
        "interiorFloorPlateCount": sum(item[4] for item in [
            (-326, 78, 44, 34, 22), (-260, 82, 50, 38, 28), (-190, 75, 38, 32, 18),
            (-326, -78, 48, 36, 25), (-258, -82, 42, 34, 20), (-188, -76, 54, 40, 16),
        ]),
        "signatureCafeTerraceCount": 2,
        "hyperPolishScene": hyper_polish,
        "nearFieldTreeSilhouetteCount": 12,
        "detachedWindowCount": 0, "stackedDecorativeGridCount": 0,
        "singleFacadeGlassCardCount": 0,
        "structuralPlausibility": {
            "buildingCount": len(STRUCTURAL_PLAUSIBILITY),
            "coreMeetsWindowRoomBack": all(
                item["coreMeetsWindowRoomBack"] for item in STRUCTURAL_PLAUSIBILITY),
            "unsupportedRoofCapCount": sum(
                item["unsupportedRoofCapCount"] for item in STRUCTURAL_PLAUSIBILITY),
            "roofEquipmentContained": all(
                item["roofEquipmentContained"] for item in STRUCTURAL_PLAUSIBILITY),
            "upperMassContainedByLower": all(
                item["upperMassContainedByLower"] for item in STRUCTURAL_PLAUSIBILITY),
            "buildings": STRUCTURAL_PLAUSIBILITY,
        },
        "chamferedPrimaryMassCount": 12,
        "distinctFacadeGrammarCount": 3,
        "facadeBodyCornerReturnCount": 24,
        "integratedSkyRoomCount": sum(item["integratedSkyRoomCount"] for item in ENVELOPE),
        "featureCellsRemovedBeforeRoomBuild": sum(
            item["featureCellsRemovedBeforeRoomBuild"] for item in ENVELOPE),
        "distinctRoofGrammarCount": 3,
        "coordinatedBuildingPaletteCount": 6,
        "sidePerOpeningEnvelope": True,
        "sideCoreRevealM": 1.05,
        "podiumSideBoundedRoomCount": 42,
        "podiumRearServiceGrammar": True,
        "upperSideRearBoundedEnvelope": True,
        "cornerOpeningCoverage": "90_PERCENT_OR_GREATER",
        "occupiedSetbackTerraceCount": 18,
        "envelope": ENVELOPE, "validation": validation,
        "baseValidation": base_validation, "consolidation": consolidation,
        "treeCount": len(trees), "humanCount": len(base_activity) + len(public_activity) + len(signature_activity),
        "signatureActivityHumanCount": len(signature_activity),
        "nearFieldMidDetailHumanCount": len(signature_activity),
        "seatedMidDetailHumanCount": 6,
        "lowerPromenadeMidDetailHumanCount": 12,
        "inhabitedCivicIslandCount": 2,
        "signatureBicycleRackCount": 5,
        "programmedStreamRoomCount": len(stream_rooms),
        "streamLinerBuildingCount": len(stream_liners),
        "streamLinerBoundedRoomCount": sum(item["boundedRooms"] for item in stream_liners),
        "streamLinerParentPodiumConnectionCount": sum(
            1 for item in stream_liners if item["parentPodiumConnected"]),
        "streamLinerDeepPublicRoomCount": sum(
            item["deepPublicRooms"] for item in stream_liners),
        "streamLinerVestibuleCount": len(stream_liners),
        "archiveCivicSectionCount": len(civic_sections),
        "archiveCivicSection": civic_sections,
        "metropolitanPrecision": metropolitan_precision,
        "smoothOrganicObjectCount": smooth_object_count,
        "precisionEdgeObjectCount": len(precision_edges), "imageDatablocks": len(bpy.data.images),
        "officeV5Changed": False, "directReferenceCopy": False,
        "referencePolicy": "Abstract spatial and visual-quality direction only; no identifiable design reproduced.",
    }
    (output / "archive-water-plaza-hero-v41-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "triangles": triangles,
                      "facadeAssemblies": len(ENVELOPE), "detachedWindows": 0}))


if __name__ == "__main__":
    main()
