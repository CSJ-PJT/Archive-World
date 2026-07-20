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
    "_build_metropolitan_street_rooms", "v39-urban-room-paving",
    "v39-urban-room-arcade-roof", "v39-programmed-vehicle-body",
    "v40-street-room-glass", "v40-street-room-interior-light",
    '"scatterPlacement": False',
    "core-stream-ledger-transit-v47.glb", '"officeV5Changed": False',
    '"structuralPlausibility"', '"coreMeetsWindowRoomBack"',
    "_build_attached_identity_frames", "v41-attached-metropolitan-vertical-frame",
    "v41-attached-ground-portal-pier", "attachedIdentityFrames",
    "_build_cinematic_activity_nodes", "Broad parasols were repeatedly caught",
    "cinematicActivityNodes", '"scatterPlacement": False',
    '"duplicateBridgeDecks": 0', "portal layer now adds no deck",
    '"detachedWindowCount": detached_windows',
    "_build_stream_edge_activity_rooms", "v45-stream-room-inset-paving",
    "v45-stream-room-planter", "streamEdgeActivityRooms",
)
missing = [token for token in required if token not in text]
assert not missing, missing
for forbidden in ("bpy.data.images.load", "bpy.data.images.save", "Image Texture",
                  "architecture_factory_v3"):
    assert forbidden not in text, forbidden
print("core stream all-zone v45 inhabited stream-edge contract: PASS")
