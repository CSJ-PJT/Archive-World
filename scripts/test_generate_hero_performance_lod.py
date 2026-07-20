from pathlib import Path
import ast

source = (Path(__file__).parent / "blender" / "hero_zones" /
          "generate_hero_performance_lod.py")
text = source.read_text(encoding="utf-8")
ast.parse(text)
for token in ("DECIMATE", "use_collapse_triangulate", "sourceUnchanged",
              "trianglesBefore", "trianglesAfter", "materialSlots",
              '"officeV5Changed": False'):
    assert token in text, token
for forbidden in ("bpy.data.images.load", "bpy.data.images.save", "Image Texture",
                  "architecture_factory_v3"):
    assert forbidden not in text, forbidden
print("hero performance LOD contract: PASS")
