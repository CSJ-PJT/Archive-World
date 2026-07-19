#!/usr/bin/env python3
"""Strict contract validator for the Generated Metropolitan Pilot."""
import json
from .city_assembler import assemble_city
from .street_transit import build_street_graph,build_transit,connected
from .green_blue import build_green_blue
from .public_realm import build_public_realm
from .skyline_metrics import analyze

def validate(seed=7302026):
 city=assemble_city(seed); street=build_street_graph(); transit=build_transit(street); green=build_green_blue(); realm=build_public_realm(seed); analysis=analyze(seed)
 checks={
  "districts>=7":len(city['districts'])>=7,"families>=30":len(city['families'])>=30,"blockVariants>=80":analysis['metrics']['blockVariantCount']>=80,
  "instances>=2500":len(city['instances'])>=2500,"streetSegments>=500":len(street['edges'])>=500,"intersections>=100":len(street['nodes'])>=100,
  "vehicleConnected":connected(street,'vehicle'),"pedestrianConnected":connected(street,'pedestrian'),"serviceConnected":connected(street,'service'),"fireConnected":connected(street,'fire'),
  "orphanEntrance=0":all(i['entranceSide'] for i in city['instances']),"serviceAccess=100%":all(i['serviceSide'] for i in city['instances']),
  "transitStations>=18":len(transit['stations'])>=18,"transferStations>=3":len(transit['transferStations'])>=3,"busStops>=80":len(transit['busStops'])>=80,
  "greenRatio>=18%":green['greenOpenSpaceRatioProxy']>=.18,"greenConnected":green['connectedComponents']==1,"riverfrontContinuous":green['riverfrontPromenade']['continuous'],
  "publicRealm>=150":len(realm['publicRealm'])>=150,"skylineDiversity>=75":analysis['skyline']['diversityScore']>=75,"districtTransition>=75":analysis['skyline']['districtTransitionScore']>=75,
  "familyRepetition<8%":analysis['metrics']['familyRepetitionMaximumShare']<.08,"canonicalMutation=0":not city['canonical'],"v3LayoutMutation=0":not city['v3Applied'],
  "simulationRuntimeIntegration=false":transit['simulationRuntimeIntegration'] is False and realm['simulationRuntimeIntegration'] is False,
 }
 errors=[key for key,value in checks.items() if not value]
 return {"status":"PASS" if not errors else "FAIL","checks":checks,"errors":errors,"counts":{"districts":len(city['districts']),"families":len(city['families']),"blocks":len(city['blocks']),"instances":len(city['instances']),"streetEdges":len(street['edges']),"transitStations":len(transit['stations']),"publicRealm":len(realm['publicRealm'])},"scope":"planning-and-generated-contracts"}

if __name__=='__main__':
 result=validate();print(json.dumps(result,indent=2));raise SystemExit(0 if result['status']=='PASS' else 1)

