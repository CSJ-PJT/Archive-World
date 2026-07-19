"""Deterministic city-support family catalog; no meshes or canonical mutation."""
from hashlib import sha256

GROUPS = {
 "residential": ["premium-highrise","slab-tower","point-tower","courtyard-tower","midrise-perimeter","neighborhood-retail","community-center","school","senior-community","gate-security"],
 "office": ["metropolitan-landmark","medium-office","compact-office","corner-office","podium-office","operations-annex","civic-tech-office","mixed-use-office","corporate-campus","service-building"],
 "commercial": ["retail-podium","shopping-street","entertainment-block","hotel","mixed-use-tower","market-hall","restaurant-street","neighborhood-commercial"],
 "industrial": ["warehouse","logistics-hub","distribution-center","light-industrial","utility-building","freight-office","service-yard"],
 "civic": ["city-hall","library","cultural-center","museum-gallery","transit-hall","medical-public-service","public-safety"],
}

def _status(category, name):
 if (category,name)==("office","metropolitan-landmark"): return "PO_REVIEW_CANDIDATE_FROZEN"
 if (category,name)==("residential","premium-highrise"): return "PO_REVIEW_CANDIDATE_FROZEN"
 return "CITY_SUPPORT_PROTOTYPE"

def family_catalog(seed=7302026):
 out=[]
 for category,names in GROUPS.items():
  for index,name in enumerate(names):
   family_id=f"metro-{category}-{name}"
   digest=int(sha256(f"{seed}:{family_id}".encode()).hexdigest()[:8],16)
   score=82 if _status(category,name).startswith("PO_") else 65+digest%11
   height={"residential":(18,42),"office":(8,50),"commercial":(2,28),"industrial":(1,8),"civic":(2,16)}[category]
   out.append({"id":family_id,"category":category,"status":_status(category,name),"qualityScore":score,
    "frozen":score==82,"canonical":False,"cityApplied":False,"seed":digest,"heightFloors":[height[0],height[1]],
    "facades":{"front":True,"side":True,"rear":True,"roof":True,"patternFamilies":3+digest%5,"repetitionLimit":.24},
    "orientation":{"entrance":"active-frontage","service":"rear-or-lane","roofSilhouette":"district-tier"},
    "lod":{"lod0":"near","lod1":"mid","lod2":"far"},"groundContactRequired":True,
    "districtCompatibility":[category,"market" if category=="commercial" else category],
    "provenance":{"kind":"grammar-generated-contract","referenceMeshCopied":False,"generator":"metropolitan-support-family-v1"}})
 return out

