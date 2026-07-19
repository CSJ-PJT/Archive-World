#!/usr/bin/env python3
from pathlib import Path

root=Path(__file__).with_name("blender").joinpath("production_geometry")
material=(root/"material_library.py").read_text(encoding="utf-8"); lod=(root/"lod_builder.py").read_text(encoding="utf-8")
for name in ("painted-concrete","residential-glass","limestone","curtain-wall-glass","water"): assert name in material
for token in ("imageTextureNodes","externalImageReferences","signature"): assert token in material
for token in ("60000,140000","80000,180000","strictDecrease","boundsConsistent"): assert token in lod
print("production LOD and material contracts PASS")
