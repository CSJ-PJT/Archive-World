#!/usr/bin/env python3
from pathlib import Path

root=Path(__file__).with_name("blender").joinpath("production_geometry")
source=(root/"generate_production_pilot.py").read_text(encoding="utf-8")
for token in ("residential-courtyard-piloti-pq-v5","archive-cbd-twin-atrium-pq-v5","RESIDENTIAL_MASSES","OFFICE_TOWERS","officialValidator"):
    assert token in source
for forbidden in ("bpy.data.images.load","bpy.data.images.save","architecture_factory_v3"):
    assert forbidden not in source
assert (root/"residential_pq_v5.py").exists() and (root/"office_pq_v5.py").exists()
print("production pilot source contract PASS")
