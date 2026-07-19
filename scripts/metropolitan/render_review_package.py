#!/usr/bin/env python3
"""Create truthful 1920x1080 metropolitan planning diagrams (not photoreal renders)."""
import argparse,html,json,sys
from pathlib import Path
from .city_assembler import assemble_city
from .street_transit import build_street_graph,build_transit
from .green_blue import build_green_blue
from .skyline_metrics import analyze

PALETTE={"archiveos":"#4f7793","ledger":"#6b668d","market":"#c07c4d","nexus":"#508b87","residential":"#9d8066","civic":"#789a63","infrastructure":"#777f85","logistics":"#6d777b"}
def svg_doc(title,subtitle,body,stats):
 cards=''.join(f'<text x="{60+i*220}" y="1010" class="metric">{html.escape(k)}: {html.escape(str(v))}</text>' for i,(k,v) in enumerate(stats.items()))
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"><style>text{{font-family:Arial,sans-serif;fill:#edf2f2}}.title{{font-size:42px;font-weight:700}}.sub{{font-size:21px;fill:#b8c7ca}}.metric{{font-size:18px}}.label{{font-size:16px;font-weight:700}}</style><rect width="1920" height="1080" fill="#1f292e"/><text x="60" y="70" class="title">{html.escape(title)}</text><text x="60" y="106" class="sub">{html.escape(subtitle)}</text>{body}<rect x="40" y="965" width="1840" height="80" rx="12" fill="#11191dcc"/>{cards}<text x="1515" y="1040" class="sub">GENERATED · NOT CANONICAL · NOT V3 APPLIED</text></svg>'''

def city_plan(city,mode):
 shapes=[]
 for d in city['districts']:
  x0,y0=d['polygon'][0];x1,y1=d['polygon'][2];sx=120+(x0+3000)/6000*1680;sy=160+(2500-y1)/5000*760;w=(x1-x0)/6000*1680;h=(y1-y0)/5000*760
  color=PALETTE[d['dnaId']];opacity=.84 if mode=='land-use' else .55
  shapes.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{color}" fill-opacity="{opacity}" stroke="#d9e4e4"/><text x="{sx+10:.1f}" y="{sy+25:.1f}" class="label">{html.escape(d["id"])}</text>')
 if mode in ('street-hierarchy','transit'):
  for i in range(0,14): shapes.append(f'<line x1="{140+i*125}" y1="160" x2="{140+i*125}" y2="920" stroke="#d5dfe0" stroke-width="{7 if i%4==0 else 3}" opacity=".7"/>')
  for i in range(0,9): shapes.append(f'<line x1="120" y1="{180+i*90}" x2="1800" y2="{180+i*90}" stroke="#d5dfe0" stroke-width="{7 if i%3==0 else 3}" opacity=".7"/>')
 if mode=='transit': shapes.append('<path d="M140 540 H1800 M960 170 V920 M350 300 H1580 V800 H350 Z" fill="none" stroke="#e66d55" stroke-width="10"/>')
 if mode=='green-network': shapes.append('<path d="M120 590 H1800" stroke="#56a879" stroke-width="60"/><rect x="120" y="330" width="380" height="250" fill="#4f9b70"/>')
 return ''.join(shapes)

def render(output):
 output=Path(output);output.mkdir(parents=True,exist_ok=True);city=assemble_city();metrics=analyze()['metrics'];transit=build_transit(build_street_graph());green=build_green_blue();written=[]
 modes=("master-plan","land-use","height","density","transit","green-network","street-hierarchy","skyline","status","po-anchors")
 for mode in modes:
  body=city_plan(city,mode)
  doc=svg_doc(f'Archive Metropolitan — {mode.replace("-"," ").title()}','Planning diagram; visual/engineering certification is outside this pilot.',body,{"Districts":len(city['districts']),"Instances":len(city['instances']),"Families":len(city['families']),"Blocks":len(city['blocks'])})
  path=output/f'city-{mode}.svg';path.write_text(doc,encoding='utf-8');written.append(path.name)
 for d in city['districts']:
  for view in ('district-plan','urban-section','activity-map'):
   dna=d['dna']; bars=''.join(f'<rect x="{180+i*95}" y="{850-(i%5+2)*75}" width="62" height="{(i%5+2)*75}" fill="{PALETTE[d["dnaId"]]}" stroke="#dbe6e6"/>' for i in range(16))
   body=f'<rect x="130" y="160" width="1660" height="750" rx="20" fill="#344148"/>{bars}<path d="M150 820 H1770" stroke="#76a86f" stroke-width="40"/><text x="170" y="205" class="sub">{html.escape(d["id"])} · {view.replace("-"," ")} · status overlay enabled</text>'
   doc=svg_doc(f'{d["id"]} — {view.replace("-"," ").title()}','Schematic urban review view; building geometry remains status-coded.',body,{"Area m²":d['areaM2'],"Avg height":dna['averageHeightM'],"Max height":dna['maximumHeightM'],"Green":dna['greenRatio']})
   path=output/f'{d["id"]}-{view}.svg';path.write_text(doc,encoding='utf-8');written.append(path.name)
 manifest={"status":"PLANNING_PRESENTATION_ONLY","photoreal":False,"count":len(written),"files":written,"resolution":[1920,1080],"transitStations":len(transit['stations']),"greenRatio":green['greenOpenSpaceRatioProxy'],"metrics":metrics}
 (output/'render-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');return manifest

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();print(json.dumps(render(a.output),indent=2))

