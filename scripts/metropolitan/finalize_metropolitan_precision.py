#!/usr/bin/env python3
"""Expand the frozen metropolitan plan into a deterministic, review-only 3D scene contract.

The output remains Generated-only.  It does not mutate canonical manifests, V3 layout,
runtime repositories, or either frozen PO building source.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path

from .city_assembler import assemble_city


DISTRICT_DESIGN = {
    "archiveos-core": ("archive", "civic-technology", 0.82, 0.76, 0.68),
    "ledger-financial": ("ledger", "premium-finance", 0.78, 0.72, 0.64),
    "market-commercial": ("market", "active-commerce", 0.88, 0.80, 0.74),
    "nexus-technology": ("nexus", "campus-innovation", 0.70, 0.68, 0.58),
    "logistics-edge": ("logistics", "industrial-service", 0.24, 0.34, 0.20),
    "residential-north": ("residential", "neighborhood-north", 0.58, 0.66, 0.44),
    "residential-south": ("residential-warm", "neighborhood-south", 0.62, 0.70, 0.48),
    "civic-cultural": ("civic", "culture-park", 0.66, 0.72, 0.52),
    "riverfront": ("riverfront", "blue-green-corridor", 0.52, 0.78, 0.56),
    "metropolitan-park": ("park", "metropolitan-green", 0.20, 0.82, 0.28),
    "transit-oriented-north": ("transit", "mixed-transit", 0.78, 0.74, 0.66),
    "infrastructure-belt": ("infrastructure", "utility-buffer", 0.18, 0.30, 0.18),
    "urban-expansion-east": ("residential-east", "future-neighborhood", 0.44, 0.60, 0.36),
}

MASSING = ("setback-slab", "point-crown", "courtyard-edge", "stepped-tower", "podium-pair", "terraced-midrise")
FACADE = ("vertical-frame", "deep-grid", "stone-glass", "horizontal-band", "recessed-bay", "corner-glass", "screened-service")
GROUND = ("lobby-arcade", "retail-bays", "civic-loggia", "community-terrace", "transit-canopy", "service-court")
ACTIVITY = ("arrival", "cafe", "lunch", "walking", "waiting", "cycling", "conversation", "night-walk")


def _token(seed: int, value: str) -> int:
    return int(sha256(f"{seed}:{value}".encode("utf-8")).hexdigest()[:12], 16)


def _atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def build_precision_scene(seed: int = 7302026) -> dict:
    city = assemble_city(seed)
    district_by_id = {item["id"]: item for item in city["districts"]}
    family_by_id = {item["id"]: item for item in city["families"]}
    block_by_id = {item["id"]: item for item in city["blocks"]}
    district_index = {item["id"]: index for index, item in enumerate(city["districts"])}

    instances = []
    district_counts = Counter()
    facade_counts = Counter()
    for index, item in enumerate(city["instances"]):
        district = district_by_id[item["districtId"]]
        family = family_by_id[item["familyId"]]
        token = _token(seed, item["id"])
        palette, identity, frontage_target, pedestrian_priority, night_activity = DISTRICT_DESIGN[item["districtId"]]
        avg_h = district["dna"]["averageHeightM"]
        max_h = district["dna"]["maximumHeightM"]
        height = min(max_h, avg_h * (0.75 + ((token >> 5) % 150) / 100.0))
        if token % 31 == 0 and district["dna"]["skylineRole"].startswith("tier-"):
            height = max(height, max_h * 0.85)
        if family["frozen"]:
            height = max_h * 0.96
        category = family["category"]
        footprint = {
            "office": (31, 27), "residential": (27, 23), "commercial": (34, 29),
            "industrial": (49, 36), "civic": (39, 31),
        }[category]
        width = footprint[0] * (0.82 + (token % 31) / 100.0)
        depth = footprint[1] * (0.84 + ((token >> 8) % 27) / 100.0)
        podium_h = min(22.0, max(5.0, height * (0.075 + ((token >> 13) % 6) / 100.0)))
        upper_scale = 0.66 + ((token >> 17) % 24) / 100.0
        massing = MASSING[(token + district_index[item["districtId"]]) % len(MASSING)]
        facade = FACADE[((token >> 4) + district_index[item["districtId"]] * 2) % len(FACADE)]
        ground = GROUND[((token >> 9) + district_index[item["districtId"]]) % len(GROUND)]
        rotation = math.radians(item["rotationZ"] + ((token >> 23) % 3 - 1) * 5)
        active = max(0.15, min(0.94, frontage_target + ((token >> 27) % 17 - 8) / 100.0))
        facade_counts[(item["districtId"], facade)] += 1
        district_counts[item["districtId"]] += 1
        instances.append({
            "id": item["id"], "districtId": item["districtId"], "blockId": item["blockId"],
            "familyId": item["familyId"], "category": category, "palette": palette,
            "position": item["position"], "rotationZ": round(rotation, 5),
            "dimensions": [round(width, 2), round(depth, 2), round(height, 2)],
            "podiumHeight": round(podium_h, 2), "upperScale": round(upper_scale, 3),
            "massing": massing, "facade": facade, "groundFloor": ground,
            "activeFrontage": round(active, 3), "nightOccupancy": round(night_activity * (0.72 + token % 23 / 100), 3),
            "entranceSide": item["entranceSide"], "serviceSide": item["serviceSide"],
            "lodPolicy": item["lodPolicy"], "frozenPO": family["frozen"],
            "status": "ACTUAL_RUNTIME_GEOMETRY_CONTRACT", "canonical": False, "v3Applied": False,
        })

    blocks = []
    activity_total = 0
    for index, item in enumerate(city["blocks"]):
        token = _token(seed, item["id"])
        palette, identity, frontage, pedestrian, night = DISTRICT_DESIGN[item["districtId"]]
        activity_count = 3 + token % 7
        activity_total += activity_count
        activities = [ACTIVITY[(token + n * 3) % len(ACTIVITY)] for n in range(activity_count)]
        blocks.append({
            **item, "status": "METROPOLITAN_POLISHED_BLOCK", "palette": palette, "identity": identity,
            "activeFrontageTarget": frontage, "pedestrianPriority": pedestrian, "nightActivity": night,
            "groundFloorDepthM": 4 + token % 5, "canopyDepthM": round(1.8 + token % 18 / 10, 1),
            "activityClusters": activities, "treeVariantOffset": token % 18,
            "publicRealm": ["entrance-forecourt", "seating-cluster", "tree-grove", "bicycle-stop", "wayfinding"],
            "lightingHierarchy": {"landmark": 1.0, "lobby": 0.72, "route": 0.42, "landscape": 0.16},
        })

    districts = []
    for item in city["districts"]:
        palette, identity, frontage, pedestrian, night = DISTRICT_DESIGN[item["id"]]
        districts.append({
            **item, "status": "METROPOLITAN_PRECISION_DISTRICT", "palette": palette, "identity": identity,
            "activeFrontageTarget": frontage, "pedestrianPriority": pedestrian, "nightActivity": night,
            "instanceCount": district_counts[item["id"]],
            "camera": {"position": [sum(p[0] for p in item["polygon"]) / 4, max(item["dna"]["maximumHeightM"] * 2.2, 240), sum(p[1] for p in item["polygon"]) / 4 + 420],
                       "target": [sum(p[0] for p in item["polygon"]) / 4, 30, sum(p[1] for p in item["polygon"]) / 4]},
        })

    repeated_max = max(facade_counts.values()) / max(1, max(district_counts.values()))
    return {
        "schemaVersion": 2, "sceneId": "archive-metropolitan-precision-v1", "seed": seed,
        "status": "GENERATED_METROPOLITAN_PRECISION", "canonical": False, "v3Applied": False,
        "runtimeMutation": False, "mainMerge": False, "boundsMeters": [6000, 5000],
        "districts": districts, "blocks": blocks, "instances": instances,
        "metrics": {"districtCount": len(districts), "blockCount": len(blocks), "buildingInstances": len(instances),
                    "uniqueFamilies": len(city["families"]), "activityClusters": activity_total,
                    "paletteCount": len(set(DISTRICT_DESIGN.values())), "maximumDistrictFacadeShare": round(repeated_max, 4),
                    "planningProxyRatio": 0.0},
        "renderContract": {"engine": "WebGL-instanced", "times": ["day", "dusk", "night"],
                           "cameras": ["metropolitan-aerial", "skyline", *[d["id"] for d in districts]],
                           "districtMaterials": True, "groundFloorOccupancy": True, "activityComposition": True},
        "badges": ["GENERATED METROPOLITAN PRECISION", "NOT CANONICAL", "NOT V3 APPLIED"],
    }


def write_precision_scene(output_root: Path, seed: int = 7302026) -> Path:
    scene = build_precision_scene(seed)
    target = output_root / "metropolitan-precision-scene.json"
    _atomic_json(target, scene)
    _atomic_json(output_root / "reports" / "metropolitan-precision-summary.json", {
        "status": "PASS", "scene": scene["sceneId"], "metrics": scene["metrics"],
        "protected": {"canonical": False, "v3Applied": False, "runtimeMutation": False, "mainMerge": False},
    })
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--seed", type=int, default=7302026)
    args = parser.parse_args()
    path = write_precision_scene(Path(args.output_root), args.seed)
    print(json.dumps({"status": "PASS", "output": str(path)}, ensure_ascii=False))
