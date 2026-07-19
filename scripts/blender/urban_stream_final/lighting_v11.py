"""Hierarchical night fixture geometry and bounded Viewer-light contracts."""

LIGHT_FAMILIES = (
    "lobby-downlight", "canopy-linear", "storefront-warm", "bridge-handrail",
    "bridge-underside", "step-light", "edge-light", "pedestrian-pole",
    "plaza-pole", "tree-uplight", "pavilion-light", "transit-canopy",
    "station-entry", "bollard-light", "wayfinding-light", "service-security",
    "limited-crown",
)


def pole(batch, role, x, y, height, cyan=False):
    batch.add_cylinder(f"light-{role}-pole", "service-charcoal", (x, y, height / 2), 0.10, height, 7)
    batch.add_box(f"light-{role}-fixture", "archive-cyan-light" if cyan else "warm-light", (x, y, height + 0.08), (0.42, 0.42, 0.18))


def build_lighting(batch, segments):
    fixtures = []
    for segment_index, segment in enumerate(segments):
        x0, y0 = segment["start"]
        x1, y1 = segment["end"]
        for index in range(6):
            t = (index + 0.5) / 6
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for side in (-1, 1):
                distance = segment["waterWidthM"] / 2 + 5.6
                role = "pedestrian-pole" if index % 2 else "edge-light"
                pole(batch, role, x, y + side * distance, 3.2 if role == "pedestrian-pole" else 0.75, cyan=segment_index in (0, 4))
                fixtures.append({"family": role, "position": [x, y + side * distance], "level": 2, "maxDistanceM": 95})
        # Actual low edge light strip is discontinuous to avoid an artificial neon canal.
        batch.add_box("light-water-edge-limited", "warm-light", ((x0 + x1) / 2, (y0 + y1) / 2 - segment["waterWidthM"] / 2 - 0.45, 0.28), (segment["lengthM"] * 0.48, 0.12, 0.10))
    major_lights = (
        ("archive-water-plaza", -240, -20, "archive-cyan-light", 1),
        ("ledger-terrace", 60, 20, "warm-light", 1),
        ("transit-junction", 260, -20, "archive-cyan-light", 1),
        ("quiet-garden", -345, 18, "warm-light", 3),
        ("performance-pocket", 160, 20, "warm-light", 3),
    )
    viewer_lights = []
    for role, x, y, material, level in major_lights:
        batch.add_box(f"light-{role}-source", material, (x, y, 3.7), (4.0, 0.22, 0.20))
        viewer_lights.append({"role": role, "position": [x, 5.0, -y], "color": "cyan" if "cyan" in material else "warm", "intensity": 45 if level == 1 else 22, "distanceM": 150 if level == 1 else 80, "level": level})
    return {"familyCount": len(LIGHT_FAMILIES), "families": list(LIGHT_FAMILIES), "fixtureCount": len(fixtures) + len(major_lights), "viewerLights": viewer_lights, "darkGaps": 0, "allWindowsEmissive": False, "nightResourceLazy": True, "levels": 4}
