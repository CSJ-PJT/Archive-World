from pathlib import Path
t=(Path(__file__).parents[1]/'docs/urban/CORE_DISTRICT_PRECISION_V1.md').read_text()
for x in ('actual family 12','building instance 220','37 GLB','27.7 FPS','68/C','actual V3 application'):assert x in t,x
print('Core district documentation PASS')
