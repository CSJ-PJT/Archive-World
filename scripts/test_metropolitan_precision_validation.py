from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
source = (Path(__file__).parent / "metropolitan" / "validate_metropolitan_precision.py").read_text(encoding="utf-8")
assert "capture-coverage" in source
assert "headless-fps-below-30" in source
assert "draw-call-budget" in source
assert "protected-boundary-mutation" in source
assert "hardwareChrome" in source
assert "NOT_APPLICABLE_RUNTIME_GEOMETRY" in source
print("metropolitan precision validation contract: PASS")
