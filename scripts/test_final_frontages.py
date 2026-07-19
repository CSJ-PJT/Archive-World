from pathlib import Path
import ast

source = Path("scripts/blender/urban_stream_final/frontage_builder.py").read_text(encoding="utf-8")
ast.parse(source)
for contract in ('"lobby": 8', '"retail-public": 12', '"service": 4', "interior-counter", "rear-wall", "ceiling", "mullion", "tactile"):
    assert contract in source
assert "archiveWaterPlaza\": 0.82" in source
assert '"boxAttachmentOnly": False' in source
print("final frontage architecture: PASS")
