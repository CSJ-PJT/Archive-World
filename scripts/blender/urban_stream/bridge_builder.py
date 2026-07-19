BRIDGE_TYPES=('slim-steel','stone-plaza','green-corridor','transit-connector','archive-gateway','service-crossing','street-crossing')
def build_bridges(batch,bridges):
 for i,b in enumerate(bridges):
  x,y=b['position'];kind=b['type'];width=(4,8,6,7,9,8,12)[i%7];deck=.28 if i<5 else .45
  batch.add_box(f'{kind}-deck','steel' if i in (0,2,3) else 'warm-stone',(x,y,1.25),(width,28,deck))
  for side in (-1,1):
   batch.add_box(f'{kind}-railing','railing',(x+side*(width/2-.12),y,2.0),(.18,28,1.35))
   batch.add_box(f'{kind}-abutment','dark-granite',(x+side*(width/2+1.1),y,0.7),(2,6,1.4))
  if kind=='archive-gateway':
   for side in (-1,1):batch.add_box('archive-gateway-frame','steel',(x+side*width/2,y,4.2),(.5,1,6));batch.add_box('archive-gateway-beam','steel',(x,y,7.2),(width+.5,1,.45))
  if kind=='green-corridor':
   for side in (-1,1):batch.add_box('bridge-planter','soil',(x+side*(width/2-.6),y,.65),(.8,18,.7))
  for j in range(-2,3):batch.add_box('bridge-step-light','light-warm',(x-width/2+.1,y+j*5,1.55),(.12,.24,.16))
 return {'bridgeCount':len(bridges),'types':list(BRIDGE_TYPES),'pedestrian':5,'service':1,'vehicle':1,'orphanBridges':0}
