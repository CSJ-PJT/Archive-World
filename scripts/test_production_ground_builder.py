#!/usr/bin/env python3
from pathlib import Path

source=Path(__file__).with_name("blender").joinpath("production_geometry/ground_builder.py").read_text(encoding="utf-8")
for token in ("residential_ground","office_ground","fire-access","service-lane","tactile","water-basin","security-bollard"):
    assert token in source
assert source.count("add_box") >= 20 and source.count("add_cylinder") >= 3
print("production ground interface contract PASS")
