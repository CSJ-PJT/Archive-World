from pathlib import Path
import ast

source = Path("scripts/blender/urban_stream_final/generate_final_stream.py").read_text(encoding="utf-8")
ast.parse(source)
for module in ("build_sections", "build_frontages", "build_nodes", "build_bridges", "build_vegetation", "build_activity", "build_lighting"):
    assert module in source
assert "archive-urban-stream-final.glb" in source
assert '"directReferenceCopy": False' in source and '"officeV5Changed": False' in source
assert "bpy.data.images.load" not in source and "bpy.data.images.save" not in source
print("final stream generator: PASS")
