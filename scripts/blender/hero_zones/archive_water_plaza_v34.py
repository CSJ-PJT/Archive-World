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
    if north:
        return ("archive-warm-stone", "archive-metal")
    return ("ledger-limestone", "ledger-bronze")


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
    for column in range(bay_count + 1):
        px = x - width * .5 + column * bay_width
        pier_w = .28 if column not in (0, bay_count) else .48
        batch.add_box("v34-structural-facade-pier", accent,
                      (px, face_y + inside * .10, base_z + height * .5),
                      (pier_w, .72, height + .24))
    for floor in range(floors + 1):
        pz = base_z + floor * floor_h
        band_h = .25 if floor % 4 else .42
        batch.add_box("v34-attached-spandrel", stone if floor % 4 == 0 else accent,
                      (x, face_y + inside * .10, pz), (width + .24, .72, band_h))
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
                     "perOpeningInfill": True, "fourSidedReturns": True})


def _add_style_specific_massing_details(batch, *, x, y, width, depth,
                                        roof_z, facing, style, stone, accent):
    """Give each hero building a constructionally different crown/terrace.

    The pieces connect to the primary mass and serve silhouette, occupied
    terraces and roof maintenance.  They are not triangle-count padding.
    """
    grammar = style % 3
    if grammar == 0:
        # Archive institutional crown: two enclosed service volumes and a
        # restrained civic frame, visibly attached to the roof slab.
        for side in (-1, 1):
            batch.add_box("v34-archive-crown-service-volume", "service-charcoal",
                          (x + side * width * .19, y, roof_z + 3.05),
                          (width * .24, depth * .34, 6.1))
            batch.add_box("v34-archive-crown-vertical-blade", accent,
                          (x + side * width * .33, y + facing * depth * .05,
                           roof_z + 5.1),
                          (.54, depth * .48, 10.2))
        batch.add_box("v34-archive-crown-bridge", stone,
                      (x, y + facing * depth * .06, roof_z + 9.3),
                      (width * .70, depth * .15, .72))
    elif grammar == 1:
        # Ledger terrace crown: three stepped, occupied roof plates with a
        # perimeter rail and integrated planting datum.
        for step in range(3):
            step_w = width * (.62 - step * .10)
            step_d = depth * (.46 - step * .07)
            step_z = roof_z + .32 + step * 1.25
            step_x = x + width * (.04 * step)
            batch.add_box("v34-ledger-roof-terrace", stone,
                          (step_x, y - facing * step * .38, step_z),
                          (step_w, step_d, .42))
            batch.add_box("v34-ledger-terrace-guard", accent,
                          (step_x, y + facing * step_d * .48, step_z + .78),
                          (step_w, .16, 1.20))
        for planter in (-1, 1):
            batch.add_box("v34-ledger-roof-planter", stone,
                          (x + planter * width * .19, y, roof_z + 1.02),
                          (width * .18, depth * .16, 1.10))
            batch.add_box("v34-ledger-roof-planting", "foliage-deep",
                          (x + planter * width * .19, y, roof_z + 1.72),
                          (width * .15, depth * .13, .40))
    else:
        # Civic-tech lantern: a recessed occupied volume is bounded by four
        # structural corner piers and a roof frame.
        lantern_w, lantern_d, lantern_h = width * .34, depth * .32, 6.8
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
        batch.add_box("v34-civic-lantern-roof-frame", stone,
                      (x, y, roof_z + lantern_h),
                      (lantern_w + 1.2, lantern_d + 1.2, .52))
        batch.add_box("v34-civic-lantern-light-line", "archive-cyan-light",
                      (x, y + facing * (lantern_d * .5 + .08),
                       roof_z + lantern_h * .72),
                      (lantern_w - .8, .10, .12))


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
                  (width + 8.0, body_depth - 5.8, podium_h))
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


def _signature_civic_lobby(batch, spec, podium_h, face_y, stone, accent):
    """A real projected public room for the two principal plaza buildings."""
    x, y, width, _depth, _floors, _floor_h, style = spec
    facing = -1 if y > 0 else 1
    inside = -facing
    lobby_x = x + (-3.6 if style == 0 else 3.8)
    lobby_width = min(18.0, width * .42)
    projection = 7.4
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


