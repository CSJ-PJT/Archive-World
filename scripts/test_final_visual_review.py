from pathlib import Path
import ast

source = Path("scripts/urban_stream/finalize_final_review.py").read_text(encoding="utf-8")
ast.parse(source)
for contract in ("visualScore", "urbanStreamScore", "poApprovalEligible", "Hardware Chrome result is UNKNOWN", "referenceDirectCopyZero", "final-visual-quality-gate.json"):
    assert contract in source
assert "Concept reference is used only for abstract spatial and visual-quality guidance" in source
assert '"poApprovalEligible": False' in source
assert "all(required.values())" in source
print("final visual review contract: PASS")
