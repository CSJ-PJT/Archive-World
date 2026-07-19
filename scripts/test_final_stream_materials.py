from pathlib import Path
import ast

source = Path("scripts/blender/urban_stream_final/materials_v11.py").read_text(encoding="utf-8")
ast.parse(source)
for required in ("wet-stone", "dry-stone", "shallow-water-v11", "warm-interior", "archive-cyan-light"):
    assert required in source
assert "ShaderNodeTexNoise" in source and "ShaderNodeBump" in source
assert "TEX_IMAGE" in source and "bpy.data.images" in source
assert "images.load" not in source and "images.save" not in source
assert 'name in ("archive-cyan-light", "warm-light", "warm-interior")' in source
assert 'if "light" in name' not in source
print("final stream materials: PASS")
