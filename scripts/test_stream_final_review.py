from pathlib import Path
import ast

source = Path("scripts/urban_stream/finalize_stream_review.py").read_text(encoding="utf-8")
ast.parse(source)
for evidence in ("screenshots72", "officialValidator", "averageFps30", "onePercentLow20", "directReferenceCopy"):
    assert evidence in source
assert '"verdict": "PARTIAL"' in source
assert '"hardwarePerformance": "UNKNOWN_NOT_MEASURED"' in source
print("stream final review contract: PASS")
