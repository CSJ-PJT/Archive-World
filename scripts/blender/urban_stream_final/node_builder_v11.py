"""Three primary nodes and four genuinely distinct pocket places."""


def light_line(batch, role, x, y, count, spacing, cyan=False):
    material = "archive-cyan-light" if cyan else "warm-light"
    for index in range(count):
        batch.add_box(role, material, (x + (index - (count - 1) / 2) * spacing, y, 0.24), (spacing * 0.52, 0.16, 0.18))


def build_nodes(batch):
    # Archive Water Plaza: civic event surface, stepped water edge and portal pavilion.
    batch.add_box("archive-event-plaza", "archive-warm-stone", (-240, -22, 0.18), (92, 30, 0.36))
    for step in range(5):
        batch.add_box("archive-water-step", "wet-stone", (-240, -6 - step * 1.15, 0.16 + step * 0.22), (66 - step * 3.0, 1.1, 0.28))
    batch.add_box("archive-pavilion-roof", "archive-metal", (-263, -23, 5.0), (26, 12, 0.38))
    for x in (-274, -265, -256, -247):
        batch.add_box("archive-pavilion-column", "archive-metal", (x, -23, 2.5), (0.34, 0.34, 5.0))
    batch.add_box("archive-pavilion-glass", "blue-gray-glass", (-260.5, -28.8, 2.35), (25, 0.22, 4.2))
    batch.add_box("archive-information-wall", "ledger-granite", (-210, -24, 2.3), (16, 0.7, 4.6))
    light_line(batch, "archive-restrained-light-line", -240, -36, 9, 7, cyan=True)

    # Ledger Terrace: narrow planting, lunch terraces and a formal bridge landing.
    batch.add_box("ledger-formal-terrace", "ledger-limestone", (60, 21, 0.24), (84, 28, 0.48))
    for tier in range(4):
        batch.add_box("ledger-terrace-step", "wet-stone", (60, 7 + tier * 1.2, 0.18 + tier * 0.24), (70 - tier * 4, 1.15, 0.28))
    for index in range(5):
        batch.add_box("ledger-lunch-table", "timber-accent", (30 + index * 14, 25, 0.78), (2.4, 1.2, 0.14))
        for side in (-1, 1):
            batch.add_box("ledger-lunch-seat", "timber-accent", (30 + index * 14, 25 + side * 1.2, 0.52), (2.0, 0.5, 0.55))
    batch.add_box("ledger-shade-canopy", "ledger-bronze", (60, 28, 4.1), (55, 8, 0.32))
    for x in (35, 47, 59, 71, 83):
        batch.add_box("ledger-canopy-column", "ledger-bronze", (x, 28, 2.05), (0.26, 0.26, 4.1))
    light_line(batch, "ledger-warm-edge", 60, 8, 8, 7)

    # Transit Junction: two entries, protected waiting zone and barrier-free connection.
    batch.add_box("transit-transfer-plaza", "promenade-paver", (260, -22, 0.16), (86, 31, 0.32))
    for entry_x in (238, 282):
        batch.add_box("station-entry-volume", "blue-gray-glass", (entry_x, -27, 3.1), (16, 9, 6.2))
        batch.add_box("station-entry-canopy", "archive-metal", (entry_x, -34, 4.8), (20, 8, 0.34))
        batch.add_box("station-wayfinding-blank", "warm-interior", (entry_x, -35, 3.0), (5.2, 0.18, 1.2))
    batch.add_box("transit-waiting-canopy", "archive-metal", (260, -10, 4.0), (42, 8, 0.30))
    batch.add_wedge("transit-barrier-free-ramp", "promenade-paver", (292, -8, 1.1), (22, 5, 2.2))
    light_line(batch, "transit-approach-light", 260, -2, 7, 7, cyan=True)

    pockets = (
        ("quiet-garden", -345, 18), ("cafe-terrace", -120, -20),
        ("performance-step", 160, 20), ("wetland-observation", 345, -18),
    )
    for index, (kind, x, y) in enumerate(pockets):
        batch.add_box(f"pocket-{kind}-surface", "dry-stone", (x, y, 0.14), (24 + index * 2, 15 + index, 0.28))
        batch.add_box(f"pocket-{kind}-seat", "timber-accent", (x - 4, y, 0.55), (7, 1.1, 0.65))
        batch.add_box(f"pocket-{kind}-planter", "soil-v11", (x + 5, y + 2, 0.55), (7, 4, 1.1))
        if kind == "performance-step":
            for step in range(3):
                batch.add_box("pocket-performance-tier", "ledger-limestone", (x, y - 4 - step, 0.25 + step * 0.25), (14 - step * 2, 1.0, 0.3))
        if kind == "wetland-observation":
            batch.add_box("pocket-observation-deck", "timber-accent", (x, y - 5, 0.38), (18, 5, 0.4))
    return {"majorNodes": 3, "pocketNodes": 4, "distinctNodeTypes": 7, "archiveWaterPlaza": True, "ledgerStreamTerrace": True, "transitStreamJunction": True}
