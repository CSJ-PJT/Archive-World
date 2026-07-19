from pathlib import Path
import ast

source = Path("scripts/urban_stream/assemble_precision_hero.py").read_text(encoding="utf-8")
ast.parse(source)
for contract in ("GENERATED_CORE_STREAM_PRECISION_HERO_A", "HERO_ZONE_SEQUENTIAL", "groundPlaneStreamOpening", "archive-water-plaza-hero-v26.glb", "nextZoneLocked"):
    assert contract in source
assert "original - len(manifest[\"instances\"]) == 12" in source
assert '"buildingInstances": len(manifest["instances"]) + 6' in source
print("precision hero assembly: PASS")
