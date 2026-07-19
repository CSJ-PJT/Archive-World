#!/usr/bin/env python3
"""Create review ZIP and SHA-256 without modifying repository assets."""
import argparse,hashlib,json,time,zipfile
from pathlib import Path
from .validate_metropolitan import validate
from .skyline_metrics import analyze
from .benchmark_metropolitan import benchmark

def package(root,transfer,commit):
 root=Path(root);transfer=Path(transfer);transfer.mkdir(parents=True,exist_ok=True)
 stamp=time.strftime('%Y%m%d-%H%M%S');report=root/'reports';report.mkdir(parents=True,exist_ok=True)
 summary={"verdict":"PARTIAL_PENDING_VISUAL_PO_REVIEW","branch":"feat/archive-metropolitan-seed-city-v1","commit":commit,
  "statusLegend":["PO_REVIEW_CANDIDATE_FROZEN","CITY_SUPPORT_PROTOTYPE","PLACEHOLDER","INFRASTRUCTURE_PROXY"],
  "technicalValidation":validate(),"planningMetrics":analyze(),"performance":benchmark(),
  "limitations":["Support families are planning contracts, not B-grade canonical GLBs.","Review PNGs are planning diagrams, not photoreal city renders.","Viewer FPS/GPU memory were not measured.","No canonical, V3 layout, Runtime, or main mutation."],
  "approvalGate":"PO visual review; no actual V3 application or canonical promotion is authorized."}
 (report/'executive-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 (report/'README.txt').write_text('Archive Metropolitan Seed City V1\nGENERATED PILOT / NOT CANONICAL / NOT V3 APPLIED\nOpen review/png and stages. See executive-summary.json.\n',encoding='utf-8')
 zip_path=transfer/f'Archive-City-Metropolitan-Seed-V1-{stamp}.zip'
 with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for path in sorted(root.rglob('*')):
   if path.is_file(): z.write(path,path.relative_to(root))
 digest=hashlib.sha256(zip_path.read_bytes()).hexdigest();(transfer/f'{zip_path.name}.sha256').write_text(f'{digest}  {zip_path.name}\n',encoding='ascii')
 return {"zip":str(zip_path),"bytes":zip_path.stat().st_size,"sha256":digest,"files":len(zipfile.ZipFile(zip_path).namelist())}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--transfer',required=True);p.add_argument('--commit',required=True);a=p.parse_args();print(json.dumps(package(a.root,a.transfer,a.commit),indent=2))

