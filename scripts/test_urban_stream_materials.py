from pathlib import Path
s=Path('scripts/blender/urban_stream/materials.py').read_text(encoding='utf-8')
assert 'bpy.data.images' in s and "'shallow-water'" in s
assert 'Image Texture' not in s and 'images.load' not in s and 'images.save' not in s
assert s.count("'provenance'")>=1
print('urban stream materials: PASS')
