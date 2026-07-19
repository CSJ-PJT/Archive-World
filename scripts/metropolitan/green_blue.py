"""Connected Metropolitan green/blue planning network."""
def build_green_blue():
 river={"id":"archive-river","polygon":[[-3000,-760],[3000,-760],[3000,-440],[-3000,-440]],"areaM2":1920000,"continuity":True}
 promenade={"id":"riverfront-promenade","centerline":[[-3000,-390],[-1500,-390],[0,-390],[1500,-390],[3000,-390]],"continuous":True,"widthM":24}
 central={"id":"metropolitan-central-park","bounds":[-3000,-400,-1600,900],"areaM2":1820000,"type":"central-park"}
 neighborhoods=[]
 for i in range(12):
  x=-2700+(i%6)*950;y=1150+(i//6)*850;neighborhoods.append({"id":f"neighborhood-park-{i+1}","center":[x,y],"areaM2":42000+(i%3)*9000,"serviceRadiusM":550})
 pockets=[]
 for i in range(30): pockets.append({"id":f"pocket-park-{i+1}","center":[-2800+(i%10)*600,-2100+(i//10)*1200],"areaM2":4800+(i%5)*700})
 corridors=[{"id":f"green-corridor-{i+1}","centerline":[[-2500+i*1400,-2300],[-2100+i*1200,2300]],"widthM":55,"continuous":True} for i in range(4)]
 modules=[{"id":f"green-module-{i+1}","kind":("tree-grove","retaining-edge","slope","groundcover","plaza-green")[i%5],"status":"CITY_SUPPORT_PROTOTYPE"} for i in range(128)]
 areas=river['areaM2']+central['areaM2']+sum(x['areaM2'] for x in neighborhoods+pockets)+sum(55*4700 for _ in corridors)
 return {"river":river,"riverfrontPromenade":promenade,"centralPark":central,"neighborhoodParks":neighborhoods,"pocketParks":pockets,
  "greenCorridors":corridors,"logisticsResidentialBuffer":{"widthM":180,"continuous":True},"wetlandPlaceholder":{"areaM2":96000},
  "urbanForestEdge":{"lengthM":4600},"modules":modules,"connectedComponents":1,"totalGreenBlueAreaM2":areas,
  "greenOpenSpaceRatioProxy":round(areas/(6000*5000),4),"status":"GENERATED_PLAN_ONLY"}
