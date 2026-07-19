#!/usr/bin/env python3
import ast
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/blender/production_geometry/residential_v6_ground.py"
s=p.read_text(encoding="utf-8"); ast.parse(s)
for token in ("courtyard-paving","dropoff-paving","pocket-lawn","pedestrian-spine","fire-route","service-lane","drainage-edge","tactile"):
    assert token in s
for contract in ('"humanProxies":20','"sedanProxies":4','"bicycleProxies":6','"benchCount":8','"planterCount":12','"bollardCount":16'):
    assert contract in s
assert "brand" in s.lower() and "bpy.data.images" not in s
print("Residential V6 ground/public-realm source contract PASS")
