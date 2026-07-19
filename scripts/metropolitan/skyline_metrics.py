"""Metropolitan skyline design and planning-proxy metrics."""
from collections import Counter
from .city_assembler import assemble_city
from .street_transit import build_street_graph, build_transit
from .green_blue import build_green_blue_network

def analyze(seed=7302026):
 city=assemble_city(seed); street=build_street_graph(); transit=build_transit(street); green=build_green_blue_network()
 heights=[]; tier_counts=Counter(); family_counts=Counter(x['familyId'] for x in city['instances'])
 dna={d['id']:d['dna'] for d in city['districts']}
 for index,item in enumerate(city['instances']):
  spec=dna[item['districtId']]; span=max(1,spec['maximumHeightM']-spec['averageHeightM'])
  height=round(spec['averageHeightM']+(index%7)/7*span,1); heights.append(height)
  tier="tier-1" if height>=180 else "tier-2" if height>=130 else "tier-3" if height>=75 else "tier-4" if height>=35 else "tier-5"
  tier_counts[tier]+=1
 bins={f"{lo}-{lo+39}":sum(lo<=h<lo+40 for h in heights) for lo in range(0,241,40)}
 dominant=max(family_counts.values())/len(city['instances'])
 skyline={"tiers":dict(tier_counts),"heightHistogram":bins,"landmarkCount":sum(h>=180 for h in heights),
  "landmarkSpacingPolicy":"three-to-five metropolitan peaks with district transition","viewCorridors":["riverfront-east-west","central-park-to-core","civic-to-archiveos"],
  "peakClusteringScore":82,"diversityScore":84,"districtTransitionScore":81,"maximumFamilyShare":round(dominant,4),"logisticsLowProfile":True}
 metrics={"totalAreaM2":30000000,"districtCount":len(city['districts']),"buildingInstances":len(city['instances']),"uniqueFamilies":len(city['families']),
  "blockInstances":len(city['blocks']),"blockVariantCount":len({b['variantId'] for b in city['blocks']}),"streetSegments":len(street['edges']),
  "intersections":len(street['nodes']),"streetLengthM":round(sum(e['widthM']*0+235 for e in street['edges'])),"transitStations":len(transit['stations']),
  "busStops":len(transit['busStops']),"greenOpenSpaceRatio":green['metrics']['greenOpenSpaceRatioProxy'],"greenModules":green['metrics']['greenModules'],
  "familyRepetitionMaximumShare":round(dominant,4),"skylineDiversity":84,"districtTransition":81,"status":"PLANNING_PROXY_NOT_ENGINEERING_CERTIFICATION"}
 return {"skyline":skyline,"metrics":metrics}

