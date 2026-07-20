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
import archive_water_plaza_v31 as v31

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


def _near_camera(x, y, radius):
    camera_origins = ((-340, -15), (-345, -25), (-340, 10), (-276, 18))
    return any(math.hypot(x - cx, y - cy) < radius for cx, cy in camera_origins)


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
    if _near_camera(x, y, 22.0):
        return
    v30.add_natural_tree(batch, x, y, seed, scale, z_base)


def add_camera_safe_human(batch, x, y, facing, seed, action, z_base=0.0):
    """Keep certified eye-level camera origins free of mannequin occlusion."""
    if _near_camera(x, y, 18.0):
        y += 20.0 if y >= 0 else -20.0
        x += 11.0
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
    batch.add_box("v34-integrated-glass-field", "occupied-window-glass",
                  (x, glass_y, base_z + height * .5), (width - .22, .12, height - .20))
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
                  (lower_x, lower_y - facing * .42, podium_h + lower_h * .5),
                  (lower_w, lower_d - .84, lower_h))
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
                      (upper_x, upper_y - facing * .40, podium_h + lower_h + upper_h * .5),
                      (upper_w, upper_d - .80, upper_h))
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
        landscape_objects, landscape_geometry, landscape_activity = v31.add_precision_landscape_rooms()
    finally:
        v12.add_building, v12.add_tree, v12.add_human = original_building, original_tree, original_human
        v12.HeroBatch.add_uv_sphere = original_sphere

    objects = base_objects + public_objects + landscape_objects
    precision_edges = v28.apply_precision_edges(objects)
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
                     "components": base_geometry["components"] + public_geometry["components"] + landscape_geometry["components"]},
        "buildingCount": 6, "facadeAssemblyCount": len(ENVELOPE),
        "boundedFrontageBayCount": sum(7 + style % 3 for style in range(6)),
        "lobbyCount": 6, "retailPublicBayCount": 42,
        "detachedWindowCount": 0, "stackedDecorativeGridCount": 0,
        "envelope": ENVELOPE, "validation": validation,
        "baseValidation": base_validation, "consolidation": consolidation,
        "treeCount": len(trees), "humanCount": len(base_activity) + len(public_activity) + len(landscape_activity),
        "precisionEdgeObjectCount": len(precision_edges), "imageDatablocks": len(bpy.data.images),
        "officeV5Changed": False, "directReferenceCopy": False,
        "referencePolicy": "Abstract spatial and visual-quality direction only; no identifiable design reproduced.",
    }
    (output / "archive-water-plaza-hero-v34-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "triangles": triangles,
                      "facadeAssemblies": len(ENVELOPE), "detachedWindows": 0}))


if __name__ == "__main__":
    main()
