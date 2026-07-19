#!/usr/bin/env python3
"""Build evidence-linked, provisional static scorecards for LOD2 smoke pilots."""
import argparse
import json
from pathlib import Path


def score(report, validator):
    metrics = report["metrics"]
    validation = next(
        (item for item in validator["results"] if Path(item["file"]).name == report["glb"]["file"]),
        None,
    )
    checks = {
        "officialValidatorErrorsZero": validation is not None and validation["errors"] == 0,
        "officialValidatorWarningsZero": validation is not None and validation["warnings"] == 0,
        "sideRearComplete": bool(metrics["sideRearComplete"]),
        "entrancePresent": metrics["entranceCount"] > 0,
        "serviceAccessPresent": bool(metrics["serviceAccess"]),
        "roofEquipmentPresent": metrics["roofEquipment"] > 0,
        "groundContact": bool(metrics["groundContact"]),
        "materialCountPositive": metrics["materialCount"] > 0,
        "threeSmokeViews": len(report["renders"]) == 3,
    }
    # Static evidence cannot award Visual Quality. Scores stay deliberately conservative.
    breakdown = {
        "massingSilhouette": 7,
        "facadeGeometry": 6 if metrics["uniqueFacadePatterns"] < 3 else 9,
        "entrancePodiumGround": 7,
        "sideRearCompleteness": 7 if checks["sideRearComplete"] else 0,
        "roofMechanical": 6 if checks["roofEquipmentPresent"] else 0,
        "materialPBR": 5,
        "functionalCredibility": 5,
        "archiveIdentity": 2,
    }
    total = sum(breakdown.values())
    return {
        "family": report["family"],
        "assessment": "PROVISIONAL_STATIC_ONLY",
        "visualApproval": "FAIL_NOT_REVIEW_READY",
        "score": total,
        "grade": "D" if total < 65 else "C",
        "breakdown": breakdown,
        "checks": checks,
        "metrics": metrics,
        "limitations": [
            "LOD2 smoke geometry is a technical composition proof, not production geometry.",
            "Rendered views show blockout-level facade and public-realm detail.",
            "A/B grade is prohibited until production renders are visually reviewed.",
            "LOD0/LOD1 ratios are not available from this smoke run.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--residential", required=True)
    parser.add_argument("--office", required=True)
    parser.add_argument("--validator", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    reports = [json.loads(Path(p).read_text(encoding="utf-8")) for p in (args.residential, args.office)]
    validator = json.loads(Path(args.validator).read_text(encoding="utf-8"))
    result = {
        "schemaVersion": 1,
        "status": "PROVISIONAL",
        "officialValidator": validator["validator"],
        "pilots": [score(report, validator) for report in reports],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"status": result["status"], "scores": [p["score"] for p in result["pilots"]]}))


if __name__ == "__main__":
    main()
