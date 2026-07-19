#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
targets = json.loads((root / "config/production-geometry-v5-targets.json").read_text(encoding="utf-8"))
assert targets["residential"]["triangleRange"]["LOD0"][0] >= 60000
assert targets["office"]["triangleRange"]["LOD0"][0] >= 80000
source = (root / "scripts/urban/analyze_proof_baseline.py").read_text(encoding="utf-8")
for token in ("FAILED_BASELINE_PRESERVED", "facadeRepetitionRatio", "humanScaleFeatureCount"):
    assert token in source
print("production geometry baseline contract PASS")
