#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "config/residential-v6-quality-targets.json").read_text(encoding="utf-8"))
assert data["family"].endswith("-v6")
assert data["officeBaseline"] == {
    "family": "archive-cbd-twin-atrium-pq-v5", "score": 82, "grade": "B",
    "status": "PO_REVIEW_CANDIDATE", "frozen": True, "canonical": False, "cityApplied": False,
}
targets = data["targets"]
assert targets["minimumScore"] >= 82
assert targets["facadeRepetitionRatioMax"] <= 0.09
assert targets["triangleRange"] == {"LOD0": [120000, 180000], "LOD1": [40000, 85000], "LOD2": [15000, 35000]}
assert sum(data["plannedScoreGain"].values()) >= 6
assert len(data["before"]["issues"]) == 10
print("Residential V6 quality target contract PASS")
