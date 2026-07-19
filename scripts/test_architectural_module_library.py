#!/usr/bin/env python3
import json,sys
from pathlib import Path
source=Path('scripts/blender/architectural_module_library.py').read_text(encoding='utf-8')
for forbidden in ('bpy.data.images.load','bpy.data.images.save','Image Texture','C:/Users/'):assert forbidden not in source
for required in ('recessed-bay','curtain-wall-panel','apartment-lobby','atrium-entry','machine-room','communications-proxy','fire-access','landscape-buffer'):assert required in source
if len(sys.argv)>1:
 report=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));assert report['moduleCount']==45;assert len(report['boards'])==5;assert all(v==0 for v in report['validation'].values());assert all(len(x['anchorPoints'])>=3 and set(x['lod'])=={'LOD0','LOD1','LOD2'} for x in report['modules']);assert all(x['pngSignature']=='89504e470d0a1a0a' for x in report['boards'])
print('architectural module library contract PASS')
