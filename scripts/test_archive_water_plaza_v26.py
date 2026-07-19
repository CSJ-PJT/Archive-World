from pathlib import Path
source=Path('scripts/blender/hero_zones/archive_water_plaza_v26.py').read_text(encoding='utf-8')
facade=Path('scripts/blender/hero_zones/archive_water_plaza_v14.py').read_text(encoding='utf-8')
for token in ('FACADE_GLASS_RECESS_M=.12','FACADE_GLASS_THICKNESS_M=.08',
              'TOWER_FACADE_CAVITY_DEPTH_M=v14.FACADE_GLASS_RECESS_M+v14.FACADE_GLASS_THICKNESS_M',
              'glassToStructuralFaceGapM','sideGlassToStructuralFaceGapM',
              'V26_ALL_SIDES_STRUCTURAL_OPENING_DATUM'):
    assert token in source
for token in ('structural_face_y','glass_front_y','glass_y','glass_back_y','glass_back_gap',
              'attachment_depth','-facade-return','opening-side-return','opening-head',
              'opening-sill','-occupied-interior-back','side-attached-vertical-frame',
              'side-opening-return'):
    assert token in facade
for forbidden in ('bpy.data.images.load','bpy.data.images.save','ShaderNodeTexImage'):
    assert forbidden not in source+facade
print('archive water plaza v26 connected opening datum: PASS')
