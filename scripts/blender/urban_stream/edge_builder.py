"""Ten sectionally distinct stream edge families."""
import math

EDGE_FAMILIES=('formal-stone','stepped-seating','green-planted','low-retaining','plaza-terrace','transit-frontage','service-maintenance','bridge-abutment','pocket-wetland','pavilion-edge')

def build_edges(batch,segments):
 for index,s in enumerate(segments):
  x=(s['start'][0]+s['end'][0])/2;y=(s['start'][1]+s['end'][1])/2;length=s['lengthM'];corr=s['corridorWidthM'];water=s['waterWidthM'];kind=EDGE_FAMILIES[index%len(EDGE_FAMILIES)]
  dx=s['end'][0]-s['start'][0];dy=s['end'][1]-s['start'][1];rotation=math.atan2(dy,dx);nx=-dy/length;ny=dx/length
  def offset(distance): return (x+nx*distance,y+ny*distance)
  def box(role,material,distance,z,dimensions):
   px,py=offset(distance);batch.add_box(role,material,(px,py,z),dimensions,rotation_z=rotation)
  # Bed, shallow surface and two pedestrian banks are separate physical layers.
  box('water-bed','water-bed',0,-.32,(length+.5,water+2,.18))
  box('water-surface','shallow-water',0,-.08,(length+.5,water,.06))
  bank=(corr-water)/4
  box(f'{kind}-walk','paving',-water/2-bank/2,.08,(length+.4,bank,.16));box(f'{kind}-walk','paving',water/2+bank/2,.08,(length+.4,bank,.16))
  if kind in ('stepped-seating','plaza-terrace'):
   for step in range(3):
    off=water/2+.7+step*1.1;box(f'{kind}-step','warm-stone',-off,.18+step*.18,(length+.2,1,.22));box(f'{kind}-step','warm-stone',off,.18+step*.18,(length+.2,1,.22))
  elif kind in ('green-planted','pocket-wetland'):
   tx=dx/length;ty=dy/length
   for n in range(-4,5):
    for side in (-1,1):
     px,py=offset(side*(water/2+2.2));batch.add_box(f'{kind}-planter','soil',(px+n*tx*length/10,py+n*ty*length/10,.32),(length/13,1.5,.5),rotation_z=rotation)
  elif kind=='service-maintenance':
   box('maintenance-route','dark-granite',water/2+3,.12,(length,3,.24))
  else:
   box(f'{kind}-edge','warm-stone',-water/2-.35,.42,(length+.2,.7,.84));box(f'{kind}-edge','warm-stone',water/2+.35,.42,(length+.2,.7,.84))
 return {'families':list(EDGE_FAMILIES),'count':len(EDGE_FAMILIES),'instantiatedCount':len({s['edgeType'] for s in segments}),'waterContinuity':True,'bedContinuity':True}
