#!/usr/bin/env python3
import ast
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/blender/production_geometry/residential_v6_lowrise.py"
source=p.read_text(encoding="utf-8"); ast.parse(source)
for role in ("main-lobby","secondary-lobby","community-entry","service-entry","parking-ramp","recycling","bicycle"):
    assert role in source
assert '"entranceCount":5' in source and '"lowRiseFunctions":14' in source
assert '(22,-2,.65)' in source
assert "bpy.data.images" not in source
print("Residential V6 low-rise/entrance source contract PASS")
