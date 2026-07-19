#!/usr/bin/env python3
import ast
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/blender/production_geometry/residential_v6_roof.py"
s=p.read_text(encoding="utf-8"); ast.parse(s)
for token in ("terraced-crown","glass-lantern","offset-screen","machine-room","hvac","maintenance-walkway","solar-panel","communications"):
    assert token in s
assert '"crownVariantCount"' in s and '"roofSkylineDistinct"' in s
print("Residential V6 roof/skyline source contract PASS")
