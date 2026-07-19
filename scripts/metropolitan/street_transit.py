"""Deterministic metropolitan street, pedestrian, service and transit graphs."""
from collections import deque

STREET_TYPES=("metropolitan-arterial","district-arterial","collector","local-street","residential-street","commercial-high-street","office-boulevard","service-street","logistics-freight-road","pedestrian-street","riverfront-promenade","park-edge-road")

def build_street_graph(cols=26,rows=22,spacing_x=240,spacing_y=230):
 nodes=[]; edges=[]
 for y in range(rows):
  for x in range(cols): nodes.append({"id":f"n-{x}-{y}","position":[-3000+x*spacing_x,-2500+y*spacing_y],"intersection":True})
 def add(a,b,axis,index):
  kind="metropolitan-arterial" if index%8==0 else "district-arterial" if index%5==0 else "collector" if index%3==0 else "local-street"
  modes=["vehicle","pedestrian","service","fire"]; width=38 if 'arterial' in kind else 26 if kind=='collector' else 18
  edges.append({"id":f"e-{a}-{b}","from":a,"to":b,"bidirectional":True,"axis":axis,"streetType":kind,"lanes":6 if width>=38 else 4 if width>=26 else 2,
   "widthM":width,"speedClass":"metropolitan" if width>=38 else "district" if width>=26 else "local","modes":modes,"sidewalkM":6 if width>=38 else 4,
   "cycleLane":width>=26,"transit":width>=26,"serviceAccess":True,"crosswalk":True,"status":"CITY_SUPPORT_PROTOTYPE"})
 for y in range(rows):
  for x in range(cols-1): add(f"n-{x}-{y}",f"n-{x+1}-{y}","east-west",y)
 for x in range(cols):
  for y in range(rows-1): add(f"n-{x}-{y}",f"n-{x}-{y+1}","north-south",x)
 return {"streetTypes":list(STREET_TYPES),"nodes":nodes,"edges":edges,"graphComponents":{"vehicle":1,"pedestrian":1,"service":1,"fire":1},"status":"GENERATED_PLAN_ONLY"}

def build_transit(graph):
 def node(x,y): return f"n-{x}-{y}"
 lines=[
  {"id":"metro-a","type":"metro","stations":[node(x,10) for x in (1,4,7,10,13,16,19,22,25)]},
  {"id":"metro-b","type":"metro","stations":[node(13,y) for y in (1,4,7,10,13,16,19,21)]},
  {"id":"metro-ring","type":"semi-ring","stations":[node(x,y) for x,y in ((4,4),(10,4),(16,4),(22,4),(22,10),(22,16),(16,19),(10,19),(4,16),(4,10))]},
 ]
 unique=sorted({s for line in lines for s in line['stations']}); station_nodes=set(unique)
 transfers=sorted(s for s in unique if sum(s in line['stations'] for line in lines)>1)
 # Trunk and feeder buses use deterministic graph nodes and do not claim runtime simulation.
 bus=[]
 for route in range(18):
  y=(route*3+2)%22; stops=[node(x,y) for x in range(route%3,26,5)]; bus.append({"id":f"bus-{'trunk' if route<6 else 'feeder'}-{route+1}","class":"trunk" if route<6 else "feeder","stops":stops})
 bus_stops=sorted({s for route in bus for s in route['stops']})
 return {"railLines":lines,"stations":[{"id":s,"transfer":s in transfers,"accessible":True} for s in unique],"transferStations":transfers,
  "busRoutes":bus,"busStops":bus_stops,"bikeCorridors":["riverfront","metropolitan-park","residential-north","nexus-technology","civic-cultural"],
  "taxiDropoffNodes":[node(x,y) for x,y in ((11,9),(15,9),(8,10),(17,5),(13,16),(20,10))],"simulationRuntimeIntegration":False,"status":"GENERATED_PLAN_ONLY"}

def connected(graph,mode):
 adj={n['id']:[] for n in graph['nodes']}
 for e in graph['edges']:
  if mode in e['modes']: adj[e['from']].append(e['to']);adj[e['to']].append(e['from'])
 start=next(iter(adj));seen={start};q=deque([start])
 while q:
  for nxt in adj[q.popleft()]:
   if nxt not in seen: seen.add(nxt);q.append(nxt)
 return len(seen)==len(adj)
