from pathlib import Path
import ast

source = (Path(__file__).parent / "blender" / "hero_zones" /
          "core_stream_all_zones_v37.py")
text = source.read_text(encoding="utf-8")
ast.parse(text)
required = (
    "_enrich_deep_frontage", "_build_mixed_corridor_frontages",
    "_build_promenance_life", "interior-table", "interior-chair",
    "full-depth-jamb", "corridor-pavilion", "lower-promenade-bench",
    "_build_metropolitan_node_precision", "v38-ledger-formal-terrace",
    "v38-transit-transfer-plaza", "v38-node-bridge-portal-column",
    '"activityPlacement": "PROGRAMMED_BY_NODE"',
    "core-stream-ledger-transit-v38.glb", '"officeV5Changed": False',
    '"detachedWindowCount": detached_windows',
)
missing = [token for token in required if token not in text]
assert not missing, missing
for forbidden in ("bpy.data.images.load", "bpy.data.images.save", "Image Texture",
                  "architecture_factory_v3"):
    assert forbidden not in text, forbidden
print("core stream all-zone v38 metropolitan node contract: PASS")