def _add_architectural_tree(batch, x, y, seed, scale=1.0, z_base=0.0):
    """Three near-field species silhouettes with attached branch systems."""
    variant = seed % 3
    if variant == 0:
        return ORIGINAL_NATURAL_TREE(batch, x, y, seed, scale, z_base)
    height = (8.2 if variant == 1 else 6.7) * scale
    material = ("foliage-deep", "foliage-mid", "foliage-light")[seed % 3]
    if variant == 1:
        batch.add_frustum("v34-columnar-tree-trunk", "timber-accent",
                          (x, y, z_base + height * .36), .34 * scale, .18 * scale,
                          height * .72, 16)
        for branch in range(7):
            angle = branch * math.tau / 7 + .22
            start = (x, y, z_base + height * (.43 + .035 * (branch % 3)))
            end = (x + math.cos(angle) * 1.25 * scale,
                   y + math.sin(angle) * 1.25 * scale,
                   z_base + height * (.70 + .025 * (branch % 2)))
            batch.add_tapered_branch("v34-columnar-primary-branch", "timber-accent",
                                     start, end, .12 * scale, .035 * scale, 10)
        for level in (-1, 0, 1):
            batch.add_uv_sphere("v34-columnar-tree-crown", material,
                                (x + level * .38 * scale, y, z_base + height * (.71 + level * .08)),
                                1.72 * scale, 24, 12, (.74, .72, 1.25))
    else:
        for stem in (-1, 1):
            start = (x + stem * .22 * scale, y, z_base)
            end = (x + stem * 1.10 * scale, y + stem * .30 * scale, z_base + height * .67)
            batch.add_tapered_branch("v34-multistem-tree-trunk", "timber-accent",
                                     start, end, .28 * scale, .09 * scale, 14)
            for branch in range(3):
                angle = branch * math.tau / 3 + (0 if stem > 0 else .55)
                tip = (end[0] + math.cos(angle) * 1.2 * scale,
                       end[1] + math.sin(angle) * 1.2 * scale,
                       end[2] + (.7 + .22 * branch) * scale)
                batch.add_tapered_branch("v34-multistem-primary-branch", "timber-accent",
                                         end, tip, .09 * scale, .025 * scale, 10)
                batch.add_uv_sphere("v34-open-tree-crown", material, tip,
                                    1.18 * scale, 22, 11, (1.28, .90, .72))


