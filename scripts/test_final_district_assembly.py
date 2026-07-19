from pathlib import Path
import ast

source = Path("scripts/urban_stream/assemble_final_district.py").read_text(encoding="utf-8")
ast.parse(source)
for contract in ("archive-urban-stream-final.glb", "stream-facing", "opposite-stream", "supportBodiesRebuilt", "streaming-final.json", "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY"):
    assert contract in source
assert 'family["id"] != "archive-cbd-twin-atrium-pq-v5"' in source
assert '"officeV5Changed": False' in source
print("final district assembly: PASS")
