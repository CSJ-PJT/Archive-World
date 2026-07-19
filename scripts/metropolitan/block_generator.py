"""Rule-based metropolitan block variants (planning metadata only)."""
from hashlib import sha256

BLOCK_TYPES={
 "residential":["superblock-courtyard","tower-in-park","perimeter-housing","mixed-residential-retail","school-community","neighborhood-center"],
 "office":["cbd-podium-tower","twin-landmark","office-courtyard","corporate-campus","mixed-office-retail"],
 "commercial":["shopping-street","mall-block","entertainment-block","hotel-retail"],
 "civic":["civic-plaza","cultural-campus","transit-civic-node"],
 "industrial":["logistics-compound","warehouse-cluster","utility-service-block"],
}

def variants(seed=7302026):
 rows=[]
 for district,types in BLOCK_TYPES.items():
  for block_type in types:
   for variant in range(4):
    block_id=f"block-{district}-{block_type}-v{variant+1}"
    token=int(sha256(f"{seed}:{block_id}".encode()).hexdigest()[:8],16)
    width=150+(token%6)*20; depth=110+((token//7)%6)*20
    parcels=3+token%7
    rows.append({"id":block_id,"type":block_type,"districtCompatibility":[district],"status":"GENERATED_PLAN_ONLY",
     "boundsM":[width,depth],"parcelCount":parcels,"buildingSlots":max(2,parcels-1),
     "network":{"pedestrian":"connected-loop","vehicle":"connected","fireService":"connected-rear","publicFreightIntrusion":False},
     "frontage":{"activeRatio":round(.25+(token%40)/100,2),"entranceAnchors":["primary","secondary"],"serviceSide":"rear"},
     "density":{"coverage":round(.24+(token%35)/100,2),"farProxy":round(1.2+(token%60)/10,1),"openSpaceRatio":round(.22+(token%30)/100,2)},
     "publicRealm":["sidewalk","tree-pits","seating","crosswalk"],"heightDistribution":"tiered-not-random",
     "adjacency":{"forbidSameVariant":True,"serviceLaneRequired":district in ('office','commercial','industrial')},
     "seed":token,"provenance":{"generator":"metropolitan-block-v1","randomScatter":False}})
 return rows

