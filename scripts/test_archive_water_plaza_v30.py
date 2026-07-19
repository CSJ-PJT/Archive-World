from pathlib import Path

source=Path("scripts/blender/hero_zones/archive_water_plaza_v30.py").read_text(encoding="utf-8")
facade=Path("scripts/blender/hero_zones/archive_water_plaza_v14.py").read_text(encoding="utf-8")
for token in (
    "DEEP_ATTACHED_REVEALS_AND_NATURAL_CANOPY",
    "FACADE_GLASS_RECESS_M=.26",
    "TOWER_FACADE_CAVITY_DEPTH_M=.34",
    "v30-tree-tapered-trunk",
    "v30-tree-primary-branch",
    "v30-tree-secondary-branch",
    "v30-tree-porous-crown",
    "add_podium_side_activation",
    "v30-podium-side-attached-glass",
    "v30-podium-side-room-back",
    "treeCrownLobesPerTree",
    "intentionalFacadeRecessM",
):assert token in source+facade
for forbidden in ("bpy.data.images.load","bpy.data.images.save","ShaderNodeTexImage"):
    assert forbidden not in source+facade
print("archive water plaza v30 deep reveal and natural canopy contract: PASS")
