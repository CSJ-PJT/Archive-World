"""ArchiveOS/Ledger procedural material hierarchy; no image nodes."""
PALETTES=((.96,.88,.72),(.70,.82,.94),(.76,.70,.58),(.62,.76,.82),(.84,.78,.66),(.56,.70,.80),(.88,.72,.54),(.66,.62,.58),(.48,.55,.60),(.72,.80,.86),(.82,.68,.52))
def apply_palette(materials,seed):
 accent=PALETTES[(seed-1)%len(PALETTES)]
 targets={'limestone':accent,'curtain-wall-glass':tuple(x*.42 for x in accent),'dark-metal-panel':tuple(x*.16 for x in accent),'light-metal-panel':tuple(x*.66 for x in accent),'granite':tuple(x*.28 for x in accent),'aluminum':tuple(x*.50 for x in accent)}
 for name,color in targets.items():
  material=materials[name];ramp=next((n for n in material.node_tree.nodes if n.type=='VALTORGB'),None)
  if ramp:
   ramp.color_ramp.elements[0].color=(*tuple(x*.68 for x in color),1);ramp.color_ramp.elements[1].color=(*tuple(min(1,x*1.08) for x in color),1)
  # glTF cannot serialize Blender procedural nodes. Preserve the procedural graph
  # for Blender review while exporting an explicit PBR base-color fallback.
  material.diffuse_color=(*color,1)
  bsdf=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bsdf and 'Base Color' in bsdf.inputs:
   for link in list(material.node_tree.links):
    if link.to_node==bsdf and link.to_socket.name=='Base Color': material.node_tree.links.remove(link)
   bsdf.inputs['Base Color'].default_value=(*color,1)
  material['districtPalette']='ArchiveOS' if seed%2 else 'Ledger';material['imageTextureNodes']=0
 return {'palette':materials['limestone']['districtPalette'],'accent':accent,'proceduralOnly':True,'gltfPbrFallback':True}
