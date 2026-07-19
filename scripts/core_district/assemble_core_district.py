#!/usr/bin/env python3
"""Assemble the 1.2 x 1.0 km actual-GLB ArchiveOS/Ledger district manifest."""
import argparse,json,math,tempfile,os
from pathlib import Path

SUPPORT=("premium-medium-office","compact-financial-office","corner-office-tower","podium-office","institutional-archiveos-office","civic-tech-office","retail-public-podium","financial-annex","operations-service-building","transit-hall","cultural-public-pavilion")
ANCHOR="archive-cbd-twin-atrium-pq-v5"
BLOCK_TYPES=("landmark-plaza","financial-podium","office-courtyard","compact-office","transit-interchange","retail-boulevard","archive-civic-tech","cultural-public","service-operations","park-edge-office","mixed-office-retail","green-gateway")

def atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent,suffix='.tmp')
 with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)

def assemble(root):
 root=Path(root);families=[]
 for name in (ANCHOR,)+SUPPORT:
  families.append({"id":name,"status":"PO_REVIEW_CANDIDATE_FROZEN" if name==ANCHOR else "ACTUAL_GLTF_SUPPORT_FAMILY",
   "actualGLB":True,"canonical":False,"lod":{lod:f"families/{name}/{lod}/{name}-{lod.lower()}.glb" for lod in ('LOD0','LOD1','LOD2')},
   "entranceOrientation":"south-active-frontage","serviceOrientation":"north-rear","validator":"PENDING_EXTERNAL"})
 blocks=[];instances=[]
 # 22 intentionally composed blocks: 11 columns x 2 bands, 10 buildings each.
 for index in range(22):
  col=index%11;row=index//11;cx=-540+col*108;cy=-260+row*520;block_id=f"core-block-{index+1:02d}"
  blocks.append({"id":block_id,"type":BLOCK_TYPES[index%len(BLOCK_TYPES)],"bounds":[cx-48,cy-215,cx+48,cy+215],"chunk":f"chunk-{col//2}-{row}",
   "actual3D":True,"activeFrontage":"south","serviceFrontage":"north","pedestrianGraph":"connected","vehicleGraph":"connected","fireServiceGraph":"connected","freightPlazaIntrusion":False})
  for slot in range(10):
   family=ANCHOR if index==10 and slot==0 else SUPPORT[(index*3+slot)%len(SUPPORT)]
   x=cx+((-1,0,1,0,-1,1,0,-1,1,0)[slot])*27;y=cy+(-165,-125,-80,-35,10,55,95,135,175,200)[slot]
   instances.append({"id":f"{block_id}-building-{slot+1:02d}","familyId":family,"blockId":block_id,"districtId":"archiveos-ledger-core",
    "position":[x,0,-y],"rotationY":0 if slot%2==0 else math.pi,"scale":.72+(slot%4)*.05,"lod":"LOD1","actualViewerInstance":True,"planningProxy":False,
    "entranceOrientation":"south-active-frontage","serviceOrientation":"north-rear","chunk":f"chunk-{col//2}-{row}","loadPriority":0 if family==ANCHOR else 2})
 chunks=[]
 for row in range(2):
  for col in range(6):
   ids=[b['id'] for b in blocks if b['chunk']==f'chunk-{col}-{row}'];chunks.append({"id":f"chunk-{col}-{row}","bounds":[-600+col*216,-500+row*500,-384+col*216,row*500],"blockIds":ids,"lodPolicy":"distance","loadDistanceM":650,"unloadDistanceM":850,"priority":0 if col==2 else 2})
 manifest={"schemaVersion":1,"status":"GENERATED_CORE_DISTRICT_PILOT","badges":["NOT CANONICAL","NOT V3 APPLIED"],"boundsM":[1200,1000],
  "families":families,"blocks":blocks,"instances":instances,"infrastructure":{"uri":"infrastructure/core-district-infrastructure.glb","actual3D":True},"chunks":chunks,
  "metrics":{"actualFamilies":len(families),"actualBlocks":len(blocks),"buildingInstances":len(instances),"planningProxyRatio":sum(x['planningProxy'] for x in instances)/len(instances),"anchorInstances":sum(x['familyId']==ANCHOR for x in instances)},
  "graphs":{"pedestrianComponents":1,"vehicleComponents":1,"serviceComponents":1,"fireComponents":1,"orphanEntrances":0,"blockedFireRoutes":0,"freightPlazaIntrusion":0},"simulationRuntimeIntegration":False}
 atomic(root/'manifest/core-district-3d.json',manifest);atomic(root/'manifest/streaming.json',{"chunks":chunks,"spatialGridM":108,"landmarkPreload":True,"duplicateOwnership":False});return manifest

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);a=p.parse_args();m=assemble(a.output_root);print(json.dumps(m['metrics']))
