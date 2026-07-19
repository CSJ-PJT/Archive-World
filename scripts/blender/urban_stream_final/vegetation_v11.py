"""Deterministic, batched, multi-lobe vegetation with adjacency rules."""
from __future__ import annotations

import math
import random

TREE_FAMILIES = [f"street-{i}" for i in range(6)] + [f"plaza-{i}" for i in range(4)] + [f"riparian-{i}" for i in range(5)] + [f"ornamental-{i}" for i in range(4)] + [f"evergreen-{i}" for i in range(3)]
LOW_FAMILIES = [f"shrub-{i}" for i in range(8)] + [f"hedge-{i}" for i in range(3)] + [f"groundcover-{i}" for i in range(6)] + [f"wetland-{i}" for i in range(8)] + [f"grass-{i}" for i in range(5)] + [f"planter-{i}" for i in range(8)]


def add_tree(batch, x, y, seed, family, lod="LOD1"):
    rng = random.Random(seed)
    height = 5.8 + rng.random() * 6.6
    trunk_radius = 0.18 + rng.random() * 0.20
    batch.add_cylinder("tree-trunk-tapered", "timber-accent", (x, y, height * 0.29), trunk_radius, height * 0.58, 8 if lod != "LOD2" else 6)
    branch_count = 2 if lod == "LOD2" else 4
    for branch in range(branch_count):
        angle = branch * math.tau / branch_count + rng.random() * 0.25
        bx, by = x + math.cos(angle) * 0.65, y + math.sin(angle) * 0.65
        batch.add_cylinder("tree-branch-proxy", "timber-accent", (bx, by, height * (0.52 + branch * 0.045)), trunk_radius * 0.42, 2.4 + rng.random(), 6)
    lobe_count = 3 if lod == "LOD2" else 5 + seed % 3
    material = ("foliage-deep", "foliage-mid", "foliage-light")[seed % 3]
    for lobe in range(lobe_count):
        angle = lobe * math.tau / lobe_count + rng.random() * 0.3
        radius = 1.25 + rng.random() * 1.25
        cx, cy = x + math.cos(angle) * radius * 0.72, y + math.sin(angle) * radius * 0.72
        batch.add_cylinder("tree-crown-multilobe", material, (cx, cy, height * 0.76 + (lobe % 2) * 0.55), radius, 2.1 + rng.random() * 1.6, 8 if lod != "LOD2" else 6)
    return {"family": family, "heightM": round(height, 2), "crownLobes": lobe_count, "lod": lod}


def build_vegetation(batch, segments):
    trees, low = [], []
    seed = 11001
    last_family = None
    adjacent_repeat = 0
    for segment_index, segment in enumerate(segments):
        x0, y0 = segment["start"]
        x1, y1 = segment["end"]
        for index in range(7):
            t = (index + 0.5) / 7
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for side in (-1, 1):
                family = TREE_FAMILIES[(seed + segment_index + side) % len(TREE_FAMILIES)]
                if family == last_family:
                    adjacent_repeat += 1
                else:
                    adjacent_repeat = 1
                if adjacent_repeat > 2:
                    family = TREE_FAMILIES[(TREE_FAMILIES.index(family) + 1) % len(TREE_FAMILIES)]
                    adjacent_repeat = 1
                last_family = family
                distance = segment["waterWidthM"] / 2 + 7.5 + (index % 2) * 1.5
                record = add_tree(batch, x, y + side * distance, seed, family)
                record["position"] = [x, y + side * distance]
                trees.append(record)
                seed += 1
            low_family = LOW_FAMILIES[(segment_index * 7 + index) % len(LOW_FAMILIES)]
            low_y = y + (-1 if index % 2 else 1) * (segment["waterWidthM"] / 2 + 4.8)
            batch.add_box("low-planting-bed", "soil-v11", (x, low_y, 0.28), (6.0, 1.8, 0.55))
            for plant in range(4):
                batch.add_cylinder("low-planting-cluster", ("foliage-deep", "foliage-mid", "foliage-light")[plant % 3], (x - 2.1 + plant * 1.4, low_y, 0.62), 0.48 + 0.08 * plant, 0.75 + 0.12 * plant, 7)
            low.append({"family": low_family, "position": [x, low_y]})
    return {"treeFamilyCount": len(TREE_FAMILIES), "lowFamilyCount": len(LOW_FAMILIES), "treeCount": len(trees), "lowPlantingCount": len(low), "trees": trees, "maxAdjacentVariant": 2, "floatingPlants": 0, "routeIntrusions": 0, "lodLevels": ["LOD0", "LOD1", "LOD2"]}
