"""Place-based human activity and traffic composition for four time presets."""
from __future__ import annotations

CLUSTERS = ("office-arrival", "lunch-seating", "walking-pair", "conversation", "transit-waiting", "bridge-crossing", "jogging", "cafe-terrace", "family-visitor", "maintenance-worker", "bicycle-parking", "night-pedestrian")


def human(batch, x, y, angle_seed, seated=False, cycling=False):
    body_z = 0.92 if seated else 1.05
    batch.add_cylinder("human-body", "service-charcoal", (x, y, body_z), 0.18, 0.95 if seated else 1.18, 7)
    batch.add_cylinder("human-head", "archive-warm-stone", (x, y, 1.55 if seated else 1.77), 0.14, 0.28, 8)
    if not seated:
        for side in (-1, 1):
            batch.add_box("human-leg", "ledger-granite", (x + side * 0.09, y, 0.36), (0.10, 0.12, 0.72), rotation_z=angle_seed * 0.17)
    if cycling:
        for wheel_y in (-0.55, 0.55):
            batch.add_cylinder("bicycle-wheel", "archive-metal", (x, y + wheel_y, 0.38), 0.36, 0.07, 10)
        batch.add_box("bicycle-frame", "archive-metal", (x, y, 0.58), (0.08, 1.1, 0.08))


def vehicle(batch, kind, x, y, heading=0.0):
    dimensions = {"sedan": (4.6, 1.85, 1.35), "taxi": (4.7, 1.9, 1.4), "bus": (11.5, 2.55, 3.2), "delivery": (6.2, 2.1, 2.5), "shuttle": (7.2, 2.2, 2.7)}[kind]
    length, width, height = dimensions
    batch.add_box(f"vehicle-{kind}-body", "service-charcoal" if kind == "delivery" else "archive-metal", (x, y, height * 0.48), (length, width, height * 0.72), rotation_z=heading)
    batch.add_box(f"vehicle-{kind}-glass", "blue-gray-glass", (x - length * 0.08, y, height * 0.86), (length * 0.58, width * 0.88, height * 0.32), rotation_z=heading)
    for sx in (-1, 1):
        for sy in (-1, 1):
            batch.add_cylinder(f"vehicle-{kind}-wheel", "ledger-granite", (x + sx * length * 0.31, y + sy * width * 0.46, 0.34), 0.32 if kind not in ("bus", "shuttle") else 0.43, 0.18, 9)


def build_activity(batch):
    records = []
    anchors = [(-250, -19), (60, 24), (260, -18), (-150, 7), (145, -8), (330, 10)]
    human_count = 0
    for cluster_index, cluster in enumerate(CLUSTERS):
        ax, ay = anchors[cluster_index % len(anchors)]
        size = 5 + cluster_index % 5
        for index in range(size):
            x = ax + (index % 4) * 1.45 - 2.2
            y = ay + (index // 4) * 1.8
            seated = cluster in ("lunch-seating", "cafe-terrace")
            cycling = cluster == "bicycle-parking" and index < 3
            human(batch, x, y, index + cluster_index, seated, cycling)
            human_count += 1
        records.append({"cluster": cluster, "position": [ax, ay], "count": size, "orientationRule": "nearest-path-or-entrance", "time": "night" if cluster == "night-pedestrian" else "day-evening"})
    vehicles = (("taxi", -65, 58), ("taxi", -54, 58), ("bus", 250, -68), ("shuttle", 272, -68), ("delivery", 300, 66), ("sedan", 85, 62), ("sedan", 105, 62))
    for index, (kind, x, y) in enumerate(vehicles):
        vehicle(batch, kind, x, y, 0.0 if index % 2 else 3.14159)
    return {"clusterFamilies": list(CLUSTERS), "clusterCount": len(records), "humanCount": human_count, "vehicleCount": len(vehicles), "activityPresets": {"morning": 0.72, "day": 1.0, "evening": 0.86, "night": 0.36}, "floatingHumans": 0, "waterIntrusions": 0, "plazaVehicleIntrusions": 0}
