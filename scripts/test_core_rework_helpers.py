import sys
from pathlib import Path
root=Path(__file__).parents[1];sys.path.insert(0,str(root/'scripts/blender/core_district_precision'))
from family_palette import PALETTES
assert len(PALETTES)==11 and len(set(PALETTES))==11
from batch_consolidation import consolidate
assert callable(consolidate)
print('Core visual rework helpers PASS')
