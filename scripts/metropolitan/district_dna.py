"""Spatial District DNA application for the Generated Metropolitan Pilot."""
DISTRICTS=(
 ("logistics-edge","logistics",(-3000,-2500,-1400,-800),.28,24,52,36,.12,.08,.18,"tier-5"),
 ("nexus-technology","nexus",(-1400,-2500,300,-800),.40,42,130,30,.24,.22,.34,"tier-3"),
 ("market-commercial","market",(300,-2500,1600,-800),.58,38,145,24,.46,.14,.40,"tier-2-3"),
 ("residential-south","residential",(1600,-2500,3000,-800),.34,58,118,22,.25,.30,.58,"tier-3"),
 ("riverfront","infrastructure",(-3000,-800,3000,-400),.08,12,28,18,.32,.62,.78,"open-corridor"),
 ("metropolitan-park","civic",(-3000,-400,-1600,900),.10,16,34,18,.18,.72,.86,"open-corridor"),
 ("civic-cultural","civic",(-1600,-400,-400,900),.30,30,72,24,.38,.38,.72,"tier-4"),
 ("archiveos-core","archiveos",(-400,-400,800,900),.64,78,220,38,.55,.24,.82,"tier-1"),
 ("ledger-financial","ledger",(800,-400,2000,900),.66,74,205,36,.58,.20,.78,"tier-1-2"),
 ("infrastructure-belt","infrastructure",(2000,-400,3000,900),.24,22,58,30,.10,.18,.20,"tier-5"),
 ("residential-north","residential",(-3000,900,-600,2500),.36,62,132,22,.28,.34,.62,"tier-3"),
 ("transit-oriented-north","market",(-600,900,800,2500),.52,46,158,28,.48,.22,.76,"tier-2-3"),
 ("urban-expansion-east","residential",(800,900,3000,2500),.24,36,96,24,.20,.38,.44,"tier-3-4"),
)

def polygon(bounds):
 x0,y0,x1,y1=bounds; return [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]

def district_records():
 out=[]
 for identifier,kind,bounds,coverage,avg_h,max_h,street,frontage,green,ped,skyline in DISTRICTS:
  x0,y0,x1,y1=bounds
  out.append({"id":identifier,"dnaId":kind,"polygon":polygon(bounds),"areaM2":(x1-x0)*(y1-y0),
   "dna":{"landUse":kind,"targetDensity":"high" if coverage>=.5 else "medium" if coverage>=.3 else "low",
   "farProxy":round(coverage*avg_h/3.4,2),"buildingCoverage":coverage,"averageHeightM":avg_h,"maximumHeightM":max_h,
   "blockSizeM":[160 if kind in ('archiveos','ledger','market') else 220,130 if kind!='logistics' else 240],
   "parcelSizeM":[48,42],"streetWidthM":street,"sidewalkWidthM":max(3,street*.18),"activeFrontageRatio":frontage,
   "greenRatio":green,"publicRealmRatio":round((green+frontage)*.35,3),"serviceAccess":True,
   "transitAccessibility":ped,"skylineRole":skyline,"dayActivity":.85,"nightActivity":.86 if kind=='market' else .62,
   "noiseTolerance":.85 if kind in ('logistics','infrastructure') else .35,"vehicleDependence":.88 if kind=='logistics' else .42,
   "pedestrianPriority":ped},"status":"GENERATED_PLAN_ONLY"})
 return out
