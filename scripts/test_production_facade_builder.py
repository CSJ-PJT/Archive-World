#!/usr/bin/env python3
from pathlib import Path

source=Path(__file__).with_name("blender").joinpath("production_geometry/facade_builder.py").read_text(encoding="utf-8")
for token in ("residential_facades", "office_facades", "res-front", "res-rear", "office-rear-service-wall", "depthRangeMeters"):
    assert token in source
for lod in ("LOD0","LOD1","LOD2"): assert lod in source
assert source.count("add_box") >= 20
assert "subdivision" not in source.lower()
print("production facade builder contract PASS")
