from pathlib import Path

source = Path("scripts/blender/hero_zones/archive_water_plaza_v28.py").read_text(encoding="utf-8")
facade = Path("scripts/blender/hero_zones/archive_water_plaza_v14.py").read_text(encoding="utf-8")

for token in (
    "ATTACHED_BUILDING_BODY_AND_PRECISION_EDGE_PASS",
    "S_95_PLUS",
    "TECHNICAL_PASS_VISUAL_GATE_PENDING",
    "identityFrameDatum",
    "precisionEdgeObjectCount",
    "frontGapM",
    "sideGapM",
):
    assert token in source

for token in (
    "add_s_grade_body_articulation",
    "lower_tower_depth=depth*.76",
    "v28-lower-architectural-pier",
    "v28-corner-room-floor",
    "v28-corner-room-back",
    "v28-corner-room-glass",
    "v28-attached-transfer-slab",
    "v28-rear-service-core",
    "v28-rear-service-louver",
):
    assert token in facade

for forbidden in (
    "bpy.data.images.load",
    "bpy.data.images.save",
    "ShaderNodeTexImage",
    "directReferenceCopy\": True",
):
    assert forbidden not in source + facade

print("archive water plaza v28 attached body contract: PASS")
