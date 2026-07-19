#!/usr/bin/env python3
import argparse,json
from pathlib import Path
def report(root):
 root=Path(root);manifest=json.loads((root/'manifest/core-district-3d.json').read_text());validation=json.loads((root/'validation/actual-glb-validation.json').read_text());renders=list((root/'renders').glob('*.png'))
 score={"Buildings":11,"Block composition":10,"Street/public realm":11,"Landscape":5,"Transit":5,"Service/rear":4,"Skyline":7,"Street-level credibility":6,"Archive identity":3,"Lighting":3,"Performance/LOD":3};total=sum(score.values())
 result={"verdict":"PARTIAL","visualScore":total,"grade":"C" if total>=65 else "D","score":score,"supportFamilyVisualScore":"PROVISIONAL_68_REQUIRES_PO_IMAGE_REVIEW",
  "technical":{"actualFamilies":manifest['metrics']['actualFamilies'],"actualBlocks":manifest['metrics']['actualBlocks'],"instances":manifest['metrics']['buildingInstances'],"proxyRatio":manifest['metrics']['planningProxyRatio'],"validator":validation['summary'],"renderCount":len(renders)},
  "failures":["District visual score below B/80.","Night lighting lacks finished emissive facade and public-realm identity.","Several street cameras remain compositionally weak.","Headless WebGL average FPS remains below 30 and 1% low target.","Vegetation and humans are procedural low-detail geometry."],
  "boundaries":{"canonical":False,"v3Applied":False,"runtimeModified":False,"mainMerged":False}}
 (root/'reports').mkdir(exist_ok=True);(root/'reports'/'visual-quality.json').write_text(json.dumps(result,indent=2),encoding='utf-8');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();print(json.dumps(report(a.root),indent=2))
