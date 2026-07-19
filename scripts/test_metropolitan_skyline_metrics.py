from metropolitan.skyline_metrics import analyze
r=analyze(); s=r['skyline']; m=r['metrics']
assert s['diversityScore']>=75 and s['districtTransitionScore']>=75
assert s['logisticsLowProfile'] and len(s['viewCorridors'])>=3
assert m['uniqueFamilies']>=30 and m['blockVariantCount']>=80 and m['buildingInstances']>=2500
assert m['streetSegments']>=500 and m['intersections']>=100 and m['transitStations']>=18
assert m['greenOpenSpaceRatio']>=.18 and m['familyRepetitionMaximumShare']<.08
print('Metropolitan skyline/metrics PASS',m)
