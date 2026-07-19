#!/usr/bin/env python3
import argparse,hashlib,json,time,zipfile
from pathlib import Path
def package(root,transfer,commit):
 root=Path(root);transfer=Path(transfer);transfer.mkdir(parents=True,exist_ok=True);stamp=time.strftime('%Y%m%d-%H%M%S');report=root/'reports';report.mkdir(exist_ok=True)
 summary={'verdict':'CORE DISTRICT PRECISION IMPLEMENTATION V1: PARTIAL','branch':'feat/archive-core-district-precision-v1','commit':commit,'viewer':'http://127.0.0.1:4176/?mode=core3d','actualFamilies':12,'actualGlbs':37,'blocks':22,'instances':220,'proxyRatio':0,'visualScore':68,'grade':'C','canonical':False,'v3Applied':False,'limitations':['30 FPS gate missed in headless measurement','night/street visual quality below B','support-family scores remain provisional']}
 (report/'executive-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');zpath=transfer/f'Archive-Core-District-Precision-V1-{stamp}.zip'
 with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(root.rglob('*')):
   if p.is_file() and 'cache' not in p.parts and 'logs' not in p.parts:z.write(p,p.relative_to(root))
 digest=hashlib.sha256(zpath.read_bytes()).hexdigest();(transfer/f'{zpath.name}.sha256').write_text(f'{digest}  {zpath.name}\n');return {'zip':str(zpath),'bytes':zpath.stat().st_size,'files':len(zipfile.ZipFile(zpath).namelist()),'sha256':digest}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--transfer',required=True);p.add_argument('--commit',required=True);a=p.parse_args();print(json.dumps(package(a.root,a.transfer,a.commit),indent=2))
