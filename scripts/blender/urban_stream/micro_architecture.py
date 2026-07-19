"""Human-scale frontages that turn the stream banks into occupied city edges."""

FRONTAGE_TYPES = (
    "archive-lobby",
    "ledger-lobby",
    "retail-bay",
    "community-bay",
    "cafe-pavilion",
    "covered-arcade",
    "bicycle-facility",
    "help-pavilion",
    "service-enclosure",
)


def build_frontage_unit(batch, kind, x, y, faces_stream=True):
    side = -1 if y > 0 else 1
    width = 12 if "lobby" in kind else 8
    depth = 5.5 if "pavilion" not in kind else 7
    facade_y = y + side * depth / 2
    batch.add_box(f"{kind}-base", "warm-stone", (x, y, 0.18), (width, depth, 0.36))
    batch.add_box(f"{kind}-frame", "dark-granite", (x, y, 2.4), (width, depth, 0.28))
    for column_x in (-width / 2 + 0.35, width / 2 - 0.35):
        batch.add_box(f"{kind}-column", "steel", (x + column_x, facade_y, 2.25), (0.35, 0.35, 4.5))
    batch.add_box(f"{kind}-glazing", "glass", (x, facade_y, 2.05), (width - 1.1, 0.24, 3.45))
    batch.add_box(f"{kind}-door", "service-metal", (x, facade_y + side * 0.16, 1.25), (1.7, 0.18, 2.5))
    canopy_depth = 2.2 if "lobby" in kind else 1.35
    batch.add_box(
        f"{kind}-canopy",
        "steel",
        (x, facade_y + side * canopy_depth / 2, 3.25),
        (width * 0.7, canopy_depth, 0.24),
    )
    batch.add_box(
        f"{kind}-blank-signage",
        "pale-stone",
        (x + width * 0.27, facade_y + side * 0.18, 3.55),
        (width * 0.22, 0.14, 0.65),
    )
    batch.add_box(f"{kind}-tactile", "paving", (x, facade_y + side * 1.45, 0.08), (2.4, 2.1, 0.12))
    return 1


def build_micro_architecture(batch):
    placements = []
    x_positions = (-345, -300, -250, -195, -140, -85, -25, 35, 95, 155, 215, 275, 330)
    for index, x in enumerate(x_positions):
        kind = FRONTAGE_TYPES[index % len(FRONTAGE_TYPES)]
        y = 30 if index % 2 == 0 else -31
        build_frontage_unit(batch, kind, x, y)
        placements.append({"kind": kind, "position": [x, y], "streamFacing": True})
    # Additional transparent community/cafe units reinforce the three primary nodes.
    for kind, x, y in (
        ("archive-lobby", -255, 31),
        ("cafe-pavilion", 48, -32),
        ("ledger-lobby", 82, 31),
        ("bicycle-facility", 245, -32),
        ("help-pavilion", 280, 31),
    ):
        build_frontage_unit(batch, kind, x, y)
        placements.append({"kind": kind, "position": [x, y], "streamFacing": True})
    return {
        "unitCount": len(placements),
        "familyCount": len(set(item["kind"] for item in placements)),
        "placements": placements,
        "doors": len(placements),
        "canopies": len(placements),
        "glazedFrontages": len(placements),
        "blankSignagePanels": len(placements),
    }
