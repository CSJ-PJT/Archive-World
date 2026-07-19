import tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'core_district'))
from assemble_core_district import assemble
with tempfile.TemporaryDirectory() as d:
 m=assemble(d);assert m['metrics']=={'actualFamilies':12,'actualBlocks':22,'buildingInstances':220,'planningProxyRatio':0.0,'anchorInstances':1}
 assert all(x['actualViewerInstance'] and not x['planningProxy'] for x in m['instances'])
 assert all(b['fireServiceGraph']=='connected' and not b['freightPlazaIntrusion'] for b in m['blocks'])
 assert len(m['chunks'])==12 and m['graphs']['orphanEntrances']==0
print('Core district assembly PASS')
