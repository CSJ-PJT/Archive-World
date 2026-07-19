#!/usr/bin/env python3
from pathlib import Path

source=Path(__file__).with_name("urban").joinpath("production_geometry_quality_report.py").read_text(encoding="utf-8")
for token in ("CODEX_VISUAL_REVIEW_COMPLETE_PO_APPROVAL_PENDING","actualCityApplicationEligible","blackClipping","facadeRepetitionRatio","canonicalLayoutRuntimeMainChanges"):
    assert token in source
assert '"residential":{' in source and '"office":{' in source
assert "PARTIAL" in source and "productionClaim" in source
print("production geometry quality report contract PASS")
