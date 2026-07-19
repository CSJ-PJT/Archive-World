#!/usr/bin/env python3
from pathlib import Path

root=Path(__file__).with_name("blender").joinpath("production_geometry")
metrics=(root/"geometry_metrics.py").read_text(encoding="utf-8"); render=(root/"render_review.py").read_text(encoding="utf-8")
for token in ("facadeRepetitionRatio","sideFacadeComplete","rearFacadeComplete","groundInterfaceCount"): assert token in metrics
for token in ("day-hero-front","rear-service","wireframe-lod0","material-breakdown","scale-check"): assert token in render
assert render.count("(\"") >= 16 and "resolution_x=size" in render
print("production metrics and review renderer contracts PASS")
