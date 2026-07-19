from metropolitan.public_realm import build_public_realm,REALM_KINDS,VEHICLES,HUMANS
r=build_public_realm()
assert len(REALM_KINDS)==20 and len(VEHICLES)==10 and len(HUMANS)==10
assert len(r['publicRealm'])>=150 and len(r['vehicles'])>=100 and len(r['humans'])>=500
assert r['simulationRuntimeIntegration'] is False and r['placementPolicy']=='relationship-driven'
assert all(x['relationship'] for x in r['publicRealm'])
print('Metropolitan public realm PASS',len(r['publicRealm']),len(r['vehicles']),len(r['humans']))
