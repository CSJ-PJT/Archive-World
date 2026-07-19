#!/usr/bin/env python3
import ast
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/urban/residential_v6_quality_report.py"
s=p.read_text(encoding="utf-8"); tree=ast.parse(s)
assert "BREAKDOWN" in s and "EVIDENCE" in s and "facadeRepetition" in s
assert '"files":3,"errors":0,"warnings":0,"infos":0' in s
assert '"actualCityApplicationEligible":False' in s
assert '"officeBaseline":targets["officeBaseline"]' in s
assert "sum(BREAKDOWN.values())" in s and "PO_REVIEW_CANDIDATE" in s
print("Residential V6 quality-report contract PASS")
