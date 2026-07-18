#!/usr/bin/env python3
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("compiler", Path("scripts/urban/building_genome_compiler.py"))
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
valid = {"id":"test","category":"office","seed":1,"footprint":{"meters":[20,20]},"massing":{"floors":8},"facade":{"bays":["a","b"]},"entrance":{},"podium":{},"roof":{},"ground":{},"materials":[],"lod":{"lod0":10,"lod1":5,"lod2":1},"serviceRear":True,"mechanicalFloor":True}
assert module.compile_genome(valid)["validation"]["groundZ"] == 0
invalid = dict(valid); invalid["serviceRear"] = False
try:
    module.compile_genome(invalid)
except ValueError as error:
    assert "serviceRear" in str(error)
else:
    raise AssertionError("missing office service rear must fail")
print("building genome compiler contract PASS")
