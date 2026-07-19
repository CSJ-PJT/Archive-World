from pathlib import Path


source = Path(__file__).parent / "blender" / "hero_zones" / "archive_water_plaza_v31.py"
text = source.read_text(encoding="utf-8")

required = (
    "add_facade_room_hierarchy",
    "v31-facade-room-floor",
    "v31-facade-room-ceiling",
    "v31-facade-room-back",
    "v31-facade-room-return",
    "v31-facade-room-glass",
    "v31-entry-vestibule-floor",
    "v31-entry-vestibule-soffit",
    "v31-entry-vestibule-return",
    "v31-entry-vestibule-glass",
    "boundedRoomRule",
    "apply_selective_architectural_edges",
    "V31 selective architectural edge",
    "add_precision_landscape_rooms",
    "v31-linear-garden-retaining-edge",
    "precisionLandscapeRoomCount",
    "officeV5Changed",
)
missing = [token for token in required if token not in text]
assert not missing, missing
assert "bpy.data.images.load" not in text
assert "bpy.data.images.save" not in text
assert "Image Texture" not in text
print("archive water plaza v31 attached room hierarchy contract: PASS")
