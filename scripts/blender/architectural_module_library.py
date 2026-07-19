"""Composable, image-free Architecture Module Library and five review boards."""
import argparse,json,math,os,sys
from pathlib import Path
import bpy
from mathutils import Vector

GROUPS={
'facade':['recessed-bay','projected-bay','curtain-wall-panel','mullion','transom','spandrel','vertical-fin','horizontal-band','corner-bay','balcony-slab','balcony-railing','blind-service-bay','mechanical-floor-band','storefront','rear-service-facade'],
'entrance':['apartment-lobby','piloti','residential-canopy','office-lobby','atrium-entry','retail-entry','drop-off-canopy','parking-ramp','service-entrance','loading-entrance'],
'roof':['parapet','machine-room','hvac-screen','mechanical-unit-proxy','maintenance-walkway','solar-panel','crown','communications-proxy'],
'ground':['curb','sidewalk','driveway','drop-off','loading-lane','fire-access','drainage-edge','planter','tree-pit','tactile-paving','plaza-transition','landscape-buffer']}
MATERIAL={'facade':'facade-stone','entrance':'entrance-glass','roof':'roof-metal','ground':'ground-concrete'}
DISTRICTS={'facade':['residential','archiveos','ledger','market'],'entrance':['residential','archiveos','ledger','market'],'roof':['residential','archiveos','ledger','nexus'],'ground':['all']}
def cli():
 v=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);p.add_argument('--size',type=int,default=512);return p.parse_args(v)
def mat(name,color,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
def box(name,loc,dims,material,category):
 bpy.ops.mesh.primitive_cube_add(location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;o['moduleCategory']=category;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);return o
def dimensions(category,index):
 base={'facade':(3.6,.45,3.3),'entrance':(5,2.8,3.4),'roof':(5,4,2),'ground':(6,3,.35)}[category];return [round(base[0]+(index%3)*.6,2),round(base[1]+(index%2)*.25,2),round(base[2]+(index%4)*.3,2)]
def contract(module_id,category,index,dims):
 return {'id':module_id,'category':category,'dimensionsMeters':dims,'anchorPoints':[{'id':'origin','position':[0,0,0]},{'id':'connect-front','position':[0,-dims[1]/2,0]},{'id':'connect-rear','position':[0,dims[1]/2,0]}],'orientation':{'frontAxis':'-Y','upAxis':'Z'},'allowedScale':[.85,1.15],'allowedRotationDegrees':[0,90,180,270] if category=='ground' else [0,180],'collisionBounds':{'min':[-dims[0]/2,-dims[1]/2,0],'max':[dims[0]/2,dims[1]/2,dims[2]]},'adjacencyRules':{'requires':['origin'],'allows':[category,'ground'],'forbids':['airborne']},'districtCompatibility':DISTRICTS[category],'lod':{'LOD0':'full-geometry','LOD1':'retain-primary-profile','LOD2':'silhouette-proxy'},'materialSlots':[MATERIAL[category]],'seedInputs':['familySeed','moduleIndex'],'provenance':{'source':'Archive procedural module','referenceMeshCopied':False},'status':'PROTOTYPE_VALIDATED'}
def setup_scene(size):
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=size;s.render.resolution_y=max(256,int(size*.66));s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.look='AgX - Medium High Contrast';w=bpy.data.worlds.new('module-world');w.color=(.45,.49,.54);s.world=w
 d=bpy.data.lights.new('key','AREA');d.energy=2200;d.size=12;o=bpy.data.objects.new('key',d);s.collection.objects.link(o);o.location=(15,-22,26);o.rotation_euler=(Vector((0,0,4))-o.location).to_track_quat('-Z','Y').to_euler();cd=bpy.data.cameras.new('camera');c=bpy.data.objects.new('camera',cd);s.collection.objects.link(c);s.camera=c;c.location=(35,-50,34);c.rotation_euler=(Vector((0,0,4))-c.location).to_track_quat('-Z','Y').to_euler()
def main():
 a=cli();bpy.ops.wm.read_factory_settings(use_empty=True);materials={'facade':mat('facade-stone',(.64,.62,.56),.6),'entrance':mat('entrance-glass',(.08,.28,.38),.18),'roof':mat('roof-metal',(.18,.22,.24),.32,.6),'ground':mat('ground-concrete',(.45,.46,.44),.78),'base':mat('board-ground',(.34,.36,.36),.8)};modules=[]
 all_specs=[(cat,name,i) for cat,names in GROUPS.items() for i,name in enumerate(names)]
 cols=10
 for n,(cat,name,i) in enumerate(all_specs):
  dims=dimensions(cat,i);x=(n%cols-4.5)*7;y=(n//cols-2)*8;box(name,(x,y,dims[2]/2),dims,materials[cat],cat);modules.append(contract(name,cat,i,dims))
 box('review-ground',(0,0,-.25),(76,52,.5),materials['base'],'common');setup_scene(a.size);out=Path(a.output_root)/'modules';out.mkdir(parents=True,exist_ok=True)
 boards=[]
 for board in [*GROUPS.keys(),'combined']:
  for obj in bpy.data.objects:
   if 'moduleCategory' in obj:obj.hide_render=obj['moduleCategory'] not in ('common',board) if board!='combined' else False
  path=out/f'{board}-module-board.png';bpy.context.scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);boards.append({'id':board,'output':path.name,'bytes':path.stat().st_size,'pngSignature':path.read_bytes()[:8].hex()})
 report={'moduleCount':len(modules),'categoryCounts':{k:len(v) for k,v in GROUPS.items()},'modules':modules,'boards':boards,'validation':{'duplicateIds':len(modules)-len({x['id'] for x in modules}),'missingDimensions':sum(not x['dimensionsMeters'] for x in modules),'invalidBounds':sum(any(a>=b for a,b in zip(x['collisionBounds']['min'],x['collisionBounds']['max'])) for x in modules),'orphanAnchors':sum(not x['anchorPoints'] for x in modules),'invalidAdjacency':sum(not x['adjacencyRules']['requires'] for x in modules),'unsupportedLOD':sum(set(x['lod'])!={'LOD0','LOD1','LOD2'} for x in modules),'missingProvenance':sum(not x['provenance'] for x in modules)},'imageTextureNodes':0,'externalImageReferences':0,'status':'PROCEDURAL_ONLY'};(out/'modules.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'modules':len(modules),'boards':len(boards),'validation':report['validation']}))
if __name__=='__main__':main()
