from metropolitan.block_generator import BLOCK_TYPES, variants

rows=variants()
assert len(BLOCK_TYPES)==5 and sum(map(len,BLOCK_TYPES.values()))==21
assert len(rows)==84 and len({r['id'] for r in rows})==84
for row in rows:
 assert row['network']['pedestrian']=='connected-loop'
 assert row['network']['publicFreightIntrusion'] is False
 assert row['adjacency']['forbidSameVariant'] is True
 assert row['provenance']['randomScatter'] is False
 assert row['parcelCount']>=3 and row['boundsM'][0]>=150
print('Metropolitan block generator PASS',len(rows))
