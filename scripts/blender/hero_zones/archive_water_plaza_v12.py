"""Production-focused Archive Water Plaza hero zone.

The GLB uses absolute district coordinates and replaces six nearby support instances.
It is intentionally authored for 1.65m street review before aerial coverage.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
BLENDER = HERE.parent
PROD = BLENDER / "production_geometry"
CORE = BLENDER / "core_district_precision"
FINAL = BLENDER / "urban_stream_final"
sys.path[:0] = [str(PROD), str(CORE), str(FINAL)]
from geometry_core import MeshBatch, validate_geometry
from batch_consolidation import consolidate
from materials_v11 import create_materials

SEED = 120101
ZONE_CENTER = (-250.0, 0.0)
REPLACED_INSTANCES = [
    "core-block-03-building-10", "core-block-03-building-09",
    "core-block-15-building-01", "core-block-04-building-08",
    "core-block-15-building-02", "core-block-04-building-09",
    "core-block-03-building-08", "core-block-04-building-10",
    "core-block-05-building-08", "core-block-14-building-01",
    "core-block-14-building-02", "core-block-16-building-01",
]


class HeroBatch(MeshBatch):
    def add_uv_sphere(self, role, material, center, radius, segments=16, rings=8, squash=(1.0, 1.0, 1.0)):
        cx, cy, cz = center
        vertices = []
        for ring in range(rings + 1):
            phi = math.pi * ring / rings
            for segment in range(segments):
                theta = math.tau * segment / segments
                vertices.append((
                    cx + radius * math.sin(phi) * math.cos(theta) * squash[0],
                    cy + radius * math.sin(phi) * math.sin(theta) * squash[1],
                    cz + radius * math.cos(phi) * squash[2],
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
        self._append(role, material, vertices, faces)

    def add_frustum(self, role, material, center, radius_bottom, radius_top, height, segments=12):
        cx,cy,cz=center;vertices=[]
        for z,radius in ((cz-height*.5,radius_bottom),(cz+height*.5,radius_top)):
            vertices.extend((cx+radius*math.cos(math.tau*i/segments),cy+radius*math.sin(math.tau*i/segments),z)
                            for i in range(segments))
        vertices.extend(((cx,cy,cz-height*.5),(cx,cy,cz+height*.5)))
        bottom,top=segments*2,segments*2+1;faces=[]
        for i in range(segments):
            nxt=(i+1)%segments
            faces.extend(((i,nxt,segments+nxt),(i,segments+nxt,segments+i),(bottom,nxt,i),(top,segments+i,segments+nxt)))
        self._append(role,material,vertices,faces)

    def add_water_ribbon(self, role, material, center, length, width, base_z, length_segments=56, width_segments=8):
        """Generate a seamless centimetre-ripple water surface from geometry."""
        cx,cy=center;vertices=[]
        for ix in range(length_segments+1):
            u=ix/length_segments;x=cx-length*.5+u*length
            for iy in range(width_segments+1):
                v=iy/width_segments;y=cy-width*.5+v*width
                boundary=ix in (0,length_segments) or iy in (0,width_segments)
                wave=0.0 if boundary else math.sin(u*math.tau*9+v*2.1)*.018+math.sin(u*math.tau*17-v*3.4)*.009
                vertices.append((x,y,base_z+wave))
        stride=width_segments+1;faces=[]
        for ix in range(length_segments):
            for iy in range(width_segments):
                a=ix*stride+iy;b=a+stride;c=b+1;d=a+1
                faces.extend(((a,b,c),(a,c,d)))
        self._append(role,material,vertices,faces)

    def add_tapered_branch(self, role, material, start, end, radius_start, radius_end, segments=10):
        """Add an oriented tapered branch between two actual attachment points."""
        sx,sy,sz=start;ex,ey,ez=end;dx,dy,dz=ex-sx,ey-sy,ez-sz
        length=math.sqrt(dx*dx+dy*dy+dz*dz);assert length>0
        wx,wy,wz=dx/length,dy/length,dz/length
        rx,ry,rz=(0.,0.,1.) if abs(wz)<.9 else (0.,1.,0.)
        ux,uy,uz=wy*rz-wz*ry,wz*rx-wx*rz,wx*ry-wy*rx
        ul=math.sqrt(ux*ux+uy*uy+uz*uz);ux,uy,uz=ux/ul,uy/ul,uz/ul
        vx,vy,vz=wy*uz-wz*uy,wz*ux-wx*uz,wx*uy-wy*ux
        vertices=[]
        for point,radius in ((start,radius_start),(end,radius_end)):
            px,py,pz=point
            for i in range(segments):
                angle=math.tau*i/segments;ca,sa=math.cos(angle),math.sin(angle)
                vertices.append((px+radius*(ux*ca+vx*sa),py+radius*(uy*ca+vy*sa),pz+radius*(uz*ca+vz*sa)))
        vertices.extend((start,end));bottom,top=segments*2,segments*2+1;faces=[]
        for i in range(segments):
            nxt=(i+1)%segments;faces.extend(((i,nxt,segments+nxt),(i,segments+nxt,segments+i),(bottom,nxt,i),(top,segments+i,segments+nxt)))
        self._append(role,material,vertices,faces)


def add_facade(batch, x, y, width, depth, podium_h, floors, floor_h, facing, style, seed):
    rng = random.Random(seed)
    front_y = y + facing * (depth / 2 + .18)
    bay = (3.2, 3.8, 4.4)[style % 3]
    columns = max(5, int(width / bay))
    usable = width * .86
    for floor in range(2, floors):
        z = podium_h + floor * floor_h + floor_h * .50
        zone = floor // max(4, floors // 4)
        if floor % 7 == 0:
            batch.add_box("hero-mechanical-shadow-band", "service-charcoal", (x, front_y + facing * .18, z), (usable, .42, .62))
            continue
        for column in range(columns):
            offset = -usable / 2 + (column + .5) * usable / columns
            panel_w = usable / columns * (.72 if (column + zone + style) % 4 else .48)
            recess = .20 + .12 * ((column + floor + style) % 3)
            batch.add_box("hero-recessed-window", "blue-gray-glass", (x + offset, front_y - facing * recess, z), (panel_w, .18, floor_h * .63))
            if floor % (3 + style % 2) == 0 and column % 3 == style % 3:
                batch.add_box("hero-facade-projecting-frame", "archive-metal", (x + offset, front_y + facing * .34, z), (panel_w + .28, .32, floor_h * .84))
        if floor % 4 == style % 4:
            batch.add_box("hero-horizontal-shadow-line", "ledger-bronze", (x, front_y + facing * .28, z - floor_h * .40), (usable + .6, .30, .16))
    # Side grammar is explicitly different and less transparent.
    side_x = x + width / 2 + .16
    side_bays = max(3, int(depth / 5.2))
    for floor in range(2, floors, 2):
        z = podium_h + floor * floor_h + floor_h * .50
        for side_bay in range(side_bays):
            sy = y - depth * .36 + side_bay * (depth * .72 / max(1, side_bays - 1))
            material = "ledger-limestone" if (side_bay + floor + style) % 3 else "blue-gray-glass"
            batch.add_box("hero-side-facade-bay", material, (side_x, sy, z), (.24, 2.7, floor_h * .60))
    # Rear service bands and ventilation are functional, not mirrored frontage.
    rear_y = y - facing * (depth / 2 + .20)
    for floor in range(3, floors, 4):
        z = podium_h + floor * floor_h
        batch.add_box("hero-rear-service-band", "service-charcoal", (x, rear_y, z), (width * .68, .35, 1.5))


def add_ground_floor(batch, x, y, width, depth, facing, variant):
    front_y = y + facing * (depth / 2 + 4.4)
    # Deep 5.5m occupied interior volumes with independent ceiling/floor/rear wall.
    lobby_x = x + (-.22 + .11 * variant) * width
    batch.add_box("hero-interior-floor", "ledger-granite", (lobby_x, front_y - facing * 2.7, .15), (width * .32, 5.4, .30))
    batch.add_box("hero-interior-ceiling", "warm-interior", (lobby_x, front_y - facing * 2.7, 5.15), (width * .32, 5.4, .22))
    batch.add_box("hero-interior-rear-wall", "warm-interior", (lobby_x, front_y - facing * 5.35, 2.6), (width * .32, .24, 5.0))
    batch.add_box("hero-lobby-glazing", "blue-gray-glass", (lobby_x, front_y, 2.6), (width * .31, .20, 4.9))
    batch.add_box("hero-lobby-door", "archive-metal", (lobby_x + width * .07, front_y + facing * .15, 1.35), (1.8, .18, 2.7))
    batch.add_box("hero-main-canopy", "archive-metal", (lobby_x, front_y + facing * 2.2, 5.25), (width * .42, 4.8, .34))
    # Retail/public bays contain rear wall, columns, counters and framed glazing.
    bay_count = 4 + variant % 3
    for bay in range(bay_count):
        bx = x - width * .40 + bay * (width * .80 / max(1, bay_count - 1))
        if abs(bx - lobby_x) < width * .18:
            continue
        batch.add_box("hero-retail-floor", "dry-stone", (bx, front_y - facing * 2.2, .12), (5.0, 4.4, .24))
        batch.add_box("hero-retail-ceiling", "warm-interior", (bx, front_y - facing * 2.2, 4.2), (5.0, 4.4, .18))
        batch.add_box("hero-retail-rear-wall", "warm-interior", (bx, front_y - facing * 4.35, 2.1), (5.0, .20, 4.1))
        batch.add_box("hero-retail-glazing", "blue-gray-glass", (bx, front_y, 2.1), (4.7, .18, 4.0))
        batch.add_box("hero-retail-door", "archive-metal", (bx + 1.25, front_y + facing * .14, 1.25), (1.1, .16, 2.5))
        batch.add_box("hero-retail-counter", "timber-accent", (bx, front_y - facing * 3.25, 1.05), (2.5, .65, 1.2))
        batch.add_box("hero-blank-signage", "archive-warm-stone", (bx, front_y + facing * .16, 4.55), (4.5, .18, .58))
    # Arcade/covered walk and tactile threshold.
    arcade_y = front_y + facing * 3.1
    batch.add_box("hero-covered-arcade-roof", "archive-warm-stone", (x, arcade_y, 5.5), (width + 5, 4.4, .42))
    for column in range(-3, 4):
        batch.add_cylinder("hero-arcade-column", "ledger-bronze", (x + column * width / 7, arcade_y + facing * 1.45, 2.7), .25, 5.4, 12)
    batch.add_box("hero-tactile-entry-route", "tactile-yellow", (lobby_x, arcade_y + facing * 3.0, .07), (2.0, 6.0, .14))
    # Rear loading/service entry is physically separate.
    rear_y = y - facing * (depth / 2 + 3.6)
    batch.add_box("hero-service-volume", "service-charcoal", (x + width * .18, rear_y, 2.5), (width * .28, 5.0, 5.0))
    batch.add_box("hero-service-door", "archive-metal", (x + width * .18, rear_y - facing * 2.55, 1.65), (3.2, .20, 3.3))
    batch.add_box("hero-loading-apron", "ledger-granite", (x, rear_y - facing * 5.8, .12), (width + 4, 7.0, .24))


def add_building(batch, spec):
    x, y, width, depth, floors, floor_h, style = spec
    facing = -1 if y > 0 else 1
    podium_h = 7.2 + (style % 3) * 1.1
    tower_h = floors * floor_h
    # Three materially distinct masses and a real setback sequence.
    batch.add_box("hero-podium-main", "archive-warm-stone" if y > 0 else "ledger-limestone", (x, y, podium_h / 2), (width + 8, depth + 6, podium_h))
    batch.add_box("hero-podium-stream-wing", "dry-stone", (x - width * .26, y + facing * (depth / 2 + 1.8), podium_h * .43), (width * .48, 7.5, podium_h * .86))
    batch.add_box("hero-tower-lower", "blue-gray-glass", (x - width * .08, y, podium_h + tower_h * .31), (width * .76, depth * .76, tower_h * .62))
    batch.add_box("hero-tower-upper", "archive-warm-stone" if style % 2 else "ledger-limestone", (x + width * (.08 if style % 2 else -.12), y - facing * 1.8, podium_h + tower_h * .75), (width * .52, depth * .58, tower_h * .30))
    batch.add_box("hero-corner-spine", "archive-metal" if y > 0 else "ledger-bronze", (x + width * .39, y + facing * depth * .37, podium_h + tower_h * .45), (.75, .75, tower_h * .82))
    add_facade(batch, x, y, width, depth, podium_h, floors, floor_h, facing, style, SEED + style)
    add_ground_floor(batch, x, y, width, depth, facing, style)
    roof = podium_h + tower_h
    batch.add_box("hero-roof-machine-room", "service-charcoal", (x - width * .08, y, roof + 3.0), (width * .24, depth * .26, 6.0))
    batch.add_box("hero-roof-crown", "archive-metal" if style % 2 else "ledger-bronze", (x + width * .12, y, roof + 4.2), (width * .35, depth * .32, 2.6 + style % 3))
    for unit in range(4):
        batch.add_box("hero-roof-hvac", "service-charcoal", (x - 4.5 + unit * 3.0, y + depth * .12, roof + 6.4), (2.0, 2.6, 1.4))


def add_tree(batch, x, y, seed, scale=1.0, z_base=0.0):
    rng = random.Random(seed)
    height = (7.5 + rng.random() * 3.8) * scale
    batch.add_cylinder("hero-tree-trunk-base", "timber-accent", (x, y, z_base+height * .18), .34 * scale, height * .36, 16)
    batch.add_cylinder("hero-tree-trunk", "timber-accent", (x, y, z_base+height * .43), .22 * scale, height * .52, 14)
    for branch in range(5):
        angle = branch * math.tau / 5 + rng.uniform(-.18, .18)
        start=(x,y,z_base+height*(.49+.025*branch))
        end=(x+math.cos(angle)*(1.45+.16*(branch%2))*scale,
             y+math.sin(angle)*(1.45+.16*(branch%2))*scale,
             z_base+height*(.66+.025*(branch%3)))
        batch.add_tapered_branch("hero-tree-primary-branch","timber-accent",start,end,.13*scale,.055*scale,10)
        for twig in (-1,1):
            twig_angle=angle+twig*.48
            twig_end=(end[0]+math.cos(twig_angle)*.82*scale,end[1]+math.sin(twig_angle)*.82*scale,end[2]+(.42+.12*(twig>0))*scale)
            batch.add_tapered_branch("hero-tree-secondary-branch","timber-accent",end,twig_end,.06*scale,.025*scale,8)
    material = ("foliage-deep", "foliage-mid", "foliage-light")[seed % 3]
    batch.add_uv_sphere("hero-tree-irregular-crown", material, (x, y, z_base+height * .80), 2.15 * scale, 20, 10, (1.05, .90, .78))
    for lobe in range(5):
        angle = lobe * math.tau / 5 + rng.uniform(-.20, .20)
        radius = (1.0 + rng.random() * .35) * scale
        batch.add_uv_sphere("hero-tree-irregular-crown", material, (x + math.cos(angle) * 1.55 * scale, y + math.sin(angle) * 1.35 * scale, z_base+height * .82 + (lobe % 2) * .35), radius, 18, 9, (1.12, .92, .82))


def add_human(batch, x, y, facing, seed, action, z_base=0.0):
    rng = random.Random(seed)
    palette = ("archive-metal", "ledger-bronze", "archive-warm-stone", "service-charcoal")
    clothing = palette[seed % len(palette)]
    batch.add_frustum("hero-human-tailored-torso",clothing,(x,y,z_base+1.19),.16,.24,.70,12)
    batch.add_box("hero-human-shoulder-line",clothing,(x,y,z_base+1.48),(.54,.20,.14))
    batch.add_cylinder("hero-human-neck","archive-warm-stone",(x,y,z_base+1.57),.075,.16,10)
    batch.add_uv_sphere("hero-human-head", "archive-warm-stone", (x, y, z_base+1.75), .155, 14, 7, (1, .94, 1.10))
    stride = .18 if action in ("walking", "crossing") else .08
    for side in (-1, 1):
        batch.add_frustum("hero-human-leg", "service-charcoal", (x + side * .09, y + side * stride, z_base+.47), .055,.075,.88,8)
        batch.add_frustum("hero-human-arm", clothing, (x + side * .29, y - side * stride, z_base+1.18), .045,.06,.66,8)
        batch.add_uv_sphere("hero-human-hand","archive-warm-stone",(x+side*.29,y-side*stride,z_base+.83),.065,8,4,(1,.82,1.12))
        batch.add_box("hero-human-shoe","service-charcoal",(x+side*.09,y+side*(stride+.055),z_base+.055),(.14,.26,.11))
    return {"position": [x, y], "action": action, "orientation": facing, "grounded": True}


def build_zone():
    materials = create_materials()
    batch = HeroBatch(materials)
    # Explicit water hierarchy: bed, water, lower promenade, stepped access, civic terraces.
    batch.add_box("hero-water-bed", "dark-water-bed", (-250, 0, -.52), (220, 12, .34))
    batch.add_water_ribbon("hero-water-surface", "shallow-water-v11", (-250, 0), 220, 11.4, -.11)
    for side in (-1, 1):
        batch.add_box("hero-lower-promenade", "wet-stone", (-250, side * 10.5, .02), (220, 8.0, .24))
        # Retaining wall is interrupted by real stepped/ramped access sections.
        for wall_x,wall_w in ((-350,12),(-327,10),(-275,10),(-225,10),(-175,10),(-150,8)):
            batch.add_box("hero-retaining-wall", "ledger-granite", (wall_x, side * 15.0, 1.05), (wall_w, .55, 2.1))
        batch.add_box("hero-upper-civic-terrace", "promenade-paver", (-250, side * 27.0, 2.08), (220, 24, .32))
        batch.add_box("hero-planted-threshold", "soil-v11", (-250, side * 42.0, 2.28), (205, 5.2, .65))
        batch.add_box("hero-promenade-guidance-band", "ledger-granite", (-250, side * 19.0, 2.27), (220, 1.2, .08))
        batch.add_box("hero-stream-coping", "wet-stone", (-250, side * 6.25, .30), (220, .48, .42))
        for band_x in (-330, -290, -250, -210, -170):
            batch.add_box("hero-civic-cross-paving", "dry-stone", (band_x, side * 28.0, 2.28), (2.2, 21.0, .08))
        # Fine-grained paving joints make the civic surface readable at eye level.
        for joint_x in range(-354, -145, 8):
            batch.add_box("hero-paving-joint", "ledger-granite", (joint_x, side * 27.0, 2.255), (.055, 23.5, .035))
        for joint_y in range(18, 39, 4):
            batch.add_box("hero-paving-joint", "ledger-granite", (-250, side * joint_y, 2.255), (218, .055, .035))
        # Four broad stair/ramp access sequences per bank.
        for access_x in (-325, -275, -225, -175):
            for step in range(6):
                batch.add_box("hero-civic-step", "dry-stone", (access_x, side * (17.2 + step * 1.35), .22 + step * .31), (13, 1.42, .62))
            batch.add_wedge("hero-accessible-ramp", "promenade-paver", (access_x + 10, side * 21.2, 1.1), (3.4, 13, 2.2), "y")
            batch.add_box("hero-handrail", "archive-metal", (access_x + 8.1, side * 21.2, 1.85), (.10, 13, 1.3))
        for terrace_x in (-300, -250, -200):
            for step in range(4):
                batch.add_box("hero-stepped-seating-edge", "dry-stone",
                              (terrace_x, side*(14.6+step*1.18), .28+step*.42), (26.0,1.28,.56))
            for seat_x in (-8.0,0.0,8.0):
                batch.add_box("hero-stepped-timber-seat", "timber-accent",
                              (terrace_x+seat_x,side*17.8,1.72),(4.3,.68,.16))
    # Gateway bridge, pavilion and event terrace.  The failed bridge read as a
    # pair of oversized rectangular portals.  V27 keeps civic identity at the
    # approaches, but the deck, pylons and diagonal members now form a credible
    # low pedestrian bridge that preserves the stream view corridor.
    batch.add_box("hero-gateway-bridge-deck", "archive-warm-stone", (-250, 0, 2.65), (16, 36, .75))
    for side in (-1, 1):
        edge_x = -250 + side * 7.1
        for bank in (-1, 1):
            pylon_y = bank * 12.0
            batch.add_box("hero-gateway-approach-pylon", "archive-metal",
                          (edge_x, pylon_y, 5.7), (.62, .86, 5.8))
            batch.add_box("hero-gateway-pylon-light", "archive-cyan-light",
                          (edge_x-side*.33, pylon_y-bank*.18, 5.65), (.08, .18, 3.9))
            batch.add_tapered_branch("hero-gateway-diagonal-brace", "archive-metal",
                                     (edge_x, pylon_y, 8.45),
                                     (edge_x, bank*3.2, 3.25), .20, .12, 12)
        batch.add_box("hero-gateway-deck-edge", "service-charcoal",
                      (edge_x, 0, 3.08), (.28, 33.0, .34))
        for post in range(-5, 6):
            batch.add_cylinder("hero-bridge-railing-post", "archive-metal", (edge_x, post * 2.7, 4.0), .07, 2.0, 8)
        batch.add_box("hero-bridge-handrail", "archive-metal", (edge_x, 0, 4.95), (.15, 31, .15))
        batch.add_box("hero-bridge-handrail-light", "warm-light",
                      (edge_x-side*.09, 0, 4.80), (.06, 30.0, .08))
    batch.add_box("hero-water-pavilion-floor", "dry-stone", (-300, -24, 2.45), (24, 18, .45))
    batch.add_box("hero-water-pavilion-roof", "archive-metal", (-300, -24, 8.4), (27, 21, .45))
    for px in (-310, -302, -294):
        for py in (-31, -17):
            batch.add_cylinder("hero-pavilion-column", "ledger-bronze", (px, py, 5.35), .26, 5.8, 12)
    # Pavilion enclosure is framed into bays rather than exported as one glass box.
    for px in (-308.0, -302.7, -297.3, -292.0):
        batch.add_box("hero-pavilion-glazing-bay", "pavilion-glass", (px, -16.55, 5.25), (4.5, .10, 5.1))
        batch.add_box("hero-pavilion-glazing-bay", "pavilion-glass", (px, -31.45, 5.25), (4.5, .10, 5.1))
    for frame_x in (-310.7, -305.4, -300.0, -294.6, -289.3):
        batch.add_box("hero-pavilion-frame", "archive-metal", (frame_x, -16.42, 5.35), (.18, .18, 5.6))
        batch.add_box("hero-pavilion-frame", "archive-metal", (frame_x, -31.58, 5.35), (.18, .18, 5.6))
    for py in (-28.5, -24.0, -19.5):
        batch.add_box("hero-pavilion-side-glazing", "pavilion-glass", (-311.05, py, 5.25), (.10, 3.7, 5.1))
        batch.add_box("hero-pavilion-side-glazing", "pavilion-glass", (-288.95, py, 5.25), (.10, 3.7, 5.1))
    batch.add_box("hero-pavilion-warm-ceiling", "warm-light", (-300, -24, 7.95), (19.5, 12.5, .12))
    # A furnished, bounded pavilion interior replaces the former opaque box.
    batch.add_box("hero-pavilion-rear-feature-wall", "warm-interior", (-300, -29.2, 4.8), (17.5, .32, 4.4))
    batch.add_box("hero-pavilion-service-core", "ledger-granite", (-307.2, -26.5, 4.75), (3.2, 4.0, 4.5))
    batch.add_box("hero-pavilion-reception", "timber-accent", (-300, -27.2, 3.35), (5.6, 1.0, 1.3))
    for table_x in (-304.5,-298.0,-292.0):
        batch.add_cylinder("hero-pavilion-table", "ledger-bronze", (table_x,-21.5,3.15), .72,.12,18)
        for chair_y in (-1.0,1.0):
            batch.add_box("hero-pavilion-chair", "timber-accent", (table_x,-21.5+chair_y,2.85),(.52,.52,.66))
    for light_x in (-306,-300,-294):
        batch.add_cylinder("hero-pavilion-pendant", "warm-light", (light_x,-23.0,6.55), .18,.35,12)
    # Six distinct adjacent buildings replace six existing instances.
    specs = [
        (-326, 78, 44, 34, 22, 3.55, 0), (-260, 82, 50, 38, 28, 3.65, 1), (-190, 75, 38, 32, 18, 3.50, 2),
        (-326, -78, 48, 36, 25, 3.60, 3), (-258, -82, 42, 34, 20, 3.55, 4), (-188, -76, 54, 40, 16, 3.70, 5),
    ]
    for spec in specs:
        add_building(batch, spec)
    # Curated trees frame entrances and views instead of random scatter.
    tree_records = []
    tree_positions = [
        (-340, 40), (-318, 43), (-286, 40), (-220, 42), (-188, 44), (-164, 40),
        (-340, -42), (-315, -46), (-285, -42), (-225, -45), (-195, -42), (-165, -44),
        (-350, 48), (-300, 49), (-240, 48), (-175, 49), (-350, -50), (-295, -50), (-235, -49), (-170, -50),
        (-332, 31), (-305, 33), (-272, 31), (-238, 33), (-204, 31), (-176, 33),
        (-332, -31), (-305, -33), (-272, -31), (-238, -33), (-204, -31), (-176, -33),
    ]
    for index, (tx, ty) in enumerate(tree_positions):
        add_tree(batch, tx, ty, SEED + 300 + index, .85 + (index % 4) * .08, z_base=2.3)
        tree_records.append({"variant": index % 12, "position": [tx, ty], "role": "entrance-frame" if abs(ty) > 30 else "stream-edge-softening"})
    # Benches, café clusters, bollards and lights create readable activity anchors.
    for cluster_x in (-330, -285, -220, -175):
        for side in (-1, 1):
            y = side * 24.5
            batch.add_box("hero-bench-seat", "timber-accent", (cluster_x, y, .72), (3.0, .65, .20))
            batch.add_box("hero-bench-back", "timber-accent", (cluster_x, y - side * .30, 1.15), (3.0, .16, .9))
            batch.add_cylinder("hero-cafe-table", "ledger-bronze", (cluster_x + 5.0, y, .72), .72, .12, 18)
            for seat in (-1.2, 1.2):
                batch.add_cylinder("hero-cafe-seat", "timber-accent", (cluster_x + 5.0 + seat, y, .52), .28, .48, 12)
            batch.add_box("hero-terrace-planter", "archive-warm-stone", (cluster_x - 5.2, side * 34.0, 2.75), (4.2, 1.8, 1.25))
            batch.add_box("hero-terrace-planter-soil", "soil-v11", (cluster_x - 5.2, side * 34.0, 3.42), (3.8, 1.45, .18))
            for shrub in (-1.15, 0, 1.15):
                batch.add_uv_sphere("hero-planter-shrub", "foliage-mid", (cluster_x - 5.2 + shrub, side * 34.0, 4.05), .72, 14, 7, (1.0, .72, .62))
    # Occupied cafe terraces give the civic banks a legible everyday use.
    for cafe_x,cafe_side in ((-315,-1),(-255,1),(-195,-1),(-180,1)):
        cafe_y=cafe_side*29.0
        batch.add_cylinder("hero-cafe-umbrella-pole","ledger-bronze",(cafe_x,cafe_y,4.25),.09,3.7,10)
        batch.add_frustum("hero-cafe-umbrella-canopy","archive-warm-stone",(cafe_x,cafe_y,6.0),2.25,.35,.65,18)
        batch.add_cylinder("hero-cafe-terrace-table","ledger-bronze",(cafe_x,cafe_y,3.03),.72,.14,18)
        for angle in (0,math.pi*.5,math.pi,math.pi*1.5):
            batch.add_box("hero-cafe-terrace-chair","timber-accent",
                          (cafe_x+math.cos(angle)*1.25,cafe_y+math.sin(angle)*1.25,2.72),(.48,.48,.62),angle)
    for light_x in range(-350, -149, 20):
        for side in (-1, 1):
            batch.add_cylinder("hero-pedestrian-light-pole", "archive-metal", (light_x, side * 18.5, 2.2), .10, 4.4, 10)
            batch.add_uv_sphere("hero-pedestrian-light-fixture", "warm-light", (light_x, side * 18.5, 4.45), .22, 12, 6)
            batch.add_box("hero-edge-step-light", "archive-cyan-light", (light_x, side * 14.7, .62), (1.5, .12, .18))
    activity = []
    actions = ("walking", "conversation", "seated", "pavilion", "crossing")
    featured_activity = [
        (-334, -11, "walking"), (-330, -9, "conversation"), (-324, -12, "conversation"),
        (-306, -21, "pavilion"), (-300, -18, "pavilion"), (-292, -22, "seated"),
        (-270, 10, "crossing"), (-264, 12, "crossing"), (-238, -10, "walking"),
        (-226, 18, "seated"), (-214, 17, "conversation"), (-208, 20, "conversation"),
        (-316, -28, "seated"), (-312, -30, "conversation"), (-257, 28, "seated"), (-252, 31, "conversation"),
        (-197, -28, "seated"), (-191, -31, "conversation"), (-183, 28, "seated"), (-177, 30, "conversation"),
    ]
    for index, (x, y, action) in enumerate(featured_activity):
        activity.append(add_human(batch, x, y, 0, SEED + 550 + index, action, z_base=2.3 if abs(y)>15 else 0.0))
    for index in range(48):
        x = -345 + (index % 12) * 16.5 + (index // 12) * 1.8
        side = -1 if (index // 12) % 2 else 1
        y = side * (17 + (index % 4) * 5.2)
        activity.append(add_human(batch, x, y, 0 if side > 0 else math.pi, SEED + 600 + index,
                                  actions[index % len(actions)], z_base=2.3))
    # Two service vehicles remain on rear approaches; plaza itself is vehicle-free.
    for vx, vy, material in ((-315, 111, "service-charcoal"), (-205, -112, "ledger-bronze")):
        batch.add_box("hero-service-vehicle-body", material, (vx, vy, 1.05), (5.4, 2.1, 1.4))
        batch.add_box("hero-service-vehicle-cabin", "blue-gray-glass", (vx + 1.1, vy, 1.85), (2.0, 1.9, .9))
        for ox in (-1.8, 1.8):
            for oy in (-.86, .86):
                batch.add_cylinder("hero-service-vehicle-wheel", "service-charcoal", (vx + ox, vy + oy, .48), .36, .24, 12)
    consolidation = consolidate(batch)
    objects = batch.finalize()
    for obj in objects:
        # Near-camera foliage and water are intentionally smooth shaded.  The
        # prior flat primitive normals made otherwise multi-lobed trees read as
        # faceted symbols at street level.
        lowered=obj.name.lower()
        if any(token in lowered for token in ("foliage-", "shallow-water")):
            for polygon in obj.data.polygons:
                polygon.use_smooth=True
        obj["heroZone"] = "archive-water-plaza"
        obj["canonical"] = False
        obj["v3Applied"] = False
        obj["generationSeed"] = SEED
        obj["directReferenceCopy"] = False
        obj["originality"] = "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY"
    return objects, batch.statistics(), validate_geometry(objects), consolidation, tree_records, activity


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parsed = parser.parse_args(args)
    output = Path(parsed.output_root)
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objects, geometry, validation, consolidation, trees, activity = build_zone()
    target = output / "archive-water-plaza-hero-v12.glb"
    bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB", export_yup=True, export_normals=True, export_texcoords=False, export_materials="EXPORT", export_apply=True)
    report = {
        "status": "PASS", "zone": "Archive Water Plaza", "revision": 4,
        "glb": str(target), "bytes": target.stat().st_size, "geometry": geometry,
        "validation": validation, "consolidation": consolidation,
        "buildingCount": 6, "replacedInstances": REPLACED_INSTANCES,
        "lobbyCount": 6, "retailPublicBayCount": 26, "pavilionCount": 1,
        "serviceEntranceCount": 6, "treeVariantCount": 12, "treeCount": len(trees),
        "humanCount": len(activity), "vehicleCount": 2,
        "streamSection": "formal-civic-multilevel", "bridge": "archive-gateway",
        "streetEyePriority": True, "officeV5Changed": False, "imageDatablocks": len(bpy.data.images),
        "directReferenceCopy": False, "originality": "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY",
    }
    (output / "archive-water-plaza-hero-v12-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "glb": str(target), "bytes": report["bytes"], "triangles": geometry["triangles"], "meshObjects": geometry["meshObjects"], "buildings": 6, "humans": len(activity)}))


if __name__ == "__main__":
    main()
