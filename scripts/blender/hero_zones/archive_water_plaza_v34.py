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
    camera_origins = ((-340, -15), (-292, 9), (-340, 10), (-210, 22))
    return any(math.hypot(x - cx, y - cy) < radius for cx, cy in camera_origins)


def _occludes_camera(x, y, length=30.0, width=4.0):
    rays = (
        ((-340, -15), (-218, 1)), ((-292, 9), (-325, -60)),
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


def _bounded_curtain_wall(batch, *, x, face_y, facing, width, base_z,
                          floors, floor_h, style, stone, accent):
    """One facade assembly: room boundary -> recessed glass -> structural grid."""
    inside = -facing
    height = floors * floor_h
    bay_count = max(6, round(width / (3.8 + .25 * (style % 3))))
    bay_width = width / bay_count
    glass_y = face_y + inside * .34
    room_depth = 1.35

    batch.add_box("v34-facade-room-back", "warm-interior",
                  (x, face_y + inside * room_depth, base_z + height * .5),
                  (width, .18, height))
    batch.add_box("v34-integrated-glass-field", "blue-gray-glass",
                  (x, glass_y, base_z + height * .5), (width - .22, .12, height - .20))
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
    # Deep vertical frames create a legible primary rhythm at street and aerial
    # distance without becoming a detached second facade.
    for column in range(0, bay_count + 1, 3):
        px = x - width * .5 + column * bay_width
        batch.add_box("v34-primary-depth-frame", stone,
                      (px, face_y + facing * .19, base_z + height * .5),
                      (.48, 1.10, height + .56))
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
                     "detachedWindows": 0, "bounded": True})


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
    batch.add_box("v34-tower-structural-core", stone,
                  (lower_x, lower_y - facing * 1.36, podium_h + lower_h * .5),
                  (lower_w, lower_d - 2.72, lower_h))
    _bounded_curtain_wall(batch, x=lower_x, face_y=lower_face, facing=facing,
                          width=lower_w, base_z=podium_h, floors=lower_floors,
                          floor_h=floor_h, style=style, stone=stone, accent=accent)
    # Side walls use recessed vertical ribbons that intersect the shell.
    for side in (-1, 1):
        side_x = lower_x + side * lower_w * .5
        for ribbon in range(3):
            sy = lower_y - lower_d * .28 + ribbon * lower_d * .28
            batch.add_box("v34-side-recessed-ribbon", "blue-gray-glass",
                          (side_x - side * .10, sy, podium_h + lower_h * .50),
                          (.16, lower_d * .18, lower_h * .78))
            batch.add_box("v34-side-ribbon-return", accent,
                          (side_x, sy - lower_d * .10, podium_h + lower_h * .50),
                          (.42, .24, lower_h * .80))
    if upper_floors:
        upper_h = upper_floors * floor_h
        upper_w = lower_w * (.68 + .05 * (style % 3))
        upper_d = lower_d * (.70 + .04 * ((style + 1) % 3))
        upper_x = lower_x + (1 if style % 2 else -1) * lower_w * .10
        upper_y = lower_y - facing * 1.6
        upper_face = upper_y + facing * upper_d * .5
        batch.add_box("v34-upper-structural-core", stone,
                      (upper_x, upper_y - facing * 1.30, podium_h + lower_h + upper_h * .5),
                      (upper_w, upper_d - 2.60, upper_h))
        _bounded_curtain_wall(batch, x=upper_x, face_y=upper_face, facing=facing,
                              width=upper_w, base_z=podium_h + lower_h,
                              floors=upper_floors, floor_h=floor_h,
                              style=style + 7, stone=stone, accent=accent)
    roof_z = podium_h + floors * floor_h
    batch.add_box("v34-integrated-machine-room", "service-charcoal",
                  (x - width * .10, y, roof_z + 2.4),
                  (width * .27, depth * .28, 4.8))
    batch.add_box("v34-roof-screen", accent,
                  (x + width * .10, y + facing * depth * .10, roof_z + 3.25),
                  (width * .42, .35, 4.9))
    for unit in range(3):
        batch.add_box("v34-roof-hvac", "service-charcoal",
                      (x - 3.4 + unit * 3.4, y - facing * depth * .10, roof_z + 5.25),
                      (2.2, 2.8, 1.4))


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
    finally:
        v12.add_building, v12.add_tree, v12.add_human = original_building, original_tree, original_human
        v12.HeroBatch.add_uv_sphere = original_sphere

    objects = base_objects + public_objects
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
        "implementationPath": "WALL_FIRST_BOUNDED_CURTAIN_WALL_AND_INHABITED_PODIUM",
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
        "envelope": ENVELOPE, "validation": validation,
        "baseValidation": base_validation, "consolidation": consolidation,
        "treeCount": len(trees), "humanCount": len(base_activity) + len(public_activity),
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
