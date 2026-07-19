import tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from metropolitan.render_review_package import render
with tempfile.TemporaryDirectory() as d:
 m=render(d); assert m['count']>=40 and m['resolution']==[1920,1080] and m['photoreal'] is False
 assert all((Path(d)/name).stat().st_size>500 for name in m['files'])
print('Metropolitan review diagrams PASS',m['count'])
