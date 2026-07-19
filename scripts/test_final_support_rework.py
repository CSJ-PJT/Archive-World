from pathlib import Path
import ast

source = Path("scripts/blender/urban_stream_final/support_rework_v11.py").read_text(encoding="utf-8")
ast.parse(source)
assert "archive-cbd-twin-atrium-pq-v5" not in source
for detail in ("podium-stream-wing", "stream-facade-recess", "stream-lobby-interior", "stream-entry-canopy", "stream-arcade-column", "rear-service-core", "roof-crown"):
    assert detail in source
assert '"families": len(SPECS)' in source and '"officeV5Changed": False' in source
print("final support body rework: PASS")
