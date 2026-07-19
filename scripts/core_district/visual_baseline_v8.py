#!/usr/bin/env python3
import argparse,json
from pathlib import Path
CAMERAS=('aerial-daylight','aerial-dusk','aerial-night','archive-plaza','ledger-boulevard','transit-frontage','pedestrian-street','service-lane','park-edge','loading-dropoff','support-family-closeup')
def analyze(root):
 root=Path(root);renders=list((root/'renders').glob('*.png'));perf=json.loads((root/'reports/viewer-performance-cdp.json').read_text())
 rows=[{'camera':c,'baselineEvidenceCount':sum(c.split('-')[0] in p.name for p in renders),'knownFailure':c in ('aerial-night','archive-plaza','service-lane','support-family-closeup'),'status':'FAILED_BASELINE' if c in ('aerial-night','archive-plaza','service-lane','support-family-closeup') else 'BASELINE'} for c in CAMERAS]
 return {'status':'FROZEN_V8_BASELINE','renderCount':len(renders),'visualScore':68,'fps':27.7,'lowFps':6.0,'drawCalls':476,'triangles':594836,'cameras':rows,'rawPerformance':perf}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--output',required=True);a=p.parse_args();r=analyze(a.root);Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(r,indent=2));print(json.dumps(r))
