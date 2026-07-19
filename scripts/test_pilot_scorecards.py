#!/usr/bin/env python3
from pathlib import Path

source = Path(__file__).with_name("urban").joinpath("build_pilot_scorecards.py").read_text(encoding="utf-8")
for token in ("PROVISIONAL_STATIC_ONLY", "FAIL_NOT_REVIEW_READY", "officialValidatorErrorsZero", "limitations"):
    assert token in source, token
assert '"A"' not in source and '"B"' not in source, "static analyzer must not award visual approval"
print("pilot scorecard contract PASS")
