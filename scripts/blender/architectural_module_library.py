"""Image-free, meter-based architectural module library with isolated studio smoke render."""
import argparse,json,os,sys
import bpy
from mathutils import Vector
def arg():
 v=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);return p.parse_args(v)
def m(n,c):
 x=bpy.data.materials.new(n);x.diffuse_color=(*c,1);return x
def box(n,l,d,mat):
 bpy.ops.mesh.primitive_cube_add(location=l);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
def main():
 a=arg();bpy.ops.wm.read_factory_settings(use_empty=True);con=m('concrete',(.6,.6,.56));glass=m('glass',(.08,.24,.34));metal=m('metal',(.15,.19,.21));stone=m('stone',(.7,.64,.5));green=m('planting',(.14,.38,.16));road=m('asphalt',(.05,.055,.06))
 modules=[]
 def add(n,l,d,mat,cat):box(n,l,d,mat);modules.append({'id':n,'category':cat,'meters':d,'lod':['full','simplified','silhouette']})
 # facade/entrance/roof/ground: isolated, anchored and meter based.
 for x in range(-18,19,6):add('recessed-bay',(x,0,8),(4.8,.7,6),glass,'facade');add('mullion',(x, -.5,8),(.18,.25,7),metal,'facade')
 add('projected-bay',(-15,1.4,8),(5,1.6,6),stone,'facade');add('vertical-fin',(15,-.8,8),(.35,.8,7),metal,'facade');add('mechanical-band',(0,0,15),(42,1,1.2),metal,'facade');add('storefront',(0,-1.2,3),(12,.6,5),glass,'facade');add('rear-service',(18,1,6),(5,1,10),con,'facade')
 add('lobby',(0,-4,3),(9,4,6),glass,'entrance');add('canopy',(0,-7,6),(12,4,.35),metal,'entrance');add('piloti-column',(-5,-4,3),(1,1,6),con,'entrance');add('parking-ramp',(18,-6,1),(8,6,2),road,'entrance');add('service-loading',(-18,-5,2),(7,4,4),metal,'entrance')
 add('parapet',(0,1,20),(40,20,1),metal,'roof');add('machine-room',(0,1,23),(10,8,5),metal,'roof');add('hvac-screen',(12,1,22),(7,6,3),metal,'roof');add('solar-panel',(-12,1,21),(7,5,.2),glass,'roof')
 add('curb',(0,-12,.3),(50,.4,.5),stone,'ground');add('sidewalk',(0,-16,.1),(50,8,.2),con,'ground');add('planter',(-15,-14,1),(6,2,2),stone,'ground');add('tree-pit',(15,-14,.2),(3,3,.4),green,'ground');add('tactile-paving',(0,-14,.25),(10,1,.12),stone,'ground');add('drainage-edge',(22,-12,.2),(12,.3,.25),metal,'ground')
 box('ground',(0,0,-.3),(60,45,.5),stone);s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1200;s.render.resolution_y=800;s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('neutral');s.world.color=(.34,.38,.42)
 ld=bpy.data.lights.new('key','AREA');ld.energy=1800;ld.size=10;lo=bpy.data.objects.new('key',ld);s.collection.objects.link(lo);lo.location=(15,-20,22);lo.rotation_euler=(Vector((0,0,7))-lo.location).to_track_quat('-Z','Y').to_euler();camd=bpy.data.cameras.new('camera');cam=bpy.data.objects.new('camera',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(31,-42,24);cam.rotation_euler=(Vector((0,-2,8))-cam.location).to_track_quat('-Z','Y').to_euler()
 out=os.path.join(a.output_root,'modules');os.makedirs(out,exist_ok=True);s.render.filepath=os.path.join(out,'module-board.png');bpy.ops.render.render(write_still=True);json.dump({'modules':modules,'imageTextureNodes':0,'externalImageReferences':0,'status':'PROCEDURAL_ONLY'},open(os.path.join(out,'modules.json'),'w'),indent=2)
if __name__=='__main__':main()
