#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts/metropolitan'))
from green_blue import build_green_blue
g=build_green_blue()
assert g['river']['continuity'] and g['riverfrontPromenade']['continuous']
assert len(g['neighborhoodParks'])>=12 and len(g['pocketParks'])>=30 and len(g['greenCorridors'])>=4
assert len(g['modules'])>=100 and g['connectedComponents']==1
assert g['greenOpenSpaceRatioProxy']>=.18 and g['logisticsResidentialBuffer']['continuous']
print('Metropolitan green/blue network PASS',g['greenOpenSpaceRatioProxy'])
