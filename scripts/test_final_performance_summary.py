from pathlib import Path
import ast

source = Path("scripts/urban_stream/summarize_final_performance.py").read_text(encoding="utf-8")
ast.parse(source)
for contract in ("HEADLESS_CHROME_ACTUAL_WEBGL", "UNKNOWN_AUTHENTIC_SAMPLE_UNAVAILABLE", "triangleReduction", "drawCallsBelow350", "dayAverage30", "nightLow20", "final-performance-summary.json"):
    assert contract in source
assert "Hardware Chrome are not interchangeable" in source
assert "os.replace(temporary, path)" in source
print("final performance summary contract: PASS")
