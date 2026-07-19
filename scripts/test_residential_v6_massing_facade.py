#!/usr/bin/env python3
import ast
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
massing=ROOT/"scripts/blender/production_geometry/residential_v6_massing.py"
facade=ROOT/"scripts/blender/production_geometry/residential_v6_facade.py"
for path in (massing,facade): ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
ms=massing.read_text(encoding="utf-8"); fs=facade.read_text(encoding="utf-8")
assert '"form":"slab"' in ms and '"form":"point"' in ms and '"form":"courtyard-edge"' in ms
assert "towerMeshCloneCount\":0" in ms
assert "PATTERNS=(" in fs and fs.count('"recessed"') >= 1
assert "verticalZones" in fs and "sidePatterns" in fs and "rearPatterns" in fs
assert "Image Texture" not in ms+fs and "bpy.data.images" not in ms+fs
print("Residential V6 massing/facade source contract PASS")
