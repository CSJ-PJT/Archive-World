#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def atomic(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2)
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def assemble(v11: Path, v12: Path):
    manifest = json.loads((v11 / "manifest/core-district-stream-final.json").read_text(encoding="utf-8-sig"))
    report = json.loads((v12 / "hero-archive/archive-water-plaza-hero-v26-report.json").read_text(encoding="utf-8-sig"))
    original = len(manifest["instances"])
    manifest["instances"] = [instance for instance in manifest["instances"] if instance["id"] not in REPLACED]
    assert original - len(manifest["instances"]) == 12
    manifest["schemaVersion"] = 4
    manifest["status"] = "GENERATED_CORE_STREAM_PRECISION_HERO_A"
    manifest["badges"] = ["PRECISION HERO ZONE A", "NOT CANONICAL", "NOT V3 APPLIED"]
    manifest["heroZones"] = [{
        "id": "archive-water-plaza", "status": f"REVISION_{report['revision']}_PENDING_VISUAL_GATE",
        "uri": "hero-archive/archive-water-plaza-hero-v26.glb", "actual3D": True,
        "buildingCount": report["buildingCount"], "replacedInstanceIds": sorted(REPLACED),
        "radiusM": 155, "streetEyePriority": True, "officeV5Changed": False,
        "geometry": report["geometry"], "lobbies": report["lobbyCount"],
        "retailPublicBays": report["retailPublicBayCount"], "humans": report["humanCount"],
        "trees": report["treeCount"], "nightState": True,
    }]
    manifest["metrics"].update({
        "batchedSupportInstances": len(manifest["instances"]), "heroZoneBuildings": 6,
        "buildingInstances": len(manifest["instances"]) + 6,
        "archiveHeroTriangles": report["geometry"]["triangles"],
        "archiveHeroHumanCount": report["humanCount"], "archiveHeroTreeCount": report["treeCount"],
    })
    manifest["precision"] = {
        "mode": "HERO_ZONE_SEQUENTIAL", "currentZone": "archive-water-plaza",
        "revision": 4, "nextZoneLocked": True, "requiredScore": 82,
        "groundPlaneStreamOpening": True, "directReferenceCopy": False,
    }
    atomic(v12 / "manifest/core-district-stream-precision.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--v11", type=Path, required=True)
    parser.add_argument("--v12", type=Path, required=True)
    args = parser.parse_args()
    result = assemble(args.v11, args.v12)
    print(json.dumps({"status": "PASS", "batchedInstances": len(result["instances"]), "heroBuildings": 6, "actualBuildings": result["metrics"]["buildingInstances"]}))
