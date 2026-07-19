from pathlib import Path
import ast

source = Path("scripts/blender/urban_stream_final/lighting_v11.py").read_text(encoding="utf-8")
ast.parse(source)
for family in ("lobby-downlight", "bridge-handrail", "edge-light", "transit-canopy", "service-security", "limited-crown"):
    assert family in source
assert '"darkGaps": 0' in source and '"allWindowsEmissive": False' in source
assert '"nightResourceLazy": True' in source and '"levels": 4' in source
print("final night lighting: PASS")
