#!/usr/bin/env python3
import ast
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/blender/production_geometry/residential_v6_materials.py"
s=p.read_text(encoding="utf-8"); tree=ast.parse(s)
specs=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(getattr(t,"id","")=="SPECS" for t in n.targets))
assert isinstance(specs,ast.Tuple) and len(specs.elts)==17
assert "TEX_IMAGE" in s and '"externalImageReferences":0' in s and '"proceduralOnly":True' in s
assert "bpy.data.images" not in s and "Image Texture" not in s
print("Residential V6 procedural palette contract PASS")
