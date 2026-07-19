from pathlib import Path
s=Path('scripts/blender/urban_stream/node_builder.py').read_text(encoding='utf-8')
for required in ('archive-water-plaza','ledger-stream-terrace','transit-stream-junction','accessible-ramp','blank-signage'):
 assert required in s
assert "'majorNodes':3" in s and "'activeFrontageProxy'" in s
print('stream primary nodes: PASS')
