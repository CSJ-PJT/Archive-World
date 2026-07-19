import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'urban_stream'))
from plan_alignment import plan
p=plan()
assert 650<=p['lengthM']<=900 and len(p['segments'])>=10
assert len({segment['edgeType'] for segment in p['segments']}) >= 8
assert len(p['bridges'])>=6 and len(p['accessPoints'])>=6
assert sum(n['role']=='MAJOR' for n in p['nodes'])==3 and sum(n['role']=='POCKET' for n in p['nodes'])>=4
assert len(p['adjacentReworkedBlocks'])>=8 and 'NO_DIRECT_COPY' in p['originality']
print('urban stream alignment: PASS')
