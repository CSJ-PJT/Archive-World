import json
from pathlib import Path
root=Path(__file__).parents[1];c=json.loads((root/'config/core-district-precision-v1.json').read_text())
assert c['boundsMeters']==[1200,1000] and c['targets']['actualFamilies']>=12
assert c['frozenAnchor']['mutable'] is False and c['metropolitanVisualCity']=='NOT_IMPLEMENTED'
assert all(x in c['prohibitions'] for x in ('canonical-mutation','v3-layout-mutation','runtime-mutation','main-merge'))
print('Core district baseline PASS')
