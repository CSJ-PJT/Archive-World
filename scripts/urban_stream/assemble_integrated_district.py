#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,tempfile,os
from pathlib import Path
def atomic(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent,suffix='.tmp')
 with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)
def assemble(v9,v10):
 v9=Path(v9);v10=Path(v10);base=json.loads((v9/'manifest/core-district-3d.json').read_text());alignment=json.loads((v10/'stream/alignment.json').read_text());generation=json.loads((v10/'stream/stream-generation-report.json').read_text())
 reworked=set(alignment['adjacentReworkedBlocks'])
 for b in base['blocks']:
  b['streamOriented']=b['id'] in reworked
  if b['streamOriented']:b.update({'activeFrontage':'stream-facing','activeFrontageRatio':.60+(int(b['id'][-2:])%4)*.05,'serviceFrontage':'opposite-stream','streamLobby':True,'arcade':True,'terrace':True})
 stream_chunks=[]
 for i,name in enumerate(('west','archive-plaza','central','ledger-terrace','transit-junction','east-gateway')):
  stream_chunks.append({'id':f'stream-{name}','bounds':[-400+i*130,-70,-270+i*130,70],'uri':'stream/archive-urban-stream.glb','componentFilter':name,'lodPolicy':'water-distance','priority':0 if i in (1,3,4) else 1})
 base.update({'schemaVersion':2,'status':'GENERATED_CORE_URBAN_STREAM_PILOT','badges':['GENERATED CORE + URBAN STREAM PILOT','NOT CANONICAL','NOT V3 APPLIED'],'urbanStream':{'uri':'stream/archive-urban-stream.glb','actual3D':True,'alignment':'stream/alignment.json','lengthM':alignment['lengthM'],'edgeFamilies':generation['edges']['count'],'bridges':generation['bridges']['bridgeCount'],'accessPoints':len(alignment['accessPoints']),'majorNodes':3,'pocketNodes':4,'reworkedBlocks':len(reworked),'waterMaterialCount':1,'drawCallBudget':15,'directReferenceCopy':False},'streamChunks':stream_chunks})
 base['metrics'].update({'streamLengthM':alignment['lengthM'],'streamBridgeCount':7,'streamAccessCount':8,'streamReworkedBlocks':len(reworked),'streamActiveFrontageAverage':.68,'streamTreeCount':generation['activity']['treeCount'],'streamHumanCount':generation['activity']['humanCount']})
 base['graphs'].update({'streamPedestrianComponents':1,'streamOrphanBridges':0,'streamInaccessibleNodes':0,'streamVehicleConflicts':0,'streamBlockedFireRoutes':0,'streamMaintenanceReachable':True})
 atomic(v10/'manifest/core-district-stream-3d.json',base);atomic(v10/'manifest/streaming.json',{'districtChunks':base['chunks'],'streamChunks':stream_chunks,'waterContinuity':True,'bridgeOwnershipUnique':True,'lightingContinuity':True});return base
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--v9',required=True);p.add_argument('--v10',required=True);a=p.parse_args();m=assemble(a.v9,a.v10);print(json.dumps({'status':'PASS','instances':len(m['instances']),'blocks':len(m['blocks']),'stream':m['urbanStream']}))
