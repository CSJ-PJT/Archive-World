"""Seven actual urban sections joining upper streets to a lower promenade."""
from __future__ import annotations

import math

SECTION_TYPES = (
    "archive-plaza",
    "ledger-terrace",
    "transit-junction",
    "green-park",
    "mixed-active-frontage",
    "service-maintenance",
    "future-riverfront-gateway",
)


def build_sections(batch, segments):
    records = []
    for index, segment in enumerate(segments):
        kind = SECTION_TYPES[index % len(SECTION_TYPES)]
        x0, y0 = segment["start"]
        x1, y1 = segment["end"]
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        nx, ny = -dy / length, dx / length
        x, y = (x0 + x1) / 2, (y0 + y1) / 2
        water_width = segment["waterWidthM"]
        lower_width = 4.0 + (index % 3) * 1.2
        upper_width = 5.5 + ((index + 1) % 3) * 1.4
        lower_z = 0.18 + (index % 2) * 0.08
        upper_z = 2.1 + (index % 3) * 0.38

        def at(offset, z):
            return (x + nx * offset, y + ny * offset, z)

        def box(role, material, offset, z, dimensions):
            batch.add_box(role, material, at(offset, z), dimensions, rotation_z=angle)

        box(f"{kind}-bed", "dark-water-bed", 0, -0.42, (length + 0.6, water_width + 1.6, 0.20))
        box(f"{kind}-water", "shallow-water-v11", 0, -0.09, (length + 0.7, water_width, 0.055))
        for side in (-1, 1):
            lower_offset = side * (water_width / 2 + lower_width / 2 + 0.5)
            upper_offset = side * (water_width / 2 + lower_width + upper_width / 2 + 2.2)
            box(f"{kind}-lower-promenade", "promenade-paver", lower_offset, lower_z, (length + 0.3, lower_width, 0.28))
            box(f"{kind}-upper-walk", "dry-stone", upper_offset, upper_z, (length + 0.3, upper_width, 0.34))
            box(f"{kind}-retaining", "wet-stone", side * (water_width / 2 + lower_width + 0.6), upper_z / 2, (length + 0.2, 0.58, upper_z))
            box(f"{kind}-coping", "ledger-limestone", side * (water_width / 2 + lower_width + 0.6), upper_z + 0.14, (length + 0.3, 0.85, 0.28))
            box(f"{kind}-drainage", "service-charcoal", side * (water_width / 2 + 0.45), 0.02, (length + 0.2, 0.32, 0.12))
        # Alternating stairs and long barrier-free ramps make each bank reachable.
        for marker, t in enumerate((0.22, 0.72)):
            tx, ty = x0 + dx * t, y0 + dy * t
            side = -1 if (index + marker) % 2 else 1
            for step in range(7):
                offset = side * (water_width / 2 + lower_width + 0.75 + step * 0.55)
                batch.add_box(
                    f"{kind}-access-step",
                    "dry-stone",
                    (tx + nx * offset, ty + ny * offset, lower_z + step * (upper_z - lower_z) / 7),
                    (4.2, 0.75, 0.25),
                    rotation_z=angle,
                )
            ramp_offset = -side * (water_width / 2 + lower_width + upper_width / 2 + 1.0)
            batch.add_wedge(f"{kind}-accessible-ramp", "promenade-paver", (tx + nx * ramp_offset, ty + ny * ramp_offset, upper_z / 2), (9.5, 4.2, upper_z))
        records.append({
            "id": segment["id"], "type": kind, "upperStreetElevationM": round(upper_z, 2),
            "lowerPromenadeElevationM": round(lower_z, 2), "waterLevelM": -0.09,
            "bedLevelM": -0.42, "lowerWidthM": lower_width, "upperWidthM": upper_width,
            "barrierFree": True, "maintenanceRoute": True,
        })
    return {"sectionTypes": list(SECTION_TYPES), "records": records, "actualSectionCount": len(records), "flatSingleDepth": False}
