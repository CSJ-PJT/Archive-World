import ast
from pathlib import Path
p=Path(__file__).parents[1]/'scripts/blender/core_district_precision/support_family_generator.py';tree=ast.parse(p.read_text())
node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(getattr(t,'id',None)=='SPECS' for t in n.targets));specs=ast.literal_eval(node.value)
assert len(specs)==11 and len({x[0] for x in specs})==11
assert len({(x[1],x[2],x[3],x[4],x[5]) for x in specs})==11
text=p.read_text();assert 'main-lobby' in text and 'service-entry' in text and 'machine-room' in text
print('Core support family source PASS')
