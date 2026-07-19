#!/usr/bin/env python3
"""Create an evidence-linked, deliberately non-inflated V10 review report."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCORES = {
    "buildings": {"score": 11, "max": 13, "evidence": ["renders/01-aerial-core-day.png"]},
    "blockComposition": {"score": 9, "max": 12, "evidence": ["renders/13-stream-aerial-day.png"]},
    "streetPublicRealm": {"score": 10, "max": 13, "evidence": ["renders/14-archive-water-plaza-day.png"]},
    "urbanStreamIntegration": {"score": 9, "max": 12, "evidence": ["renders/15-ledger-stream-terrace-day.png", "renders/16-transit-stream-junction-day.png"]},
    "landscape": {"score": 5, "max": 8, "evidence": ["renders/19-green-stream-edge-day.png"]},
    "transit": {"score": 4, "max": 6, "evidence": ["renders/16-transit-stream-junction-day.png"]},
    "serviceRear": {"score": 3, "max": 5, "evidence": ["renders/23-service-stream-crossing-day.png"]},
    "skyline": {"score": 7, "max": 8, "evidence": ["renders/13-stream-aerial-day.png"]},
    "streetLevelCredibility": {"score": 7, "max": 10, "evidence": ["renders/20-archive-gateway-bridge-day.png"]},
    "archiveIdentity": {"score": 4, "max": 5, "evidence": ["renders/14-archive-water-plaza-night.png"]},
    "lighting": {"score": 2, "max": 4, "evidence": ["renders/14-archive-water-plaza-night.png"]},
    "performanceLod": {"score": 2, "max": 4, "evidence": ["performance/viewer-performance.json"]},
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main(root: Path) -> dict:
    manifest = load(root / "manifest/core-district-stream-3d.json")
    generation = load(root / "stream/stream-generation-report.json")
    validation = load(root / "validation/actual-glb-validation.json")
    capture = load(root / "renders/capture-report.json")
    performance = load(root / "performance/viewer-performance.json")
    lod2 = load(root / "performance-lod2/viewer-performance.json")
    score = sum(item["score"] for item in SCORES.values())
    report = {
        "verdict": "PARTIAL",
        "visualScore": score,
        "grade": "C" if score < 80 else "B",
        "scores": SCORES,
        "gate": {
            "visual80": score >= 80,
            "streamIntegration10": SCORES["urbanStreamIntegration"]["score"] >= 10,
            "officialValidator": validation["summary"] == {"files": 38, "errors": 0, "warnings": 0, "infos": 0},
            "screenshots72": capture["screenshotCount"] >= 72,
            "drawCalls400": all(result["drawCalls"] <= 400 for result in performance["results"]),
            "averageFps30": all(result["averageFps"] >= 30 for result in performance["results"]),
            "onePercentLow20": all(result["onePercentLow"] >= 20 for result in performance["results"]),
        },
        "stream": manifest["urbanStream"],
        "districtMetrics": manifest["metrics"],
        "geometry": generation["geometry"],
        "microArchitecture": generation["microArchitecture"],
        "headlessPerformanceLod1": performance["results"],
        "headlessPerformanceLod2": lod2["results"],
        "hardwarePerformance": "UNKNOWN_NOT_MEASURED",
        "knownLimitations": [
            "Street-level views retain large blank paving and foreground obstruction in several cameras.",
            "Vegetation is procedural low-detail and repeats visibly at close range.",
            "Night hierarchy is present but lobby and stream-edge illumination remain too sparse.",
            "Stream-facing block change is additive micro-architecture; primary support-building geometry was not rebuilt.",
            "Headless average FPS and 1% low remain below the production gate.",
        ],
        "officeV5Changed": False,
        "canonicalChanged": False,
        "v3Applied": False,
        "runtimeChanged": False,
        "directReferenceCopy": False,
    }
    report_path = root / "reports/final-review.json"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    checksum = hashlib.sha256((root / "stream/archive-urban-stream.glb").read_bytes()).hexdigest()
    (root / "reports/stream-glb.sha256").write_text(checksum + "  archive-urban-stream.glb\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    result = main(args.root)
    print(json.dumps({"verdict": result["verdict"], "score": result["visualScore"], "gate": result["gate"]}))
