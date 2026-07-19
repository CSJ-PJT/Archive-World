#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/'config/metropolitan-seed-city-v1.json').read_text())
schema=json.loads((ROOT/'city-genome/schemas/metropolitan-master-plan.schema.json').read_text())
assert cfg['boundsMeters']==[6000,5000] and cfg['targets']['buildingInstancesMin']>=2500
assert cfg['frozenPOBaselines']['office']['score']==82 and cfg['frozenPOBaselines']['residential']['score']==82
assert all(x['status']=='PO_REVIEW_CANDIDATE_FROZEN' for x in cfg['frozenPOBaselines'].values())
assert schema['properties']['status']['const']=='GENERATED_METROPOLITAN_PILOT'
assert cfg['canonical'] is False and cfg['v3Applied'] is False
print('Metropolitan baseline/schema PASS')
