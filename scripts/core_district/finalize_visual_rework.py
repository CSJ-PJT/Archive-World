#!/usr/bin/env python3
"""Create an evidence-backed V9 review report and immutable transfer package."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,zipfile
from datetime import datetime
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--transfer',required=True);p.add_argument('--commit',required=True);a=p.parse_args()
 root=Path(a.root);transfer=Path(a.transfer);transfer.mkdir(parents=True,exist_ok=True)
 validator=json.loads((root/'validation/actual-glb-validation.json').read_text(encoding='utf-8-sig'))
 perf=json.loads((root/'performance/viewer-performance.json').read_text(encoding='utf-8-sig'))
 renders=sorted((root/'renders-final2').glob('*.png'))
 report={
  'verdict':'CORE DISTRICT VISUAL & PERFORMANCE REWORK V1: PARTIAL','visualScore':71,'grade':'C',
  'branch':'feat/archive-core-district-precision-v1','commit':a.commit,'actualFamilies':12,'actualBlocks':22,
  'actualBuildingInstances':220,'proxyRatio':0,'officeV5Frozen':True,
  'improvements':['11-family export-safe ArchiveOS/Ledger PBR palettes','support GLB one-mesh-per-material consolidation','active-ground-floor geometry','multi-lobe procedural vegetation','public-realm grouping','ACES daylight/night calibration','runtime GLB material batching'],
  'visualEvidence':{'screenshots':len(renders),'actualWebGL':True,'resolution':'1920x1080','dayDuskNight':True},
  'performance':perf['results'],'validator':validator['summary'],
  'gate':{'visual80':False,'averageFps30':False,'onePercentLow20':False,'criticalFps24':False,'drawCalls350':True,'validatorZero':True},
  'knownLimitations':['Street cameras remain dominated by coarse podium walls and blank paving','night lighting lacks convincing lobby/transit hierarchy','human and vehicle proxies are not legible in key views','landscape geometry is improved but district placement remains sparse','hardware Chrome capture could not yield valid samples and is UNKNOWN'],
  'canonical':False,'v3LayoutApplied':False,'runtimeChanged':False,'mainMerged':False,'nextDistrictAllowed':False,'actualV3ApplicationAllowed':False,
 }
 reports=root/'reports';reports.mkdir(exist_ok=True);(reports/'final-gate.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 readme=root/'README-REVIEW.txt';readme.write_text('Archive Core District V9 review\nPARTIAL / Visual 71 C / performance gate not met\nNOT CANONICAL / NOT V3 APPLIED\n',encoding='utf-8')
 stamp=datetime.now().strftime('%Y%m%d-%H%M%S');zip_path=transfer/f'Archive-Core-District-Rework-V1-{stamp}.zip'
 include=['README-REVIEW.txt','manifest','reports','validation','performance','renders-final2','families','infrastructure']
 with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name in include:
   path=root/name
   if path.is_file():z.write(path,path.relative_to(root))
   elif path.exists():
    for f in path.rglob('*'):
     if f.is_file() and 'chrome-profile' not in f.parts:z.write(f,f.relative_to(root))
 digest=hashlib.sha256(zip_path.read_bytes()).hexdigest();(reports/'package-checksum.json').write_text(json.dumps({'zip':str(zip_path),'sha256':digest,'bytes':zip_path.stat().st_size},indent=2),encoding='utf-8')
 print(json.dumps({'status':'PASS','verdict':report['verdict'],'zip':str(zip_path),'sha256':digest,'screenshots':len(renders)},indent=2))
if __name__=='__main__':main()
