#!/usr/bin/env python3
from pathlib import Path

source = Path(__file__).with_name("blender").joinpath("production_geometry/geometry_core.py").read_text(encoding="utf-8")
for token in ("class MeshBatch", "add_box", "add_wedge", "add_cylinder", "validate_geometry", "componentCount"):
    assert token in source
assert "subdivision" not in source.lower()
assert "bpy.data.images" not in source
print("production geometry core contract PASS")
