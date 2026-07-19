from pathlib import Path
source=Path('scripts/blender/hero_zones/archive_water_plaza_v26.py').read_text(encoding='utf-8')
facade=Path('scripts/blender/hero_zones/archive_water_plaza_v14.py').read_text(encoding='utf-8')
for token in ('TOWER_FACADE_CAVITY_DEPTH_M=.12','FACADE_GLASS_RECESS_M=.12','glassToStructuralFaceGapM":0.0','V26_STRUCTURAL_FACE_EQUALS_RECESSED_GLASS_DATUM'):
    assert token in source
for token in ('structural_face_y','glass_y','attachment_depth','-facade-return','-window-head','-window-sill'):
    assert token in facade
for forbidden in ('bpy.data.images.load','bpy.data.images.save','ShaderNodeTexImage'):
    assert forbidden not in source+facade
print('archive water plaza v26 connected opening datum: PASS')
