"""Ten sectionally distinct stream edge families."""
EDGE_FAMILIES=('formal-stone','stepped-seating','green-planted','low-retaining','plaza-terrace','transit-frontage','service-maintenance','bridge-abutment','pocket-wetland','pavilion-edge')

def build_edges(batch,segments):
 for index,s in enumerate(segments):
  x=(s['start'][0]+s['end'][0])/2;y=(s['start'][1]+s['end'][1])/2;length=s['lengthM'];corr=s['corridorWidthM'];water=s['waterWidthM'];kind=EDGE_FAMILIES[index%len(EDGE_FAMILIES)]
  # Bed, shallow surface and two pedestrian banks are separate physical layers.
  batch.add_box('water-bed','water-bed',(x,y,-.32),(length,water+2,.18))
  batch.add_box('water-surface','shallow-water',(x,y,-.08),(length,water,.06))
  bank=(corr-water)/4
  batch.add_box(f'{kind}-walk','paving',(x,y-water/2-bank/2,.08),(length,bank,.16));batch.add_box(f'{kind}-walk','paving',(x,y+water/2+bank/2,.08),(length,bank,.16))
  if kind in ('stepped-seating','plaza-terrace'):
   for step in range(3):
    off=water/2+.7+step*1.1;batch.add_box(f'{kind}-step','warm-stone',(x,y-off,.18+step*.18),(length,1,.22));batch.add_box(f'{kind}-step','warm-stone',(x,y+off,.18+step*.18),(length,1,.22))
  elif kind in ('green-planted','pocket-wetland'):
   for n in range(-4,5):batch.add_box(f'{kind}-planter','soil',(x+n*length/10,y-water/2-2.2,.32),(length/13,1.5,.5));batch.add_box(f'{kind}-planter','soil',(x+n*length/10,y+water/2+2.2,.32),(length/13,1.5,.5))
  elif kind=='service-maintenance':
   batch.add_box('maintenance-route','dark-granite',(x,y+water/2+3,.12),(length,3,.24))
  else:
   batch.add_box(f'{kind}-edge','warm-stone',(x,y-water/2-.35,.42),(length,.7,.84));batch.add_box(f'{kind}-edge','warm-stone',(x,y+water/2+.35,.42),(length,.7,.84))
 return {'families':list(EDGE_FAMILIES),'count':len(EDGE_FAMILIES),'waterContinuity':True,'bedContinuity':True}
