#!/usr/bin/env python3
"""Quantify the preserved V4 LOD2 proof against V5 production targets."""
import argparse
import json
from pathlib import Path

FIELDS = (
    "triangleCount", "objectCount", "silhouetteComplexity", "facadePatternCount",
    "facadeRepetitionRatio", "visibleDepthVariationMeters", "balconyDepthMeters",
    "mullionDensity", "entranceComplexity", "podiumArticulation",
    "sideFacadeCompleteness", "rearFacadeCompleteness", "roofEquipmentDensity",
    "groundInterfaceCompleteness", "materialSeparation", "streetLevelDetailCount",
    "humanScaleFeatureCount",
)


def current_values(report):
    m = report["metrics"]
    return {
        "triangleCount": m["trianglesProxy"], "objectCount": m["objectCount"],
        "silhouetteComplexity": 3, "facadePatternCount": m["uniqueFacadePatterns"],
        "facadeRepetitionRatio": m["repetitionRatio"], "visibleDepthVariationMeters": 0.45,
        "balconyDepthMeters": 0.7 if report["mode"] == "residential" else 0,
        "mullionDensity": 18 if report["mode"] == "office" else 0,
        "entranceComplexity": m["entranceCount"], "podiumArticulation": 1,
        "sideFacadeCompleteness": 0.35, "rearFacadeCompleteness": 0.3,
        "roofEquipmentDensity": m["roofEquipment"], "groundInterfaceCompleteness": 4,
        "materialSeparation": m["materialCount"], "streetLevelDetailCount": 4,
        "humanScaleFeatureCount": 0,
    }


def target_values(target):
    return {
        "triangleCount": target["triangleRange"]["LOD0"][0], "objectCount": 40,
        "silhouetteComplexity": target["silhouetteComplexity"],
        "facadePatternCount": target["facadePatterns"],
        "facadeRepetitionRatio": target["maxFacadeRepetitionRatio"],
        "visibleDepthVariationMeters": target["visibleDepthRangeMeters"][1],
        "balconyDepthMeters": target["balconyDepthMeters"], "mullionDensity": target["mullionCount"],
        "entranceComplexity": target["entranceComplexity"], "podiumArticulation": target["podiumArticulation"],
        "sideFacadeCompleteness": 1.0, "rearFacadeCompleteness": 1.0,
        "roofEquipmentDensity": target["roofEquipmentCount"],
        "groundInterfaceCompleteness": target["groundInterfaceCount"],
        "materialSeparation": target["materialCount"],
        "streetLevelDetailCount": target["streetLevelDetailCount"],
        "humanScaleFeatureCount": target["humanScaleFeatureCount"],
    }


def analyze(report, target):
    current, wanted = current_values(report), target_values(target)
    rows = []
    for field in FIELDS:
        delta = round(wanted[field] - current[field], 4)
        direction = "maximum" if field == "facadeRepetitionRatio" else "minimum"
        rows.append({"metric": field, "current": current[field], "target": wanted[field], "gap": delta, "targetType": direction})
    return {
        "family": report["family"], "preservationStatus": "FAILED_BASELINE_PRESERVED",
        "metrics": rows,
        "implementationPlan": [
            "Replace object-per-box proof with batched, meaningful facade/entrance/roof/ground geometry.",
            "Compile independent LOD0/LOD1/LOD2 geometry from the same deterministic plan.",
            "Render front, rear, side, roof and ground evidence before visual scoring.",
        ],
    }


def main():
    p = argparse.ArgumentParser(); p.add_argument("--residential", required=True); p.add_argument("--office", required=True)
    p.add_argument("--targets", required=True); p.add_argument("--output", required=True); a = p.parse_args()
    targets = json.loads(Path(a.targets).read_text(encoding="utf-8"))
    result = {"schemaVersion": 1, "status": "BASELINE_ANALYZED", "pilots": []}
    for mode, path in (("residential", a.residential), ("office", a.office)):
        result["pilots"].append(analyze(json.loads(Path(path).read_text(encoding="utf-8")), targets[mode]))
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "pilots": len(result["pilots"])}))


if __name__ == "__main__": main()
