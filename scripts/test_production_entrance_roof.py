#!/usr/bin/env python3
from pathlib import Path

root=Path(__file__).with_name("blender").joinpath("production_geometry")
entrance=(root/"entrance_builder.py").read_text(encoding="utf-8"); roof=(root/"roof_builder.py").read_text(encoding="utf-8")
for token in ("residential_entrance","office_entrance","parking-ramp","service-door","security-bollard"):
    assert token in entrance
for token in ("residential_roofs","office_roofs","parapet","machine-room","maintenance-walkway"):
    assert token in roof
assert "brand" not in entrance.lower() and "logo" not in entrance.lower()
print("production entrance and roof contracts PASS")
