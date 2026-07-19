def pavilion(batch,prefix,x,y,w,d,accent='steel'):
 batch.add_box(f'{prefix}-floor','warm-stone',(x,y,.12),(w,d,.24));batch.add_box(f'{prefix}-roof',accent,(x,y,4.4),(w,d,.42))
 for sx in (-1,1):
  for sy in (-1,1):batch.add_box(f'{prefix}-column',accent,(x+sx*(w/2-.6),y+sy*(d/2-.6),2.25),(.35,.35,4.5))
 batch.add_box(f'{prefix}-glazing','glass',(x,y-d/2+.15,2.2),(w-1,.3,3.8));batch.add_box(f'{prefix}-blank-signage','pale-stone',(x,y-d/2-.15,3),(w*.28,.18,1.1))

def build_nodes(batch,nodes):
 for node in nodes:
  x,y=node['position'];nid=node['id']
  if nid=='archive-water-plaza':
   batch.add_box('archive-plaza','pale-stone',(x,y-18,.12),(82,26,.24));pavilion(batch,'archive-pavilion',x-18,y-18,20,10);batch.add_box('archive-information-wall','dark-granite',(x+22,y-20,2.1),(13,.6,4.2))
   for i in range(-4,5):batch.add_box('archive-light-line','light-warm',(x+i*7,y-30,.18),(4,.16,.18))
  elif nid=='ledger-stream-terrace':
   batch.add_box('ledger-terrace','warm-stone',(x,y+17,.18),(76,22,.36));pavilion(batch,'ledger-cafe',x+16,y+17,18,9,'dark-granite')
   for i in range(-3,4):batch.add_box('ledger-seat','wood',(x+i*8,y+20,.62),(4,1.3,.7))
  elif nid=='transit-stream-junction':
   batch.add_box('transit-plaza','paving',(x,y-18,.14),(72,25,.28));pavilion(batch,'station-entry',x,y-18,24,12)
   batch.add_wedge('accessible-ramp','warm-stone',(x+22,y-18,.65),(18,5,1.3));batch.add_box('transit-canopy','steel',(x+22,y-18,3.1),(20,7,.34))
  else:
   batch.add_box('pocket-node','paving',(x,y,.1),(24,16,.2));batch.add_box('pocket-seat','wood',(x,y-4,.55),(8,1.4,.7));batch.add_box('public-art-pedestal','dark-granite',(x+5,y+2,.8),(2.4,2.4,1.6))
 return {'majorNodes':3,'pocketNodes':sum(n['role']=='POCKET' for n in nodes),'microArchitecture':['archive-pavilion','ledger-cafe','station-entry','pocket-seat','information-wall'],'activeFrontageProxy':{'archiveWaterPlaza':.78,'ledgerTerrace':.72,'transitJunction':.73,'generalStream':.58}}
