import sys
from pathlib import Path
sys.path.insert(0,str(Path('scripts/blender/urban_stream')))
from bridge_builder import BRIDGE_TYPES
assert len(BRIDGE_TYPES)>=6 and len(set(BRIDGE_TYPES))==len(BRIDGE_TYPES)
assert 'service-crossing' in BRIDGE_TYPES and 'archive-gateway' in BRIDGE_TYPES
print('stream bridge contracts: PASS')
