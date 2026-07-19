import sys
from pathlib import Path
sys.path.insert(0,str(Path('scripts/blender/urban_stream')))
from edge_builder import EDGE_FAMILIES
assert len(EDGE_FAMILIES)>=8 and len(set(EDGE_FAMILIES))==len(EDGE_FAMILIES)
assert {'stepped-seating','green-planted','service-maintenance','pocket-wetland'}<=set(EDGE_FAMILIES)
print('stream edge families: PASS')
