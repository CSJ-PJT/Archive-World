from pathlib import Path
import ast

source = (Path(__file__).parent / "urban_stream" /
          "assemble_precision_hero.py").read_text(encoding="utf-8")
ast.parse(source)
for contract in ("GENERATED_CORE_STREAM_PRECISION_ALL_ZONES", "ALL_CORE_STREAM_ZONES",
                 "groundPlaneStreamOpening", "archive-water-plaza-hero-",
                 "core-stream-ledger-transit-", "nextZoneLocked"):
    assert contract in source
assert "original - len(manifest[\"instances\"]) == 12" in source
assert '"buildingInstances": len(manifest["instances"]) + 6 + expanded_buildings' in source
print("precision hero assembly: PASS")
