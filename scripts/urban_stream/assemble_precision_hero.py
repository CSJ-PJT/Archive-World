#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path

REPLACED = {
    "core-block-03-building-10", "core-block-03-building-09",
    "core-block-15-building-01", "core-block-04-building-08",
    "core-block-15-building-02", "core-block-04-building-09",
    "core-block-03-building-08", "core-block-04-building-10",
    "core-block-05-building-08", "core-block-14-building-01",
    "core-block-14-building-02", "core-block-16-building-01",
}

EXPANDED_REPLACED = {
    "core-block-06-building-08", "core-block-06-building-09",
    "core-block-07-building-08", "core-block-07-building-09",
    "core-block-07-building-10", "core-block-17-building-01",
    "core-block-18-building-01", "core-block-08-building-08",
    "core-block-08-building-09", "core-block-08-building-10",
    "core-block-09-building-08", "core-block-19-building-01",
    "core-block-20-building-01",
}

FAMILY_BY_BLOCK_ROLE = {
    "landmark-plaza": ("premium-medium-office", "institutional-archiveos-office",
                       "civic-tech-office", "cultural-public-pavilion"),
    "financial-podium": ("premium-medium-office", "compact-financial-office",
                          "corner-office-tower", "podium-office", "financial-annex"),
    "office-courtyard": ("premium-medium-office", "podium-office",
                         "civic-tech-office", "compact-financial-office"),
    "compact-office": ("compact-financial-office", "corner-office-tower",
                       "financial-annex"),
    "transit-interchange": ("transit-hall", "retail-public-podium",
                            "civic-tech-office", "compact-financial-office"),
    "retail-boulevard": ("retail-public-podium", "podium-office",
                         "financial-annex", "cultural-public-pavilion"),
    "archive-civic-tech": ("institutional-archiveos-office", "civic-tech-office",
                           "cultural-public-pavilion", "retail-public-podium"),
    "cultural-public": ("cultural-public-pavilion", "institutional-archiveos-office",
                        "retail-public-podium", "financial-annex"),
    "service-operations": ("operations-service-building", "financial-annex",
                           "compact-financial-office"),
    "park-edge-office": ("civic-tech-office", "cultural-public-pavilion",
                         "premium-medium-office", "retail-public-podium"),
    "mixed-office-retail": ("podium-office", "retail-public-podium",
                            "corner-office-tower", "financial-annex"),
    "green-gateway": ("cultural-public-pavilion", "civic-tech-office",
                      "retail-public-podium", "institutional-archiveos-office"),
}


def refine_metropolitan_instances(manifest: dict) -> dict:
    """Give existing blocks a role-specific skyline and frontage composition."""
    block_types = {block["id"]: block["type"] for block in manifest.get("blocks", [])}
    refined = 0
    for instance in manifest.get("instances", []):
        if instance.get("familyId") == "archive-cbd-twin-atrium-pq-v5":
            instance["officeV5Changed"] = False
            continue
        if not all(key in instance for key in ("familyId", "blockId", "position")):
            continue
        block_type = block_types.get(instance["blockId"])
        pool = FAMILY_BY_BLOCK_ROLE.get(block_type)
        if not pool:
            continue
        slot = int(instance["id"].rsplit("-", 1)[-1])
        block_number = int(instance["blockId"].rsplit("-", 1)[-1])
        instance["familyId"] = pool[(slot * 3 + block_number) % len(pool)]
        instance["rotationY"] = ((slot + block_number * 2) % 4) * math.pi * .5
        # Low civic/retail/service blocks create relief; financial towers retain
        # a stronger scale without widening every footprint in the grid.
        low_role = block_type in {"cultural-public", "service-operations",
                                  "green-gateway", "retail-boulevard"}
        scale_base = .70 if low_role else .76
        instance["scale"] = round(scale_base + ((slot + block_number) % 4) * .045, 3)
        instance["precisionRole"] = block_type
        instance["frontageOrientation"] = "STREAM_OR_PRIMARY_STREET"
        refined += 1
    return {"refinedInstances": refined, "roleCount": len(FAMILY_BY_BLOCK_ROLE),
            "quarterTurnVariation": True, "officeV5Changed": False}


