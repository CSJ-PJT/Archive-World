"""Topology and plan-only contract validation for Urban Grammar V1.1."""
import argparse,json,os,sys

REQUIRED_LAYERS={'building','street','publicRealm','pedestrianRoute','vehicleRoute','fireRoute'}

def connected(nodes,edges,mode):
 ids={n['id'] for n in nodes}; active=[e for e in edges if e['mode']==mode]
 if not active:return False,'no edges'
 seen={active[0]['from']}; changed=True
 while changed:
  changed=False
  for e in active:
   if e['from'] in seen and e['to'] not in seen:seen.add(e['to']);changed=True
   if e['to'] in seen and e['from'] not in seen:seen.add(e['from']);changed=True
 return all((e['from'] in seen and e['to'] in seen) for e in active),'ok'

def validate(path):
 d=json.load(open(path,encoding='utf-8')); errors=[]; graph=d.get('streetGraph',{}); nodes=graph.get('nodes',[]); edges=graph.get('edges',[]); ids={n.get('id') for n in nodes}
 if d.get('status')!='GENERATED_PLAN_ONLY':errors.append('not plan-only')
 if REQUIRED_LAYERS-set(d.get('layers',{})):errors.append('missing layer declaration')
 if len(ids)!=len(nodes):errors.append('duplicate graph node')
 if any(e.get('from') not in ids or e.get('to') not in ids for e in edges):errors.append('dangling graph edge')
 for mode in ('pedestrian','vehicle','fire','service'):
  ok,msg=connected(nodes,edges,mode)
  if not ok:errors.append(f'{mode}: {msg}')
 # Service is private: it must not be labelled public realm.
 if any(e['mode']=='service' and e.get('public',True) for e in edges):errors.append('service route is public')
 return {'plan':d.get('districtId'),'pass':not errors,'errors':errors,'nodes':len(nodes),'edges':len(edges)}

def main():
 p=argparse.ArgumentParser();p.add_argument('plans',nargs='+');a=p.parse_args();results=[validate(x) for x in a.plans];print(json.dumps({'pass':all(x['pass'] for x in results),'results':results},indent=2));sys.exit(0 if all(x['pass'] for x in results) else 1)
if __name__=='__main__':main()
