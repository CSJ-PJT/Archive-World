#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts/metropolitan'))
from district_dna import district_records
ds=district_records(); assert len(ds)>=12 and len({d['id'] for d in ds})==len(ds)
assert {'archiveos','ledger','market','nexus','logistics','residential','civic','infrastructure'} <= {d['dnaId'] for d in ds}
for d in ds:
 assert d['areaM2']>0 and len(d['polygon'])==4
 assert 0<=d['dna']['buildingCoverage']<=1 and 0<=d['dna']['greenRatio']<=1
 assert d['dna']['averageHeightM']<=d['dna']['maximumHeightM']
print('Metropolitan District DNA application PASS')
