#!/usr/bin/env python3
import json,sys
from pathlib import Path
source=Path('scripts/blender/generate_quality_pilot_lod2.py').read_text();assert 'bpy.data.images.load' not in source and 'bpy.data.images.save' not in source and 'C:/Users/' not in source
for report_path in sys.argv[1:]:
 r=json.loads(Path(report_path).read_text());m=r['metrics'];assert r['status']=='LOD2_SMOKE' and r['proceduralOnly'];assert r['grammarCompile']==r['modulePlan']==r['materialPlan']==r['noImagePath']=='PASS';assert m['sideRearComplete'] and m['serviceAccess'] and m['roofEquipment']>0 and m['entranceCount']>0 and m['groundContact'];assert len(r['renders'])==3 and all(x['pngSignature']=='89504e470d0a1a0a' for x in r['renders'])
print('quality pilot LOD2 contracts PASS')
