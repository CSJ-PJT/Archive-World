#!/usr/bin/env python3
"""Reproducible A-I Generated Metropolitan build with atomic checkpoints."""
import argparse,json,os,tempfile,time
from pathlib import Path
from .district_dna import district_records
from .street_transit import build_street_graph,build_transit
from .green_blue import build_green_blue
from .support_families import family_catalog
from .block_generator import variants
from .city_assembler import assemble_city
from .public_realm import build_public_realm
from .skyline_metrics import analyze

STAGES=("A-master-plan","B-networks","C-district-massing","D-block-placement","E-building-placement","F-public-realm","G-population-proxy","H-lod-streaming","I-review-manifest")
def atomic_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(dir=path.parent,suffix='.tmp')
 try:
  with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp): os.unlink(tmp)

def build(root,seed=7302026,resume=True,stop_after=None):
 root=Path(root); state_path=root/'checkpoints'/'build-state.json'; completed=[]
 if resume and state_path.exists(): completed=json.loads(state_path.read_text(encoding='utf-8')).get('completed',[])
 street=build_street_graph(); transit=build_transit(street); green=build_green_blue(); city=assemble_city(seed); realm=build_public_realm(seed); metrics=analyze(seed)
 payloads={
  STAGES[0]:{"cityBoundsM":[6000,5000],"districts":district_records(),"axes":["primary","secondary","partial-ring","riverfront","civic"],"futureExpansionInterfaces":["east","north"]},
  STAGES[1]:{"street":street,"transit":transit,"greenBlue":green}, STAGES[2]:{"districts":city['districts']},
  STAGES[3]:{"blockCatalog":variants(seed),"placedBlocks":city['blocks']}, STAGES[4]:{"familyCatalog":family_catalog(seed),"instances":city['instances']},
  STAGES[5]:{"publicRealm":realm['publicRealm']},STAGES[6]:{"vehicles":realm['vehicles'],"humans":realm['humans'],"simulationRuntimeIntegration":False},
  STAGES[7]:{"chunking":{"districtChunks":True,"blockChunks":True,"spatialIndex":"grid","instanceBatching":True},"lod":{"near":"LOD0","mid":"LOD1","far":"LOD2","veryFar":"skyline-proxy"}},
  STAGES[8]:{"status":"GENERATED_METROPOLITAN_PILOT","badges":["NOT CANONICAL","NOT V3 APPLIED"],"metrics":metrics,"cameraPresets":["city-aerial","district-hero","street-level","skyline","plan"]}}
 for stage in STAGES:
  if stage not in completed:
   atomic_json(root/'stages'/f'{stage}.json',payloads[stage]); completed.append(stage)
   atomic_json(state_path,{"status":"RUNNING","seed":seed,"completed":completed,"heartbeatEpoch":time.time()})
  if stage==stop_after: break
 status="COMPLETE" if len(completed)==len(STAGES) else "PARTIAL"
 atomic_json(state_path,{"status":status,"seed":seed,"completed":completed,"heartbeatEpoch":time.time()})
 return {"status":status,"completed":completed,"root":str(root)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);p.add_argument('--seed',type=int,default=7302026);p.add_argument('--no-resume',action='store_true');p.add_argument('--stop-after',choices=STAGES)
 a=p.parse_args();print(json.dumps(build(a.output_root,a.seed,not a.no_resume,a.stop_after),indent=2))
