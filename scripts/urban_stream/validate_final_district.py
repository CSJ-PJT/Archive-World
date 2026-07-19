#!/usr/bin/env python3
"""Validate the generated-only V11 Core + Urban Stream finalization contract."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def validate(root: Path) -> dict:
    manifest = read(root / "manifest/core-district-stream-final.json")
    generation = read(root / "stream/final-stream-generation-report.json")
    alignment = read(root / "stream/alignment.json")
    glbs = sorted(root.glob("families/**/*.glb")) + sorted(root.glob("infrastructure/*.glb")) + sorted(root.glob("stream/*.glb"))
    active = manifest["urbanStream"]["activeFrontage"]
    sections = generation["sections"]["sectionTypes"]
    section_records = generation["sections"]["records"]
    checks = {
        "generatedOnlyStatus": manifest["status"] == "GENERATED_CORE_URBAN_STREAM_FINALIZATION",
        "actualGlbCount38": len(glbs) == 38,
        "allGlbNonEmpty": all(path.stat().st_size > 1024 for path in glbs),
        "actualFamilies12": manifest["metrics"]["actualFamilies"] == 12,
        "actualBlocks22": manifest["metrics"]["actualBlocks"] == 22,
        "actualInstances220": len(manifest["instances"]) == 220,
        "planningProxyZero": manifest["metrics"]["planningProxyRatio"] == 0,
        "officeV5Frozen": not manifest["finalization"]["officeV5Changed"],
        "supportFamiliesRebuilt11": manifest["finalization"]["supportBodiesRebuilt"] == 11,
        "supportInstancesAffected": manifest["finalization"]["supportInstancesAffected"] == 219,
        "streamLength": alignment["lengthM"] >= 650,
        "sectionTypes7": len(sections) == 7,
        "sectionDepth": all(section["upperStreetElevationM"] > section["lowerPromenadeElevationM"] > section["waterLevelM"] > section["bedLevelM"] for section in section_records) and not generation["sections"]["flatSingleDepth"],
        "bridges7": manifest["urbanStream"]["bridges"] == 7,
        "access8": manifest["urbanStream"]["accessPoints"] == 8,
        "frontage41": manifest["urbanStream"]["frontageUnits"] == 41,
        "frontageTargets": active["archiveWaterPlaza"] >= .80 and active["ledgerTerrace"] >= .75 and active["transitJunction"] >= .75 and active["mixedCorridor"] >= .65 and active["coreBoulevard"] >= .60,
        "vegetationFamilies": manifest["urbanStream"]["treeFamilies"] >= 22 and manifest["urbanStream"]["lowPlantingFamilies"] >= 38,
        "activityComposition": manifest["urbanStream"]["humanCount"] >= 80 and manifest["urbanStream"]["vehicleCount"] >= 7,
        "lightHierarchy": manifest["urbanStream"]["lightFamilies"] == 17 and manifest["graphs"]["streamDarkGaps"] == 0,
        "pedestrianContinuous": manifest["graphs"]["streamPedestrianComponents"] == 1,
        "serviceFireContinuous": manifest["graphs"]["streamBlockedFireRoutes"] == 0 and manifest["graphs"]["streamServiceDiscontinuities"] == 0,
        "waterContinuous": generation["geometry"]["roles"].get("archive-plaza-water", 0) > 0 and generation["geometry"]["roles"].get("archive-plaza-bed", 0) > 0 and manifest["graphs"]["streamMaintenanceReachable"],
        "noImageData": generation["imageDatablocks"] == 0,
        "directCopyZero": not manifest["urbanStream"]["directReferenceCopy"],
        "protectedBadges": "NOT CANONICAL" in manifest["badges"] and "NOT V3 APPLIED" in manifest["badges"],
    }
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "actualGlbCount": len(glbs),
        "actualGlbs": [str(path.relative_to(root)).replace("\\", "/") for path in glbs],
        "metrics": manifest["metrics"],
        "stream": manifest["urbanStream"],
        "originality": "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY",
    }
    atomic(root / "reports/final-production-contracts.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps({"status": result["status"], "actualGlbCount": result["actualGlbCount"], "failed": [key for key, value in result["checks"].items() if not value]}))
    raise SystemExit(result["status"] != "PASS")
