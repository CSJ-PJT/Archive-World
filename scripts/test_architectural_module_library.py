#!/usr/bin/env python3
"""Static safety/contract checks for the image-free module-library smoke script."""
import json
import sys
from pathlib import Path

source = Path("scripts/blender/architectural_module_library.py").read_text(encoding="utf-8")
for forbidden in ("bpy.data.images.load", "bpy.data.images.save", "Image Texture", "C:/Users/"):
    assert forbidden not in source, f"forbidden dependency: {forbidden}"
for required in ("recessed-bay", "lobby", "machine-room", "sidewalk", "'meters'", "'lod'"):
    assert required in source, f"missing module contract: {required}"
if len(sys.argv) > 1:
    report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    modules = report["modules"]
    assert len(modules) >= 20, "expected at least 20 isolated modules"
    assert all(item["meters"] and len(item["lod"]) == 3 for item in modules)
    assert report["imageTextureNodes"] == 0 and report["externalImageReferences"] == 0
print("architectural module library contract PASS")
