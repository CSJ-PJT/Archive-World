#!/usr/bin/env python3
import argparse,json
from pathlib import Path
def validate(root):
 root=Path(root);m=json.loads((root/'manifest/core-district-3d.json').read_text());official=json.loads((root/'validation/actual-glb-validation.json').read_text())
 glbs=list(root.rglob('*.glb'));checks={'actualFamilies>=12':m['metrics']['actualFamilies']>=12,'blocks>=18':m['metrics']['actualBlocks']>=18,'instances>=180':m['metrics']['buildingInstances']>=180,'proxyRatio<10%':m['metrics']['planningProxyRatio']<.1,'anchorPlaced':m['metrics']['anchorInstances']>=1,'actualGLBs>=36':len(glbs)>=36,'validatorError0':official['summary']['errors']==0,'validatorWarning0':official['summary']['warnings']==0,'graphsConnected':all(m['graphs'][k]==1 for k in ('pedestrianComponents','vehicleComponents','serviceComponents','fireComponents')),'orphanEntrance0':m['graphs']['orphanEntrances']==0,'blockedFire0':m['graphs']['blockedFireRoutes']==0,'canonicalFalse':all(not f['canonical'] for f in m['families'])}
 return {'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'counts':{'glbs':len(glbs),**m['metrics']},'officialValidator':official['summary']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();r=validate(a.root);print(json.dumps(r,indent=2));raise SystemExit(r['status']!='PASS')
