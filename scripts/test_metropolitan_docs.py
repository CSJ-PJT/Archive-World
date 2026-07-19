from pathlib import Path
p=Path(__file__).parents[1]/'docs/urban/METROPOLITAN_SEED_CITY_V1.md';text=p.read_text(encoding='utf-8')
for phrase in ('Generated planning pilot','NOT CANONICAL','NOT V3 APPLIED','3,942','18.57%','Viewer FPS','actual V3 application'):
 assert phrase in text,phrase
assert text.count('```mermaid')==1
print('Metropolitan documentation PASS')
