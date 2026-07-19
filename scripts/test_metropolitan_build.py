import tempfile,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from metropolitan.build_metropolitan import build,STAGES
with tempfile.TemporaryDirectory() as d:
 r=build(d,stop_after=STAGES[2]); assert r['status']=='PARTIAL' and len(r['completed'])==3
 r=build(d); assert r['status']=='COMPLETE' and r['completed']==list(STAGES)
 state=json.loads((Path(d)/'checkpoints'/'build-state.json').read_text())
 assert state['status']=='COMPLETE' and len(list((Path(d)/'stages').glob('*.json')))==9
print('Metropolitan reproducible build PASS')
