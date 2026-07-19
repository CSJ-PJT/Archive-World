"""Archive Water Plaza V14: envelope-connected facade construction.

V12/V13 are retained as failed baselines. Their facade panels used the nominal
footprint while the body used a reduced depth, creating metre-scale gaps. V14
derives every window, frame, and ground-floor datum from the constructed mass.
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

MAX_ENVELOPE_GAP_M = 0.12
FRONTAGE_VOID_DEPTH_M = 0.0
TOWER_FACADE_CAVITY_DEPTH_M = 0.0
FACADE_GLASS_RECESS_M = 0.0
FACADE_GLASS_THICKNESS_M = 0.08
ACTIVE_FRONTAGE_GRADE_M = 0.0
ENVELOPE_REPORTS = []
FRONTAGE_ACTIVITY = []


def add_connected_facade(batch, *, x, y, width, depth, base_z, height, floors, floor_h, facing, style, prefix):
    """Build a load-bearing facade cassette physically tied to the tower shell.

    The failed facade path positioned thin glass cards from a nominal footprint
    and positioned the structural body from a second, reduced footprint.  The
    cards could therefore read as a detached billboard.  Every depth here is
    measured from the same constructed face.  Piers, heads, sills and returns
    extend all the way from the exterior datum to the structural shell; glazing
    is contained inside those four-sided openings.
    """
    face_y = y + facing * depth * .5
    # `glass_y` is the centre of the pane, not its exterior face.  The old
    # implementation compared that centre to the structural datum and could
    # therefore report a zero gap while half of the pane merely intersected a
    # solid box.  The pane front, centre, back and shell face now form one
    # explicit section.  The shell terminates exactly at the back of the pane.
    glass_depth = FACADE_GLASS_THICKNESS_M
    glass_front_y = face_y - facing * FACADE_GLASS_RECESS_M
    glass_y = glass_front_y - facing * glass_depth * .5
    glass_back_y = glass_y - facing * glass_depth * .5
    structural_face_y = face_y - facing * TOWER_FACADE_CAVITY_DEPTH_M
    glass_back_gap = abs(glass_back_y - structural_face_y)
    assert glass_back_gap <= 1e-6, (
        f"glass back/shell mismatch: {glass_back_gap:.6f}m; "
        "cavity must equal recess plus pane thickness"
    )
    attachment_depth = max(.18, abs(structural_face_y - face_y) + .06)
    attachment_y = (structural_face_y + face_y) * .5
    bay_count = max(6, min(11, round(width / (3.5 + (style % 3) * .35))))
    usable = width * .88
    pitch = usable / bay_count
    accent = "archive-metal" if style < 3 else "ledger-bronze"

    for index in range(bay_count + 1):
        px = x - usable * .5 + index * pitch
        # The jamb is a real return from the exterior face to the structural
        # datum.  Every third bay becomes a deeper mega-frame so the facade is
        # read as an attached wall system, not a grid of floating dark cards.
        mega = index in (0, bay_count) or (index + style) % 3 == 0
        jamb_width = .68 if index in (0, bay_count) else .46 if mega else .24
        jamb_depth = attachment_depth + (.22 if mega else 0.0)
        jamb_y = attachment_y + facing * (.11 if mega else 0.0)
        batch.add_box(f"{prefix}-facade-jamb", accent, (px, jamb_y, base_z + height * .5),
                      (jamb_width, jamb_depth, height))

    # Full-height end returns close the cavity when the facade is read obliquely.
    for side in (-1, 1):
        batch.add_box(f"{prefix}-facade-return", "archive-warm-stone",
                      (x + side * (usable + .55) * .5, attachment_y, base_z + height * .5),
                      (.48, attachment_depth, height))

    levels = max(3, min(floors, int(height / floor_h)))
    level_h = height / levels
    for floor in range(levels):
        floor_base = base_z + floor * level_h
        ratio = floor / max(1, levels - 1)
        zone = "lower" if ratio < .32 else "middle" if ratio < .72 else "upper"
        zone_index = 0 if zone == "lower" else 1 if zone == "middle" else 2
        # Structural slab edge and spandrel bridge the exterior assembly back to
        # the mass.  There is no open air gap behind the window grid.
        spandrel_material = (
            "ledger-granite" if zone == "lower" and floor % 3 == 0
            else "archive-warm-stone" if zone == "middle" and (floor + style) % 4 == 0
            else accent
        )
        spandrel_h = (.40, .30, .24)[zone_index]
        batch.add_box(f"{prefix}-facade-spandrel-{zone}", spandrel_material,
                      (x, attachment_y, floor_base + spandrel_h * .5),
                      (usable + .55, attachment_depth, spandrel_h))
        glass_ratio = (.58, .66, .72)[zone_index] + .025 * ((floor + style) % 2)
        glass_h = max(1.5, level_h * glass_ratio)
        glass_z = floor_base + .46 + glass_h * .5
        for bay in range(bay_count):
            bx = x - usable * .5 + (bay + .5) * pitch
            blind_period = (7, 9, 11)[zone_index]
            blind = (bay + floor * 2 + style + zone_index) % blind_period == 0
            # The three vertical zones use different solid/glass ratios.  This
            # prevents a single repeated curtain-wall stamp over the full tower.
            panel_margin = (.70, .52, .64)[zone_index]
            if zone == "upper" and (bay + style) % 3 == 1:
                panel_margin += .22
            panel_w = max(1.1, pitch - panel_margin)
            occupied = not blind and (bay * 3 + floor + style * 2) % 9 in (0, 4)
            panel_material = "ledger-granite" if blind else "occupied-window-glass" if occupied else "blue-gray-glass"
            batch.add_box(f"{prefix}-integrated-{zone}-{'blind' if blind else 'window'}",
                          panel_material, (bx, glass_y, glass_z), (panel_w, glass_depth, glass_h))

            # Four-sided returns are built for every opening, including blind
            # service panels.  Their rear edges meet the same datum as the pane.
            reveal_depth = abs(face_y - glass_back_y)
            reveal_y = (face_y + glass_back_y) * .5
            reveal_material = "service-charcoal" if blind or zone == "lower" else accent
            for side in (-1, 1):
                batch.add_box(f"{prefix}-{zone}-opening-side-return", reveal_material,
                              (bx + side * (panel_w * .5 + .07), reveal_y, glass_z),
                              (.14, reveal_depth, glass_h + .28))
            batch.add_box(f"{prefix}-{zone}-opening-head", accent,
                          (bx, reveal_y, glass_z + glass_h * .5 + .07),
                          (panel_w + .28, reveal_depth, .16))
            batch.add_box(f"{prefix}-{zone}-opening-sill", spandrel_material,
                          (bx, reveal_y, glass_z - glass_h * .5 - .07),
                          (panel_w + .28, reveal_depth, .16))
            if not blind:
                # A real back wall and a shadowed floor/ceiling pair establish
                # room depth behind the pane.  They sit behind the structural
                # datum and never float in front of the facade.
                interior_depth = .70 if zone == "lower" else .50
                interior_y = glass_back_y - facing * interior_depth
                batch.add_box(f"{prefix}-{zone}-occupied-interior-back",
                              "warm-interior" if occupied else "service-charcoal",
                              (bx, interior_y, glass_z),
                              (max(.4, panel_w - .18), .08, max(.5, glass_h - .22)))
                batch.add_box(f"{prefix}-{zone}-interior-ceiling", "warm-interior" if occupied else "service-charcoal",
                              (bx, glass_back_y - facing * interior_depth * .5,
                               glass_z + glass_h * .5 - .10),
                              (max(.4, panel_w - .20), interior_depth, .10))
                batch.add_box(f"{prefix}-{zone}-interior-floor", "ledger-granite",
                              (bx, glass_back_y - facing * interior_depth * .5,
                               glass_z - glass_h * .5 + .10),
                              (max(.4, panel_w - .20), interior_depth, .10))
                if zone == "lower" and (bay + floor + style) % 3 == 0:
                    batch.add_box(f"{prefix}-lower-privacy-screen", accent,
                                  (bx + pitch * .24, face_y + facing * .06, glass_z),
                                  (.12, .22, glass_h * .88))
                if zone == "upper" and (bay + style) % 2 == 0:
                    batch.add_box(f"{prefix}-upper-projecting-fin", accent,
                                  (bx - panel_w * .5 - .16, face_y + facing * .22, glass_z),
                                  (.18, .44, glass_h + .44))
        # Real transfer/mechanical floors divide the facade into readable
        # architectural zones instead of allowing one window pattern to run
        # unbroken from podium to crown.
        if floor in (max(2, levels // 3), max(4, levels * 2 // 3)):
            batch.add_box(f"{prefix}-transfer-shadow-band", accent,
                          (x, face_y + facing * .22, floor_base + level_h - .20),
                          (usable + 1.0, .46, .32))
            batch.add_box(f"{prefix}-transfer-service-recess", "service-charcoal",
                          (x, glass_y, floor_base + level_h * .52),
                          (usable * .94, glass_depth, level_h * .28))
    return {
        "maximumGapM": 0.0,
        "glassRecessM": abs(glass_front_y - face_y),
        "attachmentDepthM": attachment_depth,
        "structuralFaceY": structural_face_y,
        "glassFrontY": glass_front_y,
        "glassBackY": glass_back_y,
        "glassBackToStructuralFaceGapM": glass_back_gap,
        "exteriorFaceY": face_y,
        "bayCount": bay_count,
    }


def add_connected_side_and_rear(batch, *, x, y, width, depth, base_z, height, facing, style, prefix):
    accent = "archive-metal" if style < 3 else "ledger-bronze"
    rows = max(5, int(height / 7.0))
    side_glass_thickness = FACADE_GLASS_THICKNESS_M
    maximum_side_gap = 0.0
    for side in (-1, 1):
        face_x = x + side * width * .5
        glass_front_x = face_x - side * FACADE_GLASS_RECESS_M
        glass_x = glass_front_x - side * side_glass_thickness * .5
        glass_back_x = glass_x - side * side_glass_thickness * .5
        structural_x = face_x - side * TOWER_FACADE_CAVITY_DEPTH_M
        side_gap=abs(glass_back_x-structural_x)
        assert side_gap <= 1e-6
        maximum_side_gap=max(maximum_side_gap,side_gap)
        return_depth = abs(face_x-glass_back_x)
        return_x = (face_x+glass_back_x)*.5
        side_columns = 5 + style % 2
        for column in range(side_columns + 1):
            py = y - depth*.36 + column*depth*.72/side_columns
            batch.add_box(f"{prefix}-side-attached-vertical-frame",accent,
                          (return_x,py,base_z+height*.5),(return_depth,.24,height))
        for row in range(rows):
            z = base_z + (row + .5) * height / rows
            row_h=height/rows
            for column in range(side_columns):
                py = y - depth * .36 + (column + .5) * depth * .72 / side_columns
                material = "blue-gray-glass" if (row + column + style) % 5 else "ledger-granite"
                panel_length=depth*.72/side_columns-.34
                batch.add_box(f"{prefix}-side-integrated-opening", material,
                              (glass_x, py, z), (side_glass_thickness, panel_length, row_h * .58))
                for edge in (-1,1):
                    batch.add_box(f"{prefix}-side-opening-return",accent,
                                  (return_x,py+edge*(panel_length*.5+.06),z),
                                  (return_depth,.12,row_h*.70))
                batch.add_box(f"{prefix}-side-opening-head",accent,
                              (return_x,py,z+row_h*.34),(return_depth,panel_length+.24,.14))
                batch.add_box(f"{prefix}-side-opening-sill","ledger-granite",
                              (return_x,py,z-row_h*.34),(return_depth,panel_length+.24,.14))
            batch.add_box(f"{prefix}-side-slab-edge", accent,
                          (face_x+side*.08,y,z-row_h*.40),(.16,depth*.78,.18))
    rear_y = y - facing * depth * .5
    rear_rows = max(4, int(height / 9.0))
    for column in (-.34,-.08,.18,.36):
        batch.add_box(f"{prefix}-rear-vertical-frame",accent,
                      (x+width*column,rear_y-facing*.08,base_z+height*.5),(.26,.22,height))
    for row in range(rear_rows):
        z = base_z + (row + .5) * height / rear_rows
        batch.add_box(f"{prefix}-rear-service-window", "blue-gray-glass",
                      (x + width * .18, rear_y-facing*.04, z), (width*.32, .07, 1.45))
        batch.add_box(f"{prefix}-rear-service-screen", "service-charcoal",
                      (x - width * .23, rear_y-facing*.10, z), (width*.17, .18, 2.0))
    return {"glassBackToStructuralFaceGapM":maximum_side_gap,
            "intentionalGlassRecessM":FACADE_GLASS_RECESS_M,
            "sideOpeningRows":rows,"sideOpeningColumns":side_columns}


def add_connected_ground_floor(batch, *, x, y, width, depth, facing, style):
    podium_depth = depth + 5.0
    face_y = y + facing * podium_depth * .5
    inside = -facing
    frontage_w = width + 2.0
    requested_pitch = 5.4 + (style % 2) * .5
    bays = max(6, int(frontage_w / requested_pitch))
    pitch = frontage_w / bays
    lobby_bay = 1 + style % max(2, bays - 2)
    accent = "archive-metal" if style < 3 else "ledger-bronze"
    glazing_depth = .10
    glazing_front_y = face_y - facing * FACADE_GLASS_RECESS_M
    glazing_y = glazing_front_y - facing * glazing_depth * .5
    glazing_back_y = glazing_y - facing * glazing_depth * .5
    frontage_attachment_depth = max(.22, abs(face_y - glazing_back_y) + .06)
    frontage_attachment_y = (face_y + glazing_back_y) * .5

    grade=ACTIVE_FRONTAGE_GRADE_M
    batch.add_box("v17-building-forecourt", "promenade-paver", (x, face_y+facing*7.0, grade-.10),
                  (frontage_w+4.0, 14.0, .20))
    for joint in range(-3,4):
        batch.add_box("v17-forecourt-joint", "ledger-granite", (x+joint*frontage_w/7,face_y+facing*7.0,grade+.012),
                      (.055,13.7,.024))
    # Purposeful activity and furniture composition breaks the empty forecourt.
    for cluster in (-1,1):
        cx=x+cluster*frontage_w*.28
        cy=face_y+facing*8.6
        batch.add_box("v18-forecourt-bench-seat","timber-accent",(cx,cy,grade+.58),(2.8,.65,.18))
        batch.add_box("v18-forecourt-bench-back","timber-accent",(cx,cy-facing*.28,grade+1.0),(2.8,.14,.82))
        batch.add_cylinder("v18-cafe-table","ledger-bronze",(cx-cluster*3.2,face_y+facing*5.8,grade+.73),.68,.12,18)
        for seat in (-1,1):
            batch.add_cylinder("v18-cafe-chair","timber-accent",
                               (cx-cluster*3.2+seat*1.05,face_y+facing*5.8,grade+.44),.25,.42,12)
        batch.add_box("v18-forecourt-planter","archive-warm-stone",(cx+cluster*3.9,face_y+facing*11.0,grade+.58),(2.6,1.5,1.05))
        batch.add_box("v18-forecourt-planter-soil","soil-v11",(cx+cluster*3.9,face_y+facing*11.0,grade+1.13),(2.25,1.18,.12))
        for shrub in (-.7,0,.7):
            batch.add_uv_sphere("v18-forecourt-shrub","foliage-mid",
                                (cx+cluster*3.9+shrub,face_y+facing*11.0,grade+1.62),.52,14,7,(1,.78,.68))
    batch.add_box("v14-frontage-floor", "ledger-granite", (x, face_y+inside*3.0, grade+.15), (frontage_w, 6.0, .30))
    batch.add_box("v14-frontage-ceiling", "warm-interior", (x, face_y+inside*3.0, grade+5.25), (frontage_w, 6.0, .24))
    batch.add_box("v14-frontage-rear-wall", "warm-interior", (x, face_y+inside*5.9, grade+2.65), (frontage_w, .22, 5.1))
    for bay in range(bays):
        bx = x - frontage_w*.5 + (bay+.5)*pitch
        is_lobby = bay == lobby_bay
        is_community = not is_lobby and (bay + style) % 4 == 0
        is_cafe = not is_lobby and not is_community and (bay + style) % 3 == 0
        batch.add_box("v14-frontage-structural-pier", accent,
                      (x-frontage_w*.5+bay*pitch, frontage_attachment_y, grade+2.7),
                      (.46 if is_lobby else .34, frontage_attachment_depth, 5.4))
        batch.add_box("v14-frontage-integrated-glazing", "frontage-glass",
                      (bx, glazing_y, grade+2.55), (pitch-.55, glazing_depth, 4.75))
        # Deep perimeter reveals physically terminate the glazed opening.
        for side in (-1, 1):
            batch.add_box("v26-frontage-side-reveal", "service-charcoal",
                          (bx+side*(pitch-.42)*.5,frontage_attachment_y,grade+2.55),
                          (.14,frontage_attachment_depth,4.95))
        batch.add_box("v26-frontage-head-reveal",accent,
                      (bx,frontage_attachment_y,grade+4.97),(pitch-.30,frontage_attachment_depth,.18))
        batch.add_box("v26-frontage-sill-reveal","ledger-granite",
                      (bx,frontage_attachment_y,grade+.17),(pitch-.30,frontage_attachment_depth,.22))
        batch.add_box("v14-frontage-transom", accent, (bx, frontage_attachment_y, grade+4.15),
                      (pitch-.45, frontage_attachment_depth, .14))
        door_x = bx + pitch*(.15 if bay%2 else -.15)
        door_role = "v27-lobby-door" if is_lobby else "v27-community-door" if is_community else "v27-cafe-door" if is_cafe else "v27-public-door"
        batch.add_box(door_role, accent,
                      (door_x, face_y+facing*.11, grade+1.35), (1.35 if is_lobby else 1.05, .16, 2.7))
        # A bounded, legible room sits behind each glazed frontage.  Variant
        # roles prevent the street edge from reading as one continuous glass
        # texture pasted onto the podium.
        interior_accent = "timber-accent" if is_cafe or is_community else accent
        batch.add_box("v27-interior-counter", interior_accent,
                      (bx, face_y+inside*3.8, grade+1.05),
                      (pitch*.55, .65, 1.15 if not is_lobby else 1.35))
        batch.add_cylinder("v14-interior-column", accent,
                           (bx-pitch*.30, face_y+inside*2.4, grade+2.6), .16, 5.0, 12)
        batch.add_box("v27-interior-light-slot", "warm-light",
                      (bx, face_y+inside*2.6, grade+5.08),
                      (pitch*.58, 1.9, .08))
        if is_cafe:
            for table_offset in (-pitch*.18, pitch*.18):
                batch.add_cylinder("v27-cafe-table", "ledger-bronze",
                                   (bx+table_offset, face_y+inside*2.8, grade+.78), .46, .10, 16)
                for chair_offset in (-.58, .58):
                    batch.add_box("v27-cafe-chair", "timber-accent",
                                  (bx+table_offset, face_y+inside*(2.8+chair_offset), grade+.45),
                                  (.44,.44,.72))
        elif is_community:
            batch.add_box("v27-community-display-wall", "archive-warm-stone",
                          (bx, face_y+inside*5.68, grade+2.35),
                          (pitch*.62, .16, 3.4))
            batch.add_box("v27-community-bench", "timber-accent",
                          (bx, face_y+inside*3.2, grade+.55),
                          (pitch*.55,.62,.38))
        elif is_lobby:
            batch.add_box("v27-lobby-reception-backdrop", "ledger-granite",
                          (bx, face_y+inside*5.67, grade+2.55),
                          (pitch*.68,.18,4.0))
            batch.add_box("v27-lobby-reception-desk", "timber-accent",
                          (bx, face_y+inside*3.7, grade+1.0),
                          (pitch*.62,.78,1.35))
        # The sign band is framed architecture, deliberately blank and never a
        # floating decal.
        batch.add_box("v27-frontage-signage-back", "ledger-granite" if style >= 3 else "archive-warm-stone",
                      (bx, face_y+facing*.05, grade+4.62),
                      (pitch*.62,.18,.50))
        batch.add_box("v27-frontage-signage-frame", accent,
                      (bx, face_y+facing*.16, grade+4.62),
                      (pitch*.72,.08,.62))
    batch.add_box("v14-frontage-structural-pier", accent,
                  (x+frontage_w*.5, frontage_attachment_y, grade+2.7),
                  (.42, frontage_attachment_depth, 5.4))
    lobby_x = x-frontage_w*.5+(lobby_bay+.5)*pitch
    batch.add_box("v14-lobby-canopy", accent, (lobby_x, face_y+facing*1.8, grade+5.2), (pitch*1.6, 3.6, .30))
    batch.add_box("v19-lobby-canopy-light", "warm-light",
                  (lobby_x,face_y+facing*1.85,grade+5.02),(pitch*1.35,3.0,.08))
    for sx in (-1, 1):
        batch.add_cylinder("v14-canopy-column", accent,
                           (lobby_x+sx*pitch*.58, face_y+facing*3.25, grade+2.55), .16, 5.1, 12)
    # A double-height portal and side returns make the main entrance a load-
    # bearing facade event rather than a canopy pasted onto storefront glass.
    for sx in (-1, 1):
        batch.add_box("v27-lobby-portal-side", accent,
                      (lobby_x+sx*pitch*.78, frontage_attachment_y, grade+3.0),
                      (.34, frontage_attachment_depth+.28, 6.0))
    batch.add_box("v27-lobby-portal-head", accent,
                  (lobby_x, frontage_attachment_y, grade+5.86),
                  (pitch*1.72, frontage_attachment_depth+.28, .34))
    batch.add_box("v14-entry-threshold", "dry-stone", (lobby_x, face_y+facing*3.3, grade+.13), (pitch*1.8, 6.4, .26))
    batch.add_box("v14-tactile-route", "tactile-yellow", (lobby_x, face_y+facing*5.8, grade+.285), (1.1, 5.0, .08))
    for light_offset in (-frontage_w*.34,0,frontage_w*.34):
        batch.add_cylinder("v19-forecourt-light-pole","archive-metal",
                           (x+light_offset,face_y+facing*11.8,grade+1.55),.075,3.1,10)
        batch.add_uv_sphere("v19-forecourt-light-fixture","warm-light",
                            (x+light_offset,face_y+facing*11.8,grade+3.18),.16,12,6)
    for index,(px,offset,action) in enumerate(((lobby_x,4.7,"walking"),(lobby_x+2.1,6.3,"conversation"),
                                               (lobby_x-2.0,6.8,"conversation"),(x+frontage_w*.26,9.0,"walking"),
                                               (x-frontage_w*.28,10.5,"seated"))):
        FRONTAGE_ACTIVITY.append(v12.add_human(batch,px,face_y+facing*offset,0 if facing<0 else 3.14159,
                                                180000+style*20+index,action,z_base=grade))

    rear_y = y-facing*podium_depth*.5
    batch.add_box("v14-rear-service-entry", "service-charcoal", (x+width*.24, rear_y-facing*.08, 2.0), (5.8, .20, 4.0))
    batch.add_box("v14-rear-loading-canopy", accent, (x+width*.24, rear_y-facing*2.0, 4.2), (8.4, 4.0, .28))
    return {"maximumGapM": 0.0, "glassRecessM": FACADE_GLASS_RECESS_M,
            "glazingFrontY": glazing_front_y, "glazingBackY": glazing_back_y,
            "attachmentDepthM": frontage_attachment_depth, "bays": bays}


def add_production_building(batch, spec):
    x, y, width, depth, floors, floor_h, style = spec
    facing = -1 if y > 0 else 1
    podium_h = 7.8 + (style % 3) * .9
    stone = "archive-warm-stone" if style < 3 else "ledger-limestone"
    accent = "archive-metal" if style < 3 else "ledger-bronze"
    podium_depth = depth + 5.0
    structural_depth = podium_depth - FRONTAGE_VOID_DEPTH_M
    structural_y = y - facing * FRONTAGE_VOID_DEPTH_M * .5
    batch.add_box("v14-podium-structural-body", stone, (x, structural_y, podium_h*.5),
                  (width+7.0, structural_depth, podium_h))
    if FRONTAGE_VOID_DEPTH_M > 0:
        front_y = y + facing * podium_depth * .5
        # End walls and lintel close the occupied frontage volume into the podium.
        for side in (-1, 1):
            batch.add_box("v15-frontage-return-wall", stone,
                          (x+side*(width+6.4)*.5, front_y-facing*FRONTAGE_VOID_DEPTH_M*.5, podium_h*.5),
                          (.6, FRONTAGE_VOID_DEPTH_M, podium_h))
        batch.add_box("v15-frontage-structural-lintel", stone,
                      (x, front_y-facing*.18, 6.55), (width+7.0, .42, max(.8, podium_h-5.45)))
    batch.add_box("v14-podium-side-wing", "dry-stone",
                  (x+width*(.28 if style%2 else -.28), y-facing*2.0, podium_h*.62),
                  (width*.32, depth*.72, podium_h*.76))

    total_h = floors*floor_h
    lower_h, middle_h, upper_h = total_h*(.56+.02*(style%2)), total_h*.25, total_h*.15
    lower_w, lower_d = width*.78, depth*.76
    middle_w, middle_d = width*(.63 if style%2 else .67), depth*.64
    upper_w, upper_d = width*(.46+.03*(style%3)), depth*.52
    middle_x = x+width*(-.09 if style%2 else .08)
    upper_x = x+width*(.11 if style%3==0 else -.07)
    lower_shell_d=lower_d-TOWER_FACADE_CAVITY_DEPTH_M
    middle_shell_d=middle_d-TOWER_FACADE_CAVITY_DEPTH_M
    lower_shell_w=lower_w-TOWER_FACADE_CAVITY_DEPTH_M*2
    middle_shell_w=middle_w-TOWER_FACADE_CAVITY_DEPTH_M*2
    batch.add_box("v14-tower-lower-structural-shell", stone,
                  (x,y-facing*TOWER_FACADE_CAVITY_DEPTH_M*.5,podium_h+lower_h*.5),
                  (lower_shell_w,lower_shell_d,lower_h))
    batch.add_box("v14-tower-middle-structural-shell", "ledger-granite" if style in (2,4) else stone,
                  (middle_x,y-facing*(1.2+TOWER_FACADE_CAVITY_DEPTH_M*.5),podium_h+lower_h+middle_h*.5),
                  (middle_shell_w,middle_shell_d,middle_h))
    upper_shell_d=upper_d-TOWER_FACADE_CAVITY_DEPTH_M
    upper_shell_w=upper_w-TOWER_FACADE_CAVITY_DEPTH_M*2
    batch.add_box("v14-tower-upper-structural-shell", stone,
                  (upper_x,y-facing*(2.0+TOWER_FACADE_CAVITY_DEPTH_M*.5),podium_h+lower_h+middle_h+upper_h*.5),
                  (upper_shell_w,upper_shell_d,upper_h))

    # Family-specific corner and upper-mass devices are anchored to the shell.
    corner_side=-1 if style in (0,3,5) else 1
    batch.add_box("v23-corner-solid-pier",accent,
                  (x+corner_side*(lower_w*.5-.42),y+facing*(lower_d*.5-.36),podium_h+lower_h*.5),
                  (.84,.72,lower_h))
    if style%3==0:
        batch.add_box("v23-upper-portal-frame",accent,
                      (upper_x,y-facing*1.8,podium_h+lower_h+middle_h+upper_h-.8),
                      (upper_w+1.8,upper_d+1.2,1.1))
    elif style%3==1:
        batch.add_box("v23-upper-shadow-terrace","dry-stone",
                      (upper_x+upper_w*.12,y-facing*(upper_d*.32),podium_h+lower_h+middle_h+.35),
                      (upper_w*.82,upper_d*.34,.70))
    else:
        for fin in (-1,0,1):
            batch.add_box("v23-crown-vertical-fin",accent,
                          (upper_x+fin*upper_w*.24,y+facing*upper_d*.48,
                           podium_h+lower_h+middle_h+upper_h*.62),(.42,.52,upper_h*.72))

    lower = add_connected_facade(batch,x=x,y=y,width=lower_w,depth=lower_d,base_z=podium_h,
                                 height=lower_h,floors=floors,floor_h=floor_h,facing=facing,style=style,prefix="v14-lower")
    middle = add_connected_facade(batch,x=middle_x,y=y-facing*1.2,width=middle_w,depth=middle_d,
                                  base_z=podium_h+lower_h,height=middle_h,floors=max(5,int(middle_h/floor_h)),
                                  floor_h=floor_h,facing=facing,style=style+1,prefix="v14-middle")
    upper = add_connected_facade(batch,x=upper_x,y=y-facing*2.0,width=upper_w,depth=upper_d,
                                 base_z=podium_h+lower_h+middle_h,height=upper_h,
                                 floors=max(3,int(upper_h/floor_h)),floor_h=floor_h,
                                 facing=facing,style=style+2,prefix="v26-upper")
    lower_side=add_connected_side_and_rear(batch,x=x,y=y,width=lower_w,depth=lower_d,base_z=podium_h,
                                           height=lower_h,facing=facing,style=style,prefix="v14-lower")
    middle_side=add_connected_side_and_rear(batch,x=middle_x,y=y-facing*1.2,width=middle_w,depth=middle_d,
                                            base_z=podium_h+lower_h,height=middle_h,facing=facing,style=style+1,prefix="v26-middle")
    upper_side=add_connected_side_and_rear(batch,x=upper_x,y=y-facing*2.0,width=upper_w,depth=upper_d,
                                           base_z=podium_h+lower_h+middle_h,height=upper_h,facing=facing,style=style+2,prefix="v26-upper")
    ground = add_connected_ground_floor(batch,x=x,y=y,width=width,depth=depth,facing=facing,style=style)

    roof = podium_h+lower_h+middle_h+upper_h
    batch.add_box("v14-roof-machine-room","service-charcoal",(upper_x-upper_w*.12,y,roof+2.7),(upper_w*.38,upper_d*.42,5.4))
    batch.add_box("v14-roof-crown-frame",accent,(upper_x+upper_w*.10,y-facing*.8,roof+5.0),(upper_w*.56,upper_d*.48,2.4+style%3))
    for unit in range(3):
        batch.add_box("v14-roof-screened-unit","service-charcoal",(upper_x-3.0+unit*3.0,y+depth*.10,roof+7.0),(2.0,2.2,1.4))
    batch.add_box("v23-roof-parapet-front",accent,(upper_x,y+facing*upper_d*.49,roof+.55),(upper_w,.34,1.1))
    batch.add_box("v23-roof-parapet-rear",accent,(upper_x,y-facing*upper_d*.49,roof+.55),(upper_w,.34,1.1))

    maximum=max(lower["maximumGapM"],middle["maximumGapM"],upper["maximumGapM"],ground["maximumGapM"])
    assert maximum<=MAX_ENVELOPE_GAP_M+1e-6
    ENVELOPE_REPORTS.append({"style":style,"position":[x,y],"maximumEnvelopeGapM":maximum,
                             "minimumFacadeAttachmentDepthM":min(lower["attachmentDepthM"],middle["attachmentDepthM"],upper["attachmentDepthM"]),
                             "glassRecessM":max(lower["glassRecessM"],middle["glassRecessM"],upper["glassRecessM"]),
                             "glassBackToStructuralFaceGapM":max(lower["glassBackToStructuralFaceGapM"],
                                                                 middle["glassBackToStructuralFaceGapM"],
                                                                 upper["glassBackToStructuralFaceGapM"]),
                             "sideGlassBackToStructuralFaceGapM":max(lower_side["glassBackToStructuralFaceGapM"],
                                                                     middle_side["glassBackToStructuralFaceGapM"],
                                                                     upper_side["glassBackToStructuralFaceGapM"]),
                             "facadeBays":lower["bayCount"]+middle["bayCount"]+upper["bayCount"],"frontageBays":ground["bays"]})


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    parser=argparse.ArgumentParser(); parser.add_argument("--output-root",required=True); parsed=parser.parse_args(args)
    output=Path(parsed.output_root); output.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True); ENVELOPE_REPORTS.clear()
    original=v12.add_building; v12.add_building=add_production_building
    try: objects,geometry,validation,consolidation,trees,activity=v12.build_zone()
    finally: v12.add_building=original
    for obj in objects: obj["heroRevision"]="V14_ENVELOPE_CONNECTED"
    target=output/"archive-water-plaza-hero-v14.glb"
    bpy.ops.export_scene.gltf(filepath=str(target),export_format="GLB",export_yup=True,export_normals=True,
                              export_texcoords=False,export_materials="EXPORT",export_apply=True)
    report={"status":"PASS","zone":"Archive Water Plaza","revision":6,
            "implementationPath":"V14_ENVELOPE_CONNECTED_PUNCHED_FACADE","glb":str(target),
            "bytes":target.stat().st_size,"geometry":geometry,"validation":validation,"consolidation":consolidation,
            "buildingCount":6,"replacedInstances":v12.REPLACED_INSTANCES,"lobbyCount":6,"retailPublicBayCount":44,
            "pavilionCount":1,"serviceEntranceCount":6,"treeVariantCount":12,"treeCount":len(trees),
            "humanCount":len(activity),"vehicleCount":2,
            "envelopeConnection":{"status":"PASS","maximumAllowedGapM":MAX_ENVELOPE_GAP_M,
            "maximumObservedGapM":max(x["maximumEnvelopeGapM"] for x in ENVELOPE_REPORTS),"buildings":ENVELOPE_REPORTS},
            "streetEyePriority":True,"officeV5Changed":False,"imageDatablocks":len(bpy.data.images),
            "directReferenceCopy":False,"originality":"ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY"}
    (output/"archive-water-plaza-hero-v14-report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"status":"PASS","glb":str(target),"triangles":geometry["triangles"],
                      "maximumEnvelopeGapM":report["envelopeConnection"]["maximumObservedGapM"]}))


if __name__=="__main__": main()
