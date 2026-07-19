from pathlib import Path
import ast

source = Path("scripts/blender/urban_stream_final/section_builder.py").read_text(encoding="utf-8")
ast.parse(source)
for required in ("archive-plaza", "ledger-terrace", "transit-junction", "green-park", "mixed-active-frontage", "service-maintenance", "future-riverfront-gateway"):
    assert required in source
for geometry in ("lower-promenade", "upper-walk", "retaining", "access-step", "accessible-ramp", "drainage"):
    assert geometry in source
assert '"flatSingleDepth": False' in source
print("final stream sections: PASS")
