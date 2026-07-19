from pathlib import Path
s=Path('scripts/blender/urban_stream/landscape_activity.py').read_text(encoding='utf-8')
assert 'stream-tree-crown' in s and 'human-proxy' in s and 'pedestrian-light' in s
assert "'floatingObjects':0" in s and "'waterIntrusion':0" in s
print('stream landscape/activity: PASS')
