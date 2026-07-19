#!/usr/bin/env python3
import json,sys
from pathlib import Path
p=Path('config/render-studio-presets.json');items=json.loads(p.read_text(encoding='utf-8'));assert len(items)==8;assert len({x['id'] for x in items})==8
required={'camera','exposure','color','lights','world','ground','resolution','samples','timeoutSeconds','expectedLuminance'}
assert all(required<=x.keys() for x in items);assert len({x['target'] for x in items})>=5
source=Path('scripts/blender/calibrated_render_studio.py').read_text(encoding='utf-8');analyzer=Path('scripts/urban/analyze_render_studio.py').read_text(encoding='utf-8');assert 'C:/Users/' not in source+analyzer;assert 'bpy.data.images.load' not in source
if len(sys.argv)>1:
 report=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));assert report['presets']==8 and report['passed']==8;assert len(report['targets'])>=5;assert all(x['pngSignature']=='89504e470d0a1a0a' for x in report['reports'])
print('calibrated render studio contract PASS')
