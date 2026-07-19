#!/usr/bin/env python3
"""Issue an evidence-linked, non-inflated V11 final review verdict."""
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
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def finalize(root: Path) -> dict:
    capture = read(root / "renders/capture-report.json")
    contracts = read(root / "reports/final-production-contracts.json")
    performance = read(root / "performance/final-performance-summary.json")
    official = read(root / "validation/actual-glb-validation.json")
    categories = {
        "Buildings": {"score": 10, "max": 13, "evidence": ["01-district-aerial-day.png", "11-support-family-context-day.png"], "finding": "11 support bodies are rebuilt, but tower grids remain visibly repetitive."},
        "Block Composition": {"score": 9, "max": 12, "evidence": ["01-district-aerial-day.png", "09-skyline-day.png"], "finding": "Primary/secondary peaks read; repeated high-rise cadence remains."},
        "Street/Public Realm": {"score": 9, "max": 13, "evidence": ["14-archive-water-plaza-street-day.png", "28-cafe-terrace-day.png"], "finding": "Actual furnishings and frontages exist; broad hardscape and primitive detail remain."},
        "Urban Stream Integration": {"score": 9, "max": 12, "evidence": ["13-stream-spine-aerial-day.png", "25-water-closeup-day.png", "33-stream-section-depth-day.png"], "finding": "785.88m actual bed/water/edges and seven sections are connected, but water legibility is inconsistent at eye level."},
        "Landscape": {"score": 5, "max": 8, "evidence": ["19-green-stream-edge-day.png", "27-pocket-wetland-day.png"], "finding": "Emissive foliage defect fixed and 60 families are represented; crown geometry remains coarse near camera."},
        "Transit": {"score": 5, "max": 6, "evidence": ["16-transit-stream-junction-day.png", "31-transit-waiting-plaza-night.png"], "finding": "Station, waiting plaza, bridge and bus/taxi relation are present."},
        "Service/Rear": {"score": 4, "max": 5, "evidence": ["06-service-rear-day.png", "23-service-stream-crossing-day.png"], "finding": "Service/fire/maintenance continuity passes with a distinct rear grammar."},
        "Skyline": {"score": 6, "max": 8, "evidence": ["09-skyline-day.png", "01-district-aerial-dusk.png"], "finding": "Anchor and secondary peaks exist; family/orientation repetition is still apparent."},
        "Street-Level Credibility": {"score": 6, "max": 10, "evidence": ["15-ledger-stream-terrace-day.png", "30-archive-active-frontage-day.png"], "finding": "Entrances and interiors are readable, but human activity and some foreground composition remain weak."},
        "Archive Identity": {"score": 4, "max": 5, "evidence": ["20-archive-gateway-bridge-dusk.png", "14-archive-water-plaza-street-dusk.png"], "finding": "Civic portal, restrained cyan hierarchy and material split are Archive-native."},
        "Lighting": {"score": 3, "max": 4, "evidence": ["35-night-lighting-axis-night.png", "16-transit-stream-junction-night.png"], "finding": "A bounded hierarchy exists; night depth remains less resolved than the concept direction."},
        "Performance/LOD": {"score": 2, "max": 4, "evidence": ["36-technical-status-day.png", "../performance/final-performance-summary.json"], "finding": "339 draw calls passes the budget; FPS and 1% low gates fail in measured headless Chrome."},
    }
    score = sum(item["score"] for item in categories.values())
    required = {
        "visual80": score >= 80,
        "stream10": categories["Urban Stream Integration"]["score"] >= 10,
        "streetCredibility8": categories["Street-Level Credibility"]["score"] >= 8,
        "dayAverage30": performance["gates"]["dayAverage30"],
        "nightAverage30": performance["gates"]["nightAverage30"],
        "dayNightLow20": performance["gates"]["dayLow20"] and performance["gates"]["nightLow20"],
        "critical24": performance["gates"]["critical24"],
        "drawCallsUnder400": max(performance["lod2Optimized"]["day"]["drawCalls"], performance["lod2Optimized"]["night"]["drawCalls"]) < 400,
        "officialValidatorZero": official["summary"] == {"files": 38, "errors": 0, "warnings": 0, "infos": 0},
        "productionContracts": contracts["status"] == "PASS",
        "cameraPackage90": capture["screenshotCount"] >= 90,
        "officeV5Unchanged": contracts["checks"]["officeV5Frozen"],
        "referenceDirectCopyZero": contracts["checks"]["directCopyZero"],
    }
    report = {
        "verdict": "PASS" if all(required.values()) else "PARTIAL",
        "visualScore": score,
        "visualGrade": "B" if score >= 80 else "C" if score >= 65 else "D",
        "urbanStreamScore": categories["Urban Stream Integration"]["score"],
        "categories": categories,
        "gates": required,
        "baseline": {"version": "V10", "visualScore": 73, "grade": "C", "dayAverageFps": 26.3, "nightAverageFps": 27.5},
        "actual": {"families": 12, "blocks": 22, "instances": 220, "proxyRatio": 0, "streamLengthM": 785.88, "screenshots": capture["screenshotCount"]},
        "conceptReference": "Concept reference is used only for abstract spatial and visual-quality guidance. No direct reproduction of identifiable architecture, waterway design, bridge design, lighting arrangement, or urban plan is permitted.",
        "poApprovalEligible": False,
        "districtExpansionEligible": False,
        "v3ApplicationEligible": False,
        "knownLimitations": [
            "Visual score remains below B because near-camera vegetation, human activity, ground-floor depth and water legibility remain visibly procedural.",
            "Measured headless Chrome does not meet average/1% low/critical FPS gates; authentic Hardware Chrome result is UNKNOWN.",
            "The concept target is a direction reference, not a claim of achieved photorealism.",
        ],
    }
    atomic(root / "reports/final-visual-quality-gate.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    result = finalize(args.root)
    print(json.dumps({"verdict": result["verdict"], "visualScore": result["visualScore"], "grade": result["visualGrade"], "streamScore": result["urbanStreamScore"], "failed": [key for key, value in result["gates"].items() if not value]}))
