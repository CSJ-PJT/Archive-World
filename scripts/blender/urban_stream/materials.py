"""Export-safe procedural parameter materials; no image datablocks."""
import bpy

SPECS={
 'shallow-water':((.035,.16,.18,0.72),.18,0.0),'water-bed':((.12,.16,.13,1),.92,0),
 'warm-stone':((.58,.49,.36,1),.72,0),'pale-stone':((.67,.65,.58,1),.68,0),
 'dark-granite':((.10,.12,.13,1),.55,0),'steel':((.16,.22,.25,1),.32,.72),
 'railing':((.22,.28,.30,1),.28,.65),'glass':((.12,.28,.34,.38),.12,0),
 'wood':((.30,.16,.07,1),.64,0),'soil':((.12,.08,.04,1),.96,0),
 'foliage':((.12,.30,.16,1),.88,0),'foliage-light':((.24,.42,.20,1),.84,0),
 'paving':((.42,.44,.43,1),.82,0),'tactile':((.75,.55,.08,1),.72,0),
 'light-warm':((.95,.55,.20,1),.32,0),'service-metal':((.09,.11,.12,1),.48,.45),
}
def create_materials():
 result={}
 for name,(color,rough,metal) in SPECS.items():
  m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=color;m['proceduralOnly']=True;m['imageTextureNodes']=0;m['provenance']='Archive procedural seed 1001'
  bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Base Color'].default_value=color;bsdf.inputs['Roughness'].default_value=rough;bsdf.inputs['Metallic'].default_value=metal
  if name in ('shallow-water','glass'):
   bsdf.inputs['Alpha'].default_value=color[3];m.surface_render_method='DITHERED'
  if name=='light-warm':bsdf.inputs['Emission Color'].default_value=(.95,.32,.08,1);bsdf.inputs['Emission Strength'].default_value=2.5
  result[name]=m
 assert len(bpy.data.images)==0
 return result
