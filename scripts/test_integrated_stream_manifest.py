import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('scripts/urban_stream')))
from assemble_integrated_district import assemble
m=assemble(Path('/mnt/c/ArchiveData/World/Generated/v9/core-district-visual-performance-rework'),Path('/mnt/c/ArchiveData/World/Generated/v10/core-urban-stream-integrated-rework'))
assert m['urbanStream']['actual3D'] and m['urbanStream']['bridges']>=6
assert sum(b.get('streamOriented',False) for b in m['blocks'])>=8
assert m['graphs']['streamPedestrianComponents']==1 and m['graphs']['streamBlockedFireRoutes']==0
print('integrated stream manifest: PASS')
