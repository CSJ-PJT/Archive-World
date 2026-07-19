from metropolitan.benchmark_metropolitan import benchmark
r=benchmark();assert r['status']=='PASS' and r['viewerFps'] is None
assert [x['instances'] for x in r['results']][:3]==[500,1000,2500]
assert all(x['decoded']==x['instances'] and x['manifestBytes']>0 for x in r['results'])
print('Metropolitan manifest performance PASS',r['results'])
