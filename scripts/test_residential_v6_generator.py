#!/usr/bin/env python3
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; source=(ROOT/"scripts/blender/production_geometry/residential_pq_v6.py").read_text(encoding="utf-8")
ast.parse(source)
for module in ("residential_v6_massing","residential_v6_facade","residential_v6_lowrise","residential_v6_ground","residential_v6_roof","residential_v6_render"):
    assert module in source
assert 'FAMILY="residential-courtyard-piloti-pq-v6"' in source
assert '"LOD0":(120000,180000)' in source and '"LOD2":(15000,35000)' in source
assert "office(" not in source and "officeBaselineFrozen\":True" in source
views=(ROOT/"scripts/blender/production_geometry/residential_v6_render.py").read_text(encoding="utf-8")
ast.parse(views); assert views.count('("') >= 20 and '"streetLevel"' in views
print("Residential V6 generator/render source contract PASS")