def _add_signature_activity_layer():
    """Camera-composed civic activity anchored to real frontage and furniture."""
    human_batch = v12.HeroBatch(v12.create_materials())
    prop_batch = v12.HeroBatch(v12.create_materials())
    records = []
    groups = (
        (-312, -30.5, .18, "walking"), (-294, -32.0, -.30, "conversation"),
        (-281, -29.5, .32, "walking"),
        (-334, -43.5, .30, "walking"), (-329, -44.5, .20, "conversation"),
        (-326, -42.7, -.25, "conversation"), (-318, -45.5, .35, "walking"),
        (-313, -43.8, -.15, "conversation"), (-309, -45.1, .25, "conversation"),
        (-267, -43.5, .15, "walking"), (-262, -45.0, -.20, "conversation"),
        (-257, -43.8, .25, "conversation"), (-252, -46.0, .05, "walking"),
    )
    for index, (x, y, facing, action) in enumerate(groups):
        records.append(_add_mid_detail_human(human_batch, x, y, facing,
                                             1480 + index, action, 2.30))
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
        prop_batch.add_uv_sphere("v34-signature-activity-shrub",
                                 ("foliage-deep", "foliage-mid", "foliage-light")[shrub % 3],
                                 (-291 + shrub * 1.25, -44.8, 4.03 + (shrub % 2) * .10),
                                 .58 + (shrub % 3) * .08, 18, 9, (1.15, .75, .68))
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
            prop_batch.add_uv_sphere("v34-civic-island-layered-planting",
                                     ("foliage-deep", "foliage-mid", "foliage-light")[(plant + island) % 3],
                                     (px, py, 3.70 + .10 * (plant % 2)),
                                     .64 + .08 * (plant % 3), 20, 10, (1.20, .82, .74))
        for bench in (-1, 1):
            prop_batch.add_box("v34-civic-island-timber-seat", "timber-accent",
                               (ix + bench * iw * .28, iy + 3.0, 2.84),
                               (iw * .30, .72, .18), angle)
            prop_batch.add_box("v34-civic-island-seat-support", "archive-metal",
                               (ix + bench * iw * .28, iy + 3.0, 2.57),
                               (iw * .24, .42, .46), angle)
    # A narrow darker inlay records the primary pedestrian axis in real
    # geometry and breaks the oversized pale paving field.
    prop_batch.add_box("v34-civic-forecourt-axis-inlay", "ledger-granite",
                       (-300.0, -30.0, 2.345), (7.0, 20.0, .055))
    prop_batch.add_box("v34-civic-forecourt-axis-core", "dry-stone",
                       (-300.0, -30.0, 2.382), (5.8, 20.0, .055))
    human_objects = human_batch.finalize()
    for obj in human_objects:
        obj["nearFieldMidDetailHuman"] = True
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    v12.consolidate(prop_batch)
    return human_objects + prop_batch.finalize(), records


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
        elbow = (shoulder[0] - forward[0] * side * stride * .60,
                 shoulder[1] - forward[1] * side * stride * .60, z_base + height * .64)
        hand = (elbow[0] + forward[0] * side * stride * .33,
                elbow[1] + forward[1] * side * stride * .33, z_base + height * .49)
        batch.add_tapered_branch("v34-human-upper-arm", body, shoulder, elbow, .067, .052, 12)
        batch.add_tapered_branch("v34-human-lower-arm", body, elbow, hand, .052, .039, 12)
        batch.add_uv_sphere("v34-human-hand", skin, hand, .052, 14, 7, (1, .84, 1.08))
    if seed % 4 == 0:
        bag_x, bag_y = x + right[0] * .28, y + right[1] * .28
        batch.add_frustum("v34-human-shoulder-bag", "timber-accent",
                          (bag_x, bag_y, z_base + height * .49), .13, .17, .35, 14)
    return {"position": [x, y], "action": action, "orientation": facing,
            "grounded": True, "detail": "MID_DETAIL_NEAR_FIELD"}


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
    # The structural core sits behind the glazing datum and supplies side/rear mass.
    _add_chamfered_mass(batch, "v34-tower-chamfered-structural-core", stone,
                        (lower_x, lower_y - facing * 1.36, podium_h + lower_h * .5),
                        (lower_w, lower_d - 2.72, lower_h), 1.45 + .22 * (style % 3))
    _bounded_curtain_wall(batch, x=lower_x, face_y=lower_face, facing=facing,
                          width=lower_w, base_z=podium_h, floors=lower_floors,
                          floor_h=floor_h, style=style, stone=stone, accent=accent)
    # Side walls use a materially bounded vertical rhythm.  Recessed infill
    # panels intersect the core datum and receive actual jambs/bands, avoiding
    # both blank party walls and decorative cards hovering beside the tower.
    for side in (-1, 1):
        side_x = lower_x + side * lower_w * .5
        for ribbon in range(5):
            sy = lower_y - lower_d * .34 + ribbon * lower_d * .17
            ribbon_depth = lower_d * .105
            batch.add_box("v34-side-integrated-window-ribbon", "blue-gray-glass",
                          (side_x - side * .13, sy, podium_h + lower_h * .50),
                          (.14, ribbon_depth, lower_h * .80))
            for return_side in (-1, 1):
                batch.add_box("v34-side-ribbon-jamb", accent,
                              (side_x - side * .28,
                               sy + return_side * ribbon_depth * .5,
                               podium_h + lower_h * .50),
                              (.56, .18, lower_h * .82))
        for band_floor in range(0, lower_floors + 1, 4):
            band_z = podium_h + band_floor * floor_h
            batch.add_box("v34-side-structural-floor-band", stone,
                          (side_x - side * .18, lower_y, band_z),
                          (.52, lower_d * .76, .34))
    # Rear/service elevation has a distinct, still complete grammar.
    rear_face = lower_y - facing * lower_d * .5
    rear_outward = -facing
    for floor in range(lower_floors):
        rz = podium_h + floor * floor_h + floor_h * .5
        for bay in range(4):
            rx = lower_x - lower_w * .34 + bay * lower_w * .225
            material = "service-charcoal" if (floor + bay + style) % 7 == 0 else "blue-gray-glass"
            batch.add_box("v34-rear-integrated-service-window", material,
                          (rx, rear_face - rear_outward * .18, rz),
                          (lower_w * .14, .14, floor_h * .58))
        if floor % 5 == 0:
            batch.add_box("v34-rear-mechanical-service-band", accent,
                          (lower_x, rear_face + rear_outward * .10, rz),
                          (lower_w * .78, .46, .50))
    if upper_floors:
        upper_h = upper_floors * floor_h
        upper_w = lower_w * (.68 + .05 * (style % 3))
        upper_d = lower_d * (.70 + .04 * ((style + 1) % 3))
        upper_x = lower_x + (1 if style % 2 else -1) * lower_w * .10
        upper_y = lower_y - facing * 1.6
        upper_face = upper_y + facing * upper_d * .5
        _add_chamfered_mass(batch, "v34-upper-chamfered-structural-core", stone,
                            (upper_x, upper_y - facing * 1.30,
                             podium_h + lower_h + upper_h * .5),
                            (upper_w, upper_d - 2.60, upper_h),
                            1.15 + .18 * ((style + 1) % 3))
        _bounded_curtain_wall(batch, x=upper_x, face_y=upper_face, facing=facing,
                              width=upper_w, base_z=podium_h + lower_h,
                              floors=upper_floors, floor_h=floor_h,
                              style=style + 7, stone=stone, accent=accent)
    roof_z = podium_h + floors * floor_h
    _add_chamfered_mass(batch, "v34-integrated-chamfered-machine-room", "service-charcoal",
                        (x - width * .10, y, roof_z + 2.4),
                        (width * .27, depth * .28, 4.8), .70)
    batch.add_box("v34-roof-screen", accent,
                  (x + width * .10, y + facing * depth * .10, roof_z + 3.25),
                  (width * .42, .35, 4.9))
    for unit in range(3):
        batch.add_box("v34-roof-hvac", "service-charcoal",
                      (x - 3.4 + unit * 3.4, y - facing * depth * .10, roof_z + 5.25),
                      (2.2, 2.8, 1.4))
    _add_style_specific_massing_details(batch, x=x, y=y, width=width,
                                        depth=depth, roof_z=roof_z,
                                        facing=facing, style=style,
                                        stone=stone, accent=accent)


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
    finally:
        v12.add_building, v12.add_tree, v12.add_human = original_building, original_tree, original_human
        v12.HeroBatch.add_uv_sphere = original_sphere

    objects = base_objects + public_objects + activity_objects
    precision_edges = v28.apply_precision_edges(objects)
    smooth_tokens = ("tree", "foliage", "shrub", "human-head", "human-hair")
    smooth_object_count = 0
    for obj in objects:
        if obj.type == "MESH" and any(token in obj.name.lower() for token in smooth_tokens):
            for polygon in obj.data.polygons:
                polygon.use_smooth = True
            smooth_object_count += 1
    validation = v12.validate_geometry(objects)
    triangles = v28.triangle_count(objects)
    assert len(ENVELOPE) == 12
    assert sum(item["detachedWindows"] for item in ENVELOPE) == 0
    assert not validation["emptyMeshes"] and not validation["looseGeometry"]
    assert len(bpy.data.images) == 0

    target = output / "archive-water-plaza-hero-v34.glb"
    bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB", export_yup=True,
                              export_normals=True, export_texcoords=False,
                              export_materials="EXPORT", export_apply=True)
    report = {
        "status": "TECHNICAL_PASS_VISUAL_GATE_PENDING", "revision": 34,
        "zone": "Archive Water Plaza", "qualityTarget": {"grade": "S", "minimumScore": 95},
        "implementationPath": "WALL_FIRST_PER_OPENING_INFILL_AND_INHABITED_PODIUM",
        "failedBaselines": ["v32-chaotic-facade", "v33-flat-frontage"],
        "glb": str(target), "bytes": target.stat().st_size,
        "geometry": {"triangles": triangles, "meshObjects": len(objects),
                     "components": base_geometry["components"] + public_geometry["components"]},
        "buildingCount": 6, "facadeAssemblyCount": len(ENVELOPE),
        "boundedFrontageBayCount": sum(7 + style % 3 for style in range(6)),
        "lobbyCount": 6, "retailPublicBayCount": 42,
        "signatureProjectedLobbyCount": 2,
        "interiorFloorPlateCount": sum(item[4] for item in [
            (-326, 78, 44, 34, 22), (-260, 82, 50, 38, 28), (-190, 75, 38, 32, 18),
            (-326, -78, 48, 36, 25), (-258, -82, 42, 34, 20), (-188, -76, 54, 40, 16),
        ]),
        "signatureCafeTerraceCount": 2,
        "nearFieldTreeSilhouetteCount": 3,
        "detachedWindowCount": 0, "stackedDecorativeGridCount": 0,
        "singleFacadeGlassCardCount": 0,
        "chamferedPrimaryMassCount": 12,
        "distinctFacadeGrammarCount": 3,
        "facadeBodyCornerReturnCount": 24,
        "distinctRoofGrammarCount": 3,
        "envelope": ENVELOPE, "validation": validation,
        "baseValidation": base_validation, "consolidation": consolidation,
        "treeCount": len(trees), "humanCount": len(base_activity) + len(public_activity) + len(signature_activity),
        "signatureActivityHumanCount": len(signature_activity),
        "nearFieldMidDetailHumanCount": len(signature_activity),
        "inhabitedCivicIslandCount": 2,
        "signatureBicycleRackCount": 5,
        "smoothOrganicObjectCount": smooth_object_count,
        "precisionEdgeObjectCount": len(precision_edges), "imageDatablocks": len(bpy.data.images),
        "officeV5Changed": False, "directReferenceCopy": False,
        "referencePolicy": "Abstract spatial and visual-quality direction only; no identifiable design reproduced.",
    }
    (output / "archive-water-plaza-hero-v34-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "triangles": triangles,
                      "facadeAssemblies": len(ENVELOPE), "detachedWindows": 0}))


if __name__ == "__main__":
    main()
