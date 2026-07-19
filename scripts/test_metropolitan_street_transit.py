#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts/metropolitan'))
from street_transit import build_street_graph,build_transit,connected
g=build_street_graph();t=build_transit(g)
assert len(g['edges'])>=500 and len(g['nodes'])>=100
assert all(connected(g,m) for m in ('vehicle','pedestrian','service','fire'))
assert len(t['railLines'])==3 and len(t['stations'])>=18 and len(t['transferStations'])>=3
assert len([r for r in t['busRoutes'] if r['class']=='trunk'])==6 and len([r for r in t['busRoutes'] if r['class']=='feeder'])==12
assert len(t['busStops'])>=80 and t['simulationRuntimeIntegration'] is False
assert all(e['crosswalk'] and e['serviceAccess'] for e in g['edges'])
print('Metropolitan street/transit graphs PASS',len(g['nodes']),len(g['edges']),len(t['stations']),len(t['busStops']))
