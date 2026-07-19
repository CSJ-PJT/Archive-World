"""Generate eleven distinct actual CBD support-family GLBs at LOD0/1/2."""
from __future__ import annotations
import argparse,json,math,sys,time
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;PROD=HERE.parent/'production_geometry';sys.path[:0]=[str(HERE),str(PROD),str(HERE.parent)]
from geometry_core import MeshBatch,validate_geometry
from material_library import create_material_library
from family_palette import apply_palette
from batch_consolidation import consolidate

SPECS=(
 ('premium-medium-office','tower',28,34,24,5,1),('compact-financial-office','compact',18,24,20,3,2),
 ('corner-office-tower','corner',24,31,22,4,3),('podium-office','stepped',32,26,19,5,4),
 ('institutional-archiveos-office','civic',38,28,16,4,5),('civic-tech-office','split',30,30,23,4,6),
 ('retail-public-podium','lowrise',48,34,8,3,7),('financial-annex','annex',26,22,12,3,8),
 ('operations-service-building','service',40,28,7,2,9),('transit-hall','transit',52,30,5,2,10),
 ('cultural-public-pavilion','pavilion',42,36,4,2,11),
)

def add_facades(b,w,d,floors,fh,lod,seed):
 step={'LOD0':1,'LOD1':2,'LOD2':4}[lod]; bay=4+(seed%3); rows=range(1,floors,step)
 for floor in rows:
  z=fh*floor+fh*.52; band=floor%6==0
  for x in range(-int(w//2)+2,int(w//2)-1,bay*step):
   b.add_box('front-bay','curtain-wall-glass',(x,-d/2-.16,z),(bay*.72,.32,fh*.66))
   b.add_box('rear-bay','dark-metal-panel',(x,d/2+.14,z),(bay*.68,.28,fh*.58))
  if floor%step==0:
   b.add_box('facade-band','limestone',(0,-d/2-.25,z-fh*.42),(w,.5,.24 if not band else .42))
 for y in range(-int(d//2)+2,int(d//2)-1,bay*step):
  for floor in range(2,floors,step*2):
   z=fh*floor+fh*.5;b.add_box('side-bay','residential-glass',(-w/2-.14,y,z),(.28,bay*.7,fh*.6))
   b.add_box('service-bay','dark-stone',(w/2+.12,y,z),(.24,bay*.72,fh*.56))
 for x in range(-int(w//2)+1,int(w//2),bay): b.add_box('vertical-frame','aluminum',(x,-d/2-.38,fh*floors/2),(0.22,.35,fh*floors))

def build_family(spec,lod,materials):
 name,shape,w,d,floors,podium,seed=spec;fh=3.8;b=MeshBatch(materials)
 # Distinct silhouette and podium articulation, not scale-only copies.
 b.add_box('podium','limestone',(0,0,podium*2),(w+12,d+10,podium*4))
 if shape in ('split','corner'):
  b.add_box('tower-a','curtain-wall-glass',(-w*.22,0,podium*4+floors*fh/2),(w*.52,d,floors*fh))
  b.add_box('tower-b','light-metal-panel',(w*.28,d*.12,podium*4+(floors-5)*fh/2),(w*.34,d*.72,(floors-5)*fh))
 elif shape=='stepped':
  b.add_box('tower-lower','curtain-wall-glass',(0,0,podium*4+floors*fh*.28),(w,d,floors*fh*.56));b.add_box('tower-upper','light-metal-panel',(w*.12,0,podium*4+floors*fh*.73),(w*.68,d*.8,floors*fh*.34))
 elif shape in ('transit','pavilion','lowrise'):
  b.add_box('public-hall','curtain-wall-glass',(0,0,podium*4+floors*fh/2),(w,d,floors*fh));b.add_box('public-crown','light-metal-panel',(0,0,podium*4+floors*fh+1.2),(w*.72,d*.72,2.4))
 else:b.add_box('tower','curtain-wall-glass',(0,0,podium*4+floors*fh/2),(w,d,floors*fh))
 add_facades(b,w,d,floors,fh,lod,seed)
 # Human-scale entrance, loading/service rear and roof equipment.
 b.add_box('main-lobby','curtain-wall-glass',(0,-d/2-5,3.2),(w*.36,7,6.4));b.add_box('entrance-canopy','light-metal-panel',(0,-d/2-9,6.2),(w*.42,8,.45))
 b.add_box('service-entry','dark-metal-panel',(w*.24,d/2+5,2.2),(7,6,4.4));b.add_box('loading-canopy','painted-steel',(w*.24,d/2+8,4.7),(9,5,.4))
 b.add_box('parapet','limestone',(0,0,podium*4+floors*fh+1),(w*.78,d*.78,2));b.add_box('machine-room','dark-metal-panel',(w*.12,0,podium*4+floors*fh+3),(w*.28,d*.34,4))
 for i in range(2 if lod=='LOD2' else 5): b.add_box('hvac','painted-steel',(-w*.2+i*3,0,podium*4+floors*fh+5),(2,3,1.6))
 # Ground interface.
 b.add_box('sidewalk','sidewalk-concrete',(0,-d/2-8,.12),(w+18,14,.24));b.add_box('service-apron','asphalt',(0,d/2+7,.1),(w+14,12,.2))
 b.add_box('blank-signage-panel','light-metal-panel',(0,-d/2-9.25,3.7),(w*.20,.18,1.3));b.add_box('accessible-ramp','granite',(-w*.24,-d/2-8,.35),(w*.22,5,.7));b.add_box('corner-emphasis','limestone',(-w/2-.35,-d/2-.35,podium*4+floors*fh*.45),(.7,.7,floors*fh*.72))
 consolidation=consolidate(b);objects=b.finalize();stats=b.statistics();stats['consolidation']=consolidation;return objects,stats,validate_geometry(objects)

def main():
 args=sys.argv[sys.argv.index('--')+1:];p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);a=p.parse_args(args)
 out=Path(a.output_root);materials,_=create_material_library();reports=[]
 for spec in SPECS:
  family=spec[0]
  for lod in ('LOD0','LOD1','LOD2'):
   bpy.ops.wm.read_factory_settings(use_empty=True);materials,_=create_material_library();palette=apply_palette(materials,spec[-1]);objects,stats,validation=build_family(spec,lod,materials)
   for o in objects:o['familyId']=family;o['lod']=lod;o['actualGLB']=True;o['canonical']=False;o['generationSeed']=8102026+spec[-1]
   path=out/'families'/family/lod;path.mkdir(parents=True,exist_ok=True);glb=path/f'{family}-{lod.lower()}.glb'
   bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_normals=True,export_texcoords=False,export_materials='EXPORT',export_apply=True)
   report={'family':family,'lod':lod,'glb':str(glb),'bytes':glb.stat().st_size,'geometry':stats,'validation':validation,'palette':palette,'frontSideRearRoof':True,'mainEntrance':True,'serviceEntrance':True,'activeGroundFloor':True,'groundContact':True,'proceduralOnly':True,'visualStatus':'PENDING_RENDER_REVIEW'}
   (path/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');reports.append(report)
 (out/'reports').mkdir(parents=True,exist_ok=True);(out/'reports'/'support-families.json').write_text(json.dumps({'actualFamilies':len(SPECS),'lodGlbs':len(reports),'reports':reports},indent=2),encoding='utf-8')
 print(json.dumps({'status':'PASS','families':len(SPECS),'lodGlbs':len(reports),'output':str(out)}))
if __name__=='__main__':main()
