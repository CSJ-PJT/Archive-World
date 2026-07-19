from pathlib import Path
s=Path('scripts/blender/urban_stream/generate_stream.py').read_text(encoding='utf-8')
for x in ('build_edges','build_bridges','build_nodes','build_landscape_activity','export_scene.gltf','directReferenceCopy'):
 assert x in s
assert 'architecture_factory_v3' not in s
print('stream generator contract: PASS')
