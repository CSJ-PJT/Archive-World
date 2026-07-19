"""Deterministic district/block/building placement for the Generated pilot."""
from .district_dna import district_records
from .block_generator import variants
from .support_families import family_catalog

DNA_CATEGORY={"archiveos":"office","ledger":"office","nexus":"office","market":"commercial","residential":"residential","civic":"civic","infrastructure":"industrial","logistics":"industrial"}

def assemble_city(seed=7302026):
 districts=district_records(); blocks=variants(seed); families=family_catalog(seed)
 by_category={}
 for family in families: by_category.setdefault(family['category'],[]).append(family)
 placed_blocks=[]; instances=[]
 for d_index,district in enumerate(districts):
  x0,y0= district['polygon'][0]; x1,y1=district['polygon'][2]
  cols=max(3,int((x1-x0)//260)); rows=max(2,int((y1-y0)//220))
  category=DNA_CATEGORY[district['dnaId']]
  compatible=[b for b in blocks if b['districtCompatibility'][0]==category]
  if not compatible: compatible=[b for b in blocks if b['districtCompatibility'][0]=='industrial']
  family_pool=by_category[category]
  for row in range(rows):
   for col in range(cols):
    block=compatible[(d_index*7+row*cols+col)%len(compatible)]
    block_instance=f"{district['id']}-b{row:02d}{col:02d}"
    cx=x0+(col+.5)*(x1-x0)/cols; cy=y0+(row+.5)*(y1-y0)/rows
    placed_blocks.append({"id":block_instance,"variantId":block['id'],"districtId":district['id'],"center":[round(cx,2),round(cy,2)],"status":"GENERATED_PLAN_ONLY"})
    slot_count=max(6,min(10,block['buildingSlots']+4))
    for slot in range(slot_count):
     family=family_pool[(row*3+col*5+slot)%len(family_pool)]
     # Frozen PO candidates remain sparse anchors, never mass-filling fabric.
     if family['frozen'] and (len(instances)+slot)%17:
      family=family_pool[(row+col+slot+1)%len(family_pool)]
     dx=((slot%4)-1.5)*34; dy=((slot//4)-1.5)*30
     instances.append({"id":f"{block_instance}-i{slot:02d}","familyId":family['id'],"blockId":block_instance,"districtId":district['id'],
      "position":[round(cx+dx,2),round(cy+dy,2),0],"rotationZ":(slot%4)*90,"scale":round(.94+(slot%5)*.025,3),
      "lodPolicy":family['lod'],"status":family['status'],"entranceSide":"frontage","serviceSide":"rear","canonical":False,"v3Applied":False})
 return {"seed":seed,"districts":districts,"blocks":placed_blocks,"families":families,"instances":instances,
  "status":"GENERATED_METROPOLITAN_PILOT","canonical":False,"v3Applied":False}
