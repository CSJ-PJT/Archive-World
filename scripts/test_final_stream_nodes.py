from pathlib import Path
import ast

source = Path("scripts/blender/urban_stream_final/node_builder_v11.py").read_text(encoding="utf-8")
ast.parse(source)
for node in ("archive-event-plaza", "ledger-formal-terrace", "transit-transfer-plaza", "quiet-garden", "cafe-terrace", "performance-step", "wetland-observation"):
    assert node in source
assert '"majorNodes": 3' in source and '"pocketNodes": 4' in source
print("final stream nodes: PASS")
