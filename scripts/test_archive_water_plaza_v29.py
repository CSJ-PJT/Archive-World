from pathlib import Path

source=Path("scripts/blender/hero_zones/archive_water_plaza_v29.py").read_text(encoding="utf-8")
for token in (
    "ATTACHED_BUILDING_BODY_PLUS_INHABITED_PROMENADE",
    "v29-promenade-room-paving",
    "v29-promenade-room-planter",
    "v29-cafe-room-canopy",
    "v29-cafe-room-warm-soffit",
    "activityCompositions",
    "blankPavingMitigation",
    "identityFrameDatum",
    "TECHNICAL_PASS_VISUAL_GATE_PENDING",
):assert token in source
for forbidden in ("bpy.data.images.load","bpy.data.images.save","ShaderNodeTexImage"):
    assert forbidden not in source
print("archive water plaza v29 inhabited promenade contract: PASS")
