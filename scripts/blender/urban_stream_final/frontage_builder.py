"""Actual occupied lower-floor frontage modules with shallow interior volumes."""
from __future__ import annotations

FRONTAGE_COUNTS = {"lobby": 8, "retail-public": 12, "cafe-community": 4, "pavilion": 3, "arcade": 4, "transit": 3, "cultural": 3, "service": 4}


def build_unit(batch, family, variant, x, y, side):
    width = 7.2 + (variant % 4) * 1.4
    depth = 5.8 + (variant % 3) * 0.8
    height = 4.6 + (variant % 2) * 0.5
    facade_y = y + side * depth / 2
    frame_material = "archive-metal" if family in ("lobby", "transit", "pavilion") else "ledger-bronze"
    base_material = "archive-warm-stone" if variant % 2 == 0 else "ledger-limestone"
    batch.add_box(f"frontage-{family}-base", base_material, (x, y, 0.18), (width, depth, 0.36))
    batch.add_box(f"frontage-{family}-rear-wall", "warm-interior", (x, y - side * depth / 2, height / 2), (width - 0.6, 0.25, height))
    batch.add_box(f"frontage-{family}-ceiling", "warm-interior", (x, y, height), (width - 0.5, depth - 0.5, 0.20))
    batch.add_box(f"frontage-{family}-glazing", "blue-gray-glass", (x, facade_y, height / 2), (width - 0.8, 0.18, height - 0.5))
    for column_x in (-width / 2 + 0.25, width / 2 - 0.25):
        batch.add_box(f"frontage-{family}-frame", frame_material, (x + column_x, facade_y, height / 2), (0.24, 0.30, height))
    mullions = 2 + variant % 4
    for index in range(1, mullions + 1):
        mx = x - width / 2 + index * width / (mullions + 1)
        batch.add_box(f"frontage-{family}-mullion", frame_material, (mx, facade_y + side * 0.05, height / 2), (0.10, 0.12, height - 0.35))
    door_x = x + (-1 if variant % 2 else 1) * width * 0.18
    batch.add_box(f"frontage-{family}-door", frame_material, (door_x, facade_y + side * 0.13, 1.25), (1.45, 0.18, 2.5))
    canopy_depth = 1.6 + (variant % 3) * 0.45
    batch.add_box(f"frontage-{family}-canopy", frame_material, (x, facade_y + side * canopy_depth / 2, height - 0.35), (width * 0.72, canopy_depth, 0.22))
    batch.add_box(f"frontage-{family}-signage-blank", base_material, (x - width * 0.26, facade_y + side * 0.12, height - 0.9), (width * 0.22, 0.13, 0.55))
    batch.add_box(f"frontage-{family}-interior-counter", "timber-accent", (x, y - side * 0.8, 0.75), (width * 0.42, 0.8, 1.1))
    batch.add_box(f"frontage-{family}-interior-column", frame_material, (x + width * 0.28, y, height / 2), (0.28, 0.28, height))
    batch.add_box(f"frontage-{family}-tactile", "tactile-yellow", (door_x, facade_y + side * 1.1, 0.09), (1.45, 1.5, 0.08))
    return {"family": family, "variant": variant, "position": [x, y], "widthM": width, "depthM": depth, "interiorProxy": True, "nightState": True}


def build_frontages(batch):
    records = []
    variant = 0
    x_positions = list(range(-365, 366, 16))
    families = [family for family, count in FRONTAGE_COUNTS.items() for _ in range(count)]
    for index, family in enumerate(families):
        x = x_positions[index % len(x_positions)]
        side = -1 if index % 2 else 1
        y = side * (30 + (index % 3) * 2.5)
        records.append(build_unit(batch, family, variant, x, y, -side))
        variant += 1
    return {
        "variantContracts": FRONTAGE_COUNTS,
        "unitCount": len(records),
        "records": records,
        "activeFrontage": {"archiveWaterPlaza": 0.82, "ledgerTerrace": 0.78, "transitJunction": 0.77, "mixedCorridor": 0.67, "coreBoulevard": 0.62},
        "boxAttachmentOnly": False,
    }
