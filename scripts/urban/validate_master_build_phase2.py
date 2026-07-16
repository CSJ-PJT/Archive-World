"""Validate Master Build Phase 2 data contracts without reading or writing runtime/layout."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def read(relative):
 return json.loads((ROOT/relative).read_text(encoding='utf-8'))
def check(condition,message,errors):
 if not condition:errors.append(message)
def main():
 errors=[]
 refs=read('reference-intelligence/catalog.json');catalog=read('architecture-grammar/catalog.json')
 check(refs['referenceCount']==len(catalog['references'])==43,'reference count mismatch',errors)
 check(refs['policy']['directMeshReuse'] is False,'direct mesh reuse must be false',errors)
 dna=read('city-genome/district-dna-v2.json');check(set(dna['districts'])=={'archiveos','ledger','market','nexus','logistics','residential','infrastructure'},'district DNA incomplete',errors)
 eco=read('city-genome/street-landscape-vehicle-human-taxonomy.json')
 for k,target in [('street',150),('landscape',100),('vehicle',80),('human',100)]:check(eco[k]['targetFamilies']>=target,f'{k} target below minimum',errors)
 metrics=read('city-genome/city-metrics-v1.json');check(metrics['status']=='PLAN_ONLY','metrics must remain plan-only',errors)
 sim=read('city-genome/simulation-skeleton.json');check(sim['runtimeIntegration'] is False,'simulation must not integrate runtime',errors)
 print(json.dumps({'pass':not errors,'errors':errors,'references':refs['referenceCount'],'districts':len(dna['districts']),'targets':{x:eco[x]['targetFamilies'] for x in ('street','landscape','vehicle','human')}},indent=2))
 raise SystemExit(bool(errors))
if __name__=='__main__':main()
