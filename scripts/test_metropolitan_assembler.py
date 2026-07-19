from metropolitan.city_assembler import assemble_city

a=assemble_city(); b=assemble_city()
assert a==b
assert len(a['districts'])>=7 and len(a['families'])>=30 and len(a['blocks'])>=80
assert 2500<=len(a['instances'])<=5000, len(a['instances'])
assert len({x['familyId'] for x in a['instances']})>=30
assert all(not x['canonical'] and not x['v3Applied'] for x in a['instances'])
po=sum(x['status']=='PO_REVIEW_CANDIDATE_FROZEN' for x in a['instances'])
assert po < len(a['instances'])*.08
print('Metropolitan city assembler PASS',len(a['blocks']),len(a['instances']),po)
