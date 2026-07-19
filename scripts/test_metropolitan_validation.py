from metropolitan.validate_metropolitan import validate
r=validate()
assert r['status']=='PASS',r['errors']
assert len(r['checks'])>=20 and all(r['checks'].values())
assert r['scope']=='planning-and-generated-contracts'
print('Metropolitan validation PASS',r['counts'])
