from pathlib import Path
import ast

source = Path("scripts/blender/urban_stream_final/activity_v11.py").read_text(encoding="utf-8")
ast.parse(source)
for cluster in ("office-arrival", "transit-waiting", "bridge-crossing", "cafe-terrace", "maintenance-worker", "night-pedestrian"):
    assert cluster in source
for role in ("human-body", "human-head", "human-leg", "vehicle-{kind}-body", "bicycle-wheel"):
    assert role in source
assert '"floatingHumans": 0' in source and '"plazaVehicleIntrusions": 0' in source
print("final district activity: PASS")
