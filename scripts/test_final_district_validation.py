from pathlib import Path
import ast

source = Path("scripts/urban_stream/validate_final_district.py").read_text(encoding="utf-8")
ast.parse(source)
for contract in (
    "actualGlbCount38", "officeV5Frozen", "supportInstancesAffected",
    "sectionDepth", "frontageTargets", "pedestrianContinuous",
    "serviceFireContinuous", "directCopyZero", "final-production-contracts.json",
):
    assert contract in source
assert "read_text(encoding=\"utf-8-sig\")" in source
assert "os.replace(temporary, path)" in source
print("final district production validator: PASS")
