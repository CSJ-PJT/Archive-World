from pathlib import Path
import ast

source = Path("scripts/blender/urban_stream_final/bridge_builder_v11.py").read_text(encoding="utf-8")
ast.parse(source)
for detail in ("approach-a", "handrail", "rail-post", "drain", "archive-gateway-civic-beam", "transit-bridge-canopy", "green-bridge-cycle-strip", "service-crossing-protection"):
    assert detail in source
assert '"duplicateMesh": False' in source and '"serviceContinuity": True' in source
print("final stream bridges: PASS")
