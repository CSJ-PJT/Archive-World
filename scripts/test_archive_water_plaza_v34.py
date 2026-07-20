from pathlib import Path

source = (Path(__file__).parent / "blender" / "hero_zones" / "archive_water_plaza_v34.py").read_text(encoding="utf-8")
required = (
    "WALL_FIRST_BOUNDED_CURTAIN_WALL_AND_INHABITED_PODIUM",
    "v34-facade-room-back", "v34-integrated-glass-field",
    "v34-structural-facade-pier", "v34-attached-spandrel",
    "v34-frontage-continuous-floor", "v34-frontage-continuous-ceiling",
    "v34-frontage-continuous-back", "v34-bounded-frontage-glass",
    '"detachedWindowCount": 0', '"stackedDecorativeGridCount": 0',
    'assert len(bpy.data.images) == 0', '"minimumScore": 95',
    "_occludes_camera", '"smoothOrganicObjectCount"',
    "v34-signature-lobby-glass", "v34-signature-entry-terrace",
    '"signatureProjectedLobbyCount": 2',
    "v34-interior-floor-plate", "v34-primary-depth-frame",
    "v34-signature-cafe-table", '"signatureCafeTerraceCount": 2',
    "_add_architectural_tree", '"nearFieldTreeSilhouetteCount": 3',
)
for token in required:
    assert token in source, token
assert "bpy.data.images.load" not in source
assert "bpy.data.images.save" not in source
print("archive water plaza v34 wall-first architecture contract: PASS")
