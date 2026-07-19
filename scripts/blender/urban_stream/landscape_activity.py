import math,random
def tree(batch,x,y,seed):
 r=random.Random(seed);h=5+r.random()*5;batch.add_cylinder('stream-tree-trunk','wood',(x,y,h*.32),.28+r.random()*.15,h*.64,8)
 for j in range(3+(seed%3)):
  angle=j*2*math.pi/(3+seed%3);batch.add_cylinder('stream-tree-crown','foliage' if seed%2 else 'foliage-light',(x+math.cos(angle)*1.2,y+math.sin(angle)*1.2,h*.78+j*.12),1.5+r.random()*.8,2.4+r.random(),10)
def build_landscape_activity(batch,segments,nodes):
 seed=1001;trees=humans=lights=benches=0
 for s in segments:
  x0,y0=s['start'];x1,y1=s['end']
  for j in range(10):
   t=(j+.5)/10;x=x0+(x1-x0)*t;y=y0+(y1-y0)*t
   for side in (-1,1):
    tree(batch,x,y+side*(s['waterWidthM']/2+6),seed);seed+=1;trees+=1
    if j%2==0:batch.add_box('stream-bench','wood',(x+2,y+side*(s['waterWidthM']/2+4),.55),(3.2,1,.7));benches+=1
    batch.add_cylinder('pedestrian-light','service-metal',(x-2,y+side*(s['waterWidthM']/2+5),1.8),.11,3.6,8);batch.add_box('pedestrian-luminaire','light-warm',(x-2,y+side*(s['waterWidthM']/2+5),3.7),(.4,.4,.22));lights+=1
  for j in range(8):
   t=(j+1)/9;x=x0+(x1-x0)*t;y=y0+(y1-y0)*t+(3 if j%2 else -3);batch.add_cylinder('human-proxy','dark-granite',(x,y,.85),.18,1.7,8);humans+=1
 for node in nodes:
  x,y=node['position'];batch.add_box('node-planter','warm-stone',(x-8,y+7,.5),(8,3,1));batch.add_box('node-planter','soil',(x-8,y+7,1.05),(7.2,2.2,.25))
 return {'treeCount':trees,'humanCount':humans,'pedestrianLights':lights,'benchCount':benches,'floatingObjects':0,'waterIntrusion':0,'activityPresets':['morning','day','evening','night']}
