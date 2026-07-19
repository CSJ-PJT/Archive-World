#!/usr/bin/env python3
import json,sys
from pathlib import Path
source=Path('scripts/blender/procedural_visual_foundation.py').read_text();assert all(x not in source for x in ('bpy.data.images.load','bpy.data.images.save','ShaderNodeTexImage','C:/Users/'))
if len(sys.argv)>1:
 report=json.loads(Path(sys.argv[1]).read_text());assert report['materialCount']==20;assert report['duplicateSignatures']==0;assert report['externalImageReferences']==0 and report['imageTextureNodes']==0 and report['externalImageDatablocks']==[];assert len({x['id'] for x in report['materials']})==20
print('procedural material library contract PASS')
