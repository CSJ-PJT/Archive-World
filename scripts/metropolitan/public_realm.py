"""Rule-based public-realm and static population proxies."""
from .city_assembler import assemble_city

REALM_KINDS=("bench","planter","streetlight","pedestrian-light","bollard","tree-pit","bus-stop","bicycle-rack","waste-recycling","kiosk-placeholder","outdoor-seating","public-art-pedestal","water-feature","playground","sports-court-proxy","plaza-furniture","wayfinding-blank","taxi-dropoff","crosswalk","tactile-paving")
VEHICLES=("sedan","suv","taxi","city-bus","shuttle","delivery-van","logistics-truck","service-vehicle","emergency-proxy","bicycle")
HUMANS=("walking","standing","sitting","cycling","waiting","office","resident","student","retail-visitor","logistics-worker")

def build_public_realm(seed=7302026):
 city=assemble_city(seed); nodes=[]
 for i,block in enumerate(city['blocks']):
  # Three intentional, frontage-related nodes per block; no random scatter.
  for lane in range(3):
   nodes.append({"id":f"realm-{i:04d}-{lane}","kind":REALM_KINDS[(i*3+lane)%len(REALM_KINDS)],"blockId":block['id'],
    "districtId":block['districtId'],"relationship":["entrance","pedestrian-path","transit-or-plaza"][lane],"status":"INFRASTRUCTURE_PROXY"})
 vehicles=[]; humans=[]
 for i,block in enumerate(city['blocks']):
  if i%2==0: vehicles.append({"id":f"vehicle-{i:04d}","kind":VEHICLES[i%len(VEHICLES)],"blockId":block['id'],"timePreset":"daytime","status":"PLACEHOLDER"})
  for j in range(2): humans.append({"id":f"human-{i:04d}-{j}","kind":HUMANS[(i+j)%len(HUMANS)],"blockId":block['id'],"timePreset":("morning-commute","daytime","evening-peak","night")[(i+j)%4],"status":"PLACEHOLDER"})
 return {"publicRealm":nodes,"vehicles":vehicles,"humans":humans,"simulationRuntimeIntegration":False,"placementPolicy":"relationship-driven"}