def atomic(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2)
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def assemble(v11: Path, v12: Path, hero_version: str = "v26",
             expanded_version: str | None = None, required_score: int = 82):
    manifest = json.loads((v11 / "manifest/core-district-stream-final.json").read_text(encoding="utf-8-sig"))
    report = json.loads((v12 / f"hero-archive/archive-water-plaza-hero-{hero_version}-report.json").read_text(encoding="utf-8-sig"))
    original = len(manifest["instances"])
    manifest["instances"] = [instance for instance in manifest["instances"] if instance["id"] not in REPLACED]
    assert original - len(manifest["instances"]) == 12
    expanded_report = None
    if expanded_version:
        expanded_report_path = (v12 / "hero-expanded" /
                                f"core-stream-ledger-transit-{expanded_version}-report.json")
        expanded_report = json.loads(expanded_report_path.read_text(encoding="utf-8-sig"))
        before_expanded = len(manifest["instances"])
        manifest["instances"] = [
            instance for instance in manifest["instances"]
            if instance["id"] not in EXPANDED_REPLACED
        ]
        assert before_expanded - len(manifest["instances"]) == len(EXPANDED_REPLACED)
    composition = refine_metropolitan_instances(manifest)
    manifest["schemaVersion"] = 4
    manifest["status"] = ("GENERATED_CORE_STREAM_PRECISION_ALL_ZONES"
                          if expanded_report else "GENERATED_CORE_STREAM_PRECISION_HERO_A")
    manifest["badges"] = [
        "PRECISION ALL CORE STREAM ZONES" if expanded_report else "PRECISION HERO ZONE A",
        "NOT CANONICAL", "NOT V3 APPLIED",
    ]
    manifest["heroZones"] = [{
        "id": "archive-water-plaza", "status": f"REVISION_{report['revision']}_PENDING_VISUAL_GATE",
        "uri": f"hero-archive/archive-water-plaza-hero-{hero_version}.glb", "actual3D": True,
        "performanceUri": f"hero-archive/archive-water-plaza-hero-{hero_version}-lod2.glb",
        "buildingCount": report["buildingCount"], "replacedInstanceIds": sorted(REPLACED),
        "radiusM": 155, "streetEyePriority": True, "officeV5Changed": False,
        "geometry": report["geometry"], "lobbies": report["lobbyCount"],
        "retailPublicBays": report["retailPublicBayCount"], "humans": report["humanCount"],
        "trees": report["treeCount"], "nightState": True,
    }]
    if expanded_report:
        manifest["heroZones"].append({
            "id": "ledger-transit-corridor",
            "status": f"REVISION_{expanded_report['revision']}_PENDING_VISUAL_GATE",
            "uri": f"hero-expanded/core-stream-ledger-transit-{expanded_version}.glb",
            "performanceUri": f"hero-expanded/core-stream-ledger-transit-{expanded_version}-lod2.glb",
            "actual3D": True,
            "buildingCount": expanded_report["buildingCount"],
            "replacedInstanceIds": sorted(EXPANDED_REPLACED),
            "zones": expanded_report["zones"],
            "streetEyePriority": True,
            "officeV5Changed": False,
            "geometry": expanded_report["geometry"],
            "humans": expanded_report["life"]["humanCount"],
            "trees": expanded_report["life"]["treeCount"],
            "nightState": True,
            "streamContinuity": expanded_report["corridor"],
        })
    expanded_buildings = expanded_report["buildingCount"] if expanded_report else 0
    manifest["metrics"].update({
        "batchedSupportInstances": len(manifest["instances"]), "heroZoneBuildings": 6,
        "expandedSupportInstances": expanded_buildings,
        "buildingInstances": len(manifest["instances"]) + 6 + expanded_buildings,
        "archiveHeroTriangles": report["geometry"]["triangles"],
        "archiveHeroHumanCount": report["humanCount"], "archiveHeroTreeCount": report["treeCount"],
    })
    manifest["precision"] = {
        "mode": "ALL_CORE_STREAM_ZONES" if expanded_report else "HERO_ZONE_SEQUENTIAL",
        "currentZone": "all-core-stream-zones" if expanded_report else "archive-water-plaza",
        "revision": max(report["revision"], expanded_report["revision"] if expanded_report else 0),
        "nextZoneLocked": not bool(expanded_report), "requiredScore": required_score,
        "qualityTarget": report.get("qualityTarget", {"grade": "B", "minimumScore": required_score}),
        "groundPlaneStreamOpening": True, "directReferenceCopy": False,
        "metropolitanComposition": composition,
    }
    atomic(v12 / "manifest/core-district-stream-precision.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--v11", type=Path, required=True)
    parser.add_argument("--v12", type=Path, required=True)
    parser.add_argument("--hero-version", default="v26")
    parser.add_argument("--expanded-version")
    parser.add_argument("--required-score", type=int, default=82)
    args = parser.parse_args()
    result = assemble(args.v11, args.v12, args.hero_version,
                      args.expanded_version, args.required_score)
    print(json.dumps({"status": "PASS", "batchedInstances": len(result["instances"]),
                      "heroBuildings": sum(zone["buildingCount"] for zone in result["heroZones"]),
                      "actualBuildings": result["metrics"]["buildingInstances"]}))
