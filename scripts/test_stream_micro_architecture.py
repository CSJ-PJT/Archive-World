from pathlib import Path
import ast

path = Path("scripts/blender/urban_stream/micro_architecture.py")
source = path.read_text(encoding="utf-8")
ast.parse(source)
for required in ("door", "glazing", "canopy", "tactile", "blank-signage"):
    assert required in source
assert "unitCount" in source and "streamFacing" in source
assert "Image Texture" not in source and "bpy.data.images" not in source
print("stream micro architecture: PASS")
