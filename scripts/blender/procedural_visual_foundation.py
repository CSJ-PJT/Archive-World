"""Image-free architectural material/studio/pilot smoke path for Blender 5.2."""
import argparse,json,os,sys
import bpy
from mathutils import Vector
NAMES=['painted-concrete','exposed-concrete','light-stone','dark-stone','curtain-wall-glass','residential-glass','aluminum-mullion','metal-panel','brick-accent','asphalt','sidewalk-concrete','plaza-stone']
COLORS=[(.48,.5,.48),(.38,.39,.37),(.72,.68,.57),(.19,.18,.16),(.05,.18,.27),(.18,.34,.4),(.37,.42,.45),(.12,.15,.17),(.42,.2,.13),(.055,.06,.065),(.58,.58,.55),(.68,.62,.5)]
def a():
 v=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);p.add_argument('--mode',choices=('materials','residential','office'),required=True);p.add_argument('--size',type=int,default=512);return p.parse_args(v)
def box(n,l,d,m):
 bpy.ops.mesh.primitive_cube_add(location=l);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return o
def material(n,c,i):
 m=bpy.data.materials.new(n);m.use_nodes=True;t=m.node_tree;t.nodes.clear();out=t.nodes.new('ShaderNodeOutputMaterial');bs=t.nodes.new('ShaderNodeBsdfPrincipled');noise=t.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3+i*.37;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.7;ramp=t.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*[x*.55 for x in c],1);ramp.color_ramp.elements[1].color=(*[min(1,x*1.25+.04) for x in c],1);bump=t.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.14;bs.inputs['Roughness'].default_value=.18 if 'glass' in n else (.35 if 'metal' in n or 'mullion' in n else .68);bs.inputs['Metallic'].default_value=.72 if 'metal' in n or 'mullion' in n else 0;t.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);t.links.new(ramp.outputs['Color'],bs.inputs['Base Color']);t.links.new(noise.outputs['Fac'],bump.inputs['Height']);t.links.new(bump.outputs['Normal'],bs.inputs['Normal']);t.links.new(bs.outputs[0],out.inputs[0]);return m
def studio(size):
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=s.render.resolution_y=size;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('neutral');s.world.color=(.32,.36,.4);s.view_settings.look='AgX - Medium High Contrast'
 for loc,e,sz in [((8,-10,12),1700,8),((-10,-4,7),900,7),((2,8,10),1300,6)]:
  ld=bpy.data.lights.new('studio','AREA');ld.energy=e;ld.shape='DISK';ld.size=sz;o=bpy.data.objects.new('studio',ld);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
 camd=bpy.data.cameras.new('camera');cam=bpy.data.objects.new('camera',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(12,-18,12);cam.rotation_euler=(Vector((0,0,3))-cam.location).to_track_quat('-Z','Y').to_euler()
def render(path):os.makedirs(os.path.dirname(path),exist_ok=True);bpy.context.scene.render.filepath=path;bpy.ops.render.render(write_still=True)
def main():
 x=a();bpy.ops.wm.read_factory_settings(use_empty=True);mats=[material(n,c,i) for i,(n,c) in enumerate(zip(NAMES,COLORS))];box('ground',(0,0,-.2),(30,22,.4),mats[11]);studio(x.size)
 if x.mode=='materials':
  for i,m in enumerate(mats):box(m.name,((i%4-1.5)*5,(i//4-1)*5,1.5),(3.4,3.4,3),m)
 else:
  office=x.mode=='office';spec=[(-4,0,5,5,26 if office else 20),(4,1,4,4,21 if office else 16)]
  for i,(px,py,w,d,f) in enumerate(spec):
   h=f*3.4;box('tower',(px,py,h/2),(w,d,h),mats[4 if office else 0]);
   for z in range(4,int(h),7):box('facade-band',(px,py-d/2-.16,z),(w,.3,.35),mats[6]);box('facade-band',(px,py+d/2+.16,z),(w,.3,.35),mats[6])
   box('roof-machine',(px,py,h+1.5),(w*.35,d*.35,3),mats[7])
  box('podium',(0,-1,4),(18,13,8),mats[2]);box('entrance',(0,-7.6,3),(7,.5,5),mats[4]);box('canopy',(0,-9,5.5),(9,3,.3),mats[7]);box('service',(8,4,2),(3,3,4),mats[3])
 out=os.path.join(x.output_root,x.mode);render(os.path.join(out,'preview.png'));external=[i.name for i in bpy.data.images if i.name!='Render Result'];json.dump({'mode':x.mode,'transientRenderResult':'Render Result' in bpy.data.images,'externalImageDatablocks':external,'externalImageReferences':0,'imageTextureNodes':0,'materials':NAMES,'studio':'AgX/key-fill-rim/neutral-ground','status':'PROCEDURAL_ONLY'},open(os.path.join(out,'report.json'),'w'),indent=2)
if __name__=='__main__':main()
