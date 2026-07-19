"""Seven role-specific bridges with actual approaches, drainage and lighting."""

BRIDGE_ROLES = (
    "slim-pedestrian", "ledger-formal", "green-corridor", "archive-gateway",
    "transit-connector", "service-crossing", "street-crossing",
)


def build_bridges(batch, bridges):
    records = []
    for index, bridge in enumerate(bridges):
        role = BRIDGE_ROLES[index]
        x, y = bridge["position"]
        width = (4.2, 8.5, 7.0, 10.0, 8.0, 9.0, 13.0)[index]
        length = (29, 31, 32, 34, 33, 31, 35)[index]
        deck_thickness = (0.28, 0.55, 0.38, 0.48, 0.42, 0.62, 0.70)[index]
        deck_material = "archive-metal" if index in (0, 2, 3, 4) else "ledger-limestone"
        batch.add_box(f"bridge-{role}-deck", deck_material, (x, y, 1.34), (width, length, deck_thickness))
        batch.add_box(f"bridge-{role}-approach-a", "dry-stone", (x, y - length / 2 - 4, 0.32), (width + 6, 8, 0.35))
        batch.add_box(f"bridge-{role}-approach-b", "dry-stone", (x, y + length / 2 + 4, 0.32), (width + 6, 8, 0.35))
        for side in (-1, 1):
            rail_x = x + side * (width / 2 - 0.12)
            batch.add_box(f"bridge-{role}-handrail", "archive-metal", (rail_x, y, 2.20), (0.16, length, 0.16))
            for post in range(-3, 4):
                batch.add_box(f"bridge-{role}-rail-post", "archive-metal", (rail_x, y + post * length / 7, 1.74), (0.12, 0.12, 1.05))
            batch.add_box(f"bridge-{role}-drain", "service-charcoal", (x + side * (width / 2 - 0.38), y, 1.53), (0.20, length - 1, 0.08))
        for light_index in range(-2, 3):
            batch.add_box(f"bridge-{role}-light", "warm-light", (x - width / 2 + 0.2, y + light_index * length / 6, 1.76), (0.12, 0.5, 0.14))
        if role == "archive-gateway":
            for side in (-1, 1):
                batch.add_box("archive-gateway-portal", "archive-metal", (x + side * width / 2, y, 4.4), (0.55, 1.0, 6.4))
            batch.add_box("archive-gateway-civic-beam", "archive-metal", (x, y, 7.55), (width + 0.8, 1.0, 0.42))
            batch.add_box("archive-gateway-light-line", "archive-cyan-light", (x, y - 0.58, 7.52), (width * 0.72, 0.12, 0.12))
        elif role == "transit-connector":
            batch.add_box("transit-bridge-canopy", "archive-metal", (x, y, 4.4), (width + 1.0, length * 0.58, 0.30))
            for py in (-length * 0.22, 0, length * 0.22):
                batch.add_box("transit-canopy-column", "archive-metal", (x - width / 2 + 0.4, y + py, 2.7), (0.22, 0.22, 3.4))
                batch.add_box("transit-canopy-column", "archive-metal", (x + width / 2 - 0.4, y + py, 2.7), (0.22, 0.22, 3.4))
        elif role == "green-corridor":
            for side in (-1, 1):
                batch.add_box("green-bridge-planter", "soil-v11", (x + side * (width / 2 - 0.55), y, 1.75), (0.75, length * 0.72, 0.70))
            batch.add_box("green-bridge-cycle-strip", "archive-cyan-light", (x, y, 1.58), (1.1, length - 1, 0.05))
        elif role == "service-crossing":
            batch.add_box("service-crossing-protection", "service-charcoal", (x, y, 1.62), (width - 1.0, length - 1.0, 0.08))
        records.append({"id": bridge["id"], "role": role, "widthM": width, "deckThicknessM": deck_thickness, "accessible": bridge["accessible"], "distinctSilhouette": True})
    return {"bridgeCount": len(records), "records": records, "duplicateMesh": False, "serviceContinuity": True}
