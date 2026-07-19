from metropolitan.support_families import family_catalog

rows=family_catalog()
assert len(rows)==42 and len({r['id'] for r in rows})==42
assert sum(r['status']=='PO_REVIEW_CANDIDATE_FROZEN' for r in rows)==2
for row in rows:
 assert row['qualityScore']>=65 and row['canonical'] is False and row['cityApplied'] is False
 assert all(row['facades'][side] for side in ('front','side','rear','roof'))
 assert row['orientation']['entrance'] and row['orientation']['service']
 assert row['provenance']['referenceMeshCopied'] is False
print('Metropolitan support families PASS',len(rows))
