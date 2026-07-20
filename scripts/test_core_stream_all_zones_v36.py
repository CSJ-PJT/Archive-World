from pathlib import Path
import ast


source = (Path(__file__).parent / "blender" / "hero_zones" /
          "core_stream_all_zones_v36.py")
text = source.read_text(encoding="utf-8")
ast.parse(text)

required = (
    "LEDGER_SPECS",
    "TRANSIT_SPECS",
    "_build_continuous_corridor",
    "_build_ledger_terrace",
    "_build_transit_junction",
    "_build_vegetation_activity_lighting",
    "add_wall_first_building",
    "core-stream-ledger-transit-v36.glb",
    'assert len(buildings) == 13',
    'assert len(hero.ENVELOPE) >= 13',
    'assert detached_windows == 0',
    '"officeV5Changed": False',
    '"qualityTarget": {"grade": "S", "minimumScore": 95}',
)
missing = [token for token in required if token not in text]
assert not missing, missing
for forbidden in (
    "bpy.data.images.load",
    "bpy.data.images.save",
    "Image Texture",
    "architecture_factory_v3",
):
    assert forbidden not in text, forbidden

print("core stream all-zone v36 source contract: PASS")
