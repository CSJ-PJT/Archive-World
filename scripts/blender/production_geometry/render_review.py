"""Production geometry review renderer with deterministic camera evidence."""
from __future__ import annotations

import time
from pathlib import Path

import bpy
from mathutils import Vector


VIEWS=(
 ("day-hero-front",(.75,-1.05,.58),(.0,0,.38),"day"),("day-hero-rear",(-.72,.95,.55),(.0,.08,.38),"day"),
 ("bird-view",(.55,-.68,1.25),(.0,0,.18),"day"),("street-entrance",(.18,-1.05,.11),(0,-.18,.09),"day"),
 ("courtyard-plaza",(-.38,-.72,.16),(0,.02,.1),"day"),("side-facade",(1.05,-.15,.42),(.12,0,.4),"overcast"),
 ("rear-service",(-.55,.98,.16),(-.12,.15,.11),"overcast"),("facade-closeup",(.45,-.62,.38),(.18,-.12,.42),"overcast"),
 ("entrance-closeup",(.08,-.78,.08),(0,-.2,.075),"day"),("ground-interface",(.32,-.75,.12),(.12,-.18,.04),"day"),
 ("roof-mechanical",(.48,-.42,1.18),(.1,.05,.78),"day"),("dusk",(.75,-1.05,.58),(.0,0,.38),"dusk"),
 ("wireframe-lod0",(.75,-1.05,.58),(.0,0,.38),"wire"),("material-breakdown",(.5,-.7,.3),(.15,-.12,.24),"overcast"),
 ("scale-check",(.12,-.82,.1),(0,-.2,.07),"day"),("procedural-only-status",(-.72,-.9,.5),(0,0,.38),"day"),
)


def _look(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()


def _area(name,location,energy,size,target):
    data=bpy.data.lights.new(name,"AREA"); data.energy=energy; data.shape="DISK"; data.size=size
    obj=bpy.data.objects.new(name,data); bpy.context.scene.collection.objects.link(obj); obj.location=location; _look(obj,target)


def setup(size):
    scene=bpy.context.scene; scene.render.engine="BLENDER_EEVEE"; scene.render.resolution_x=size; scene.render.resolution_y=size
    scene.render.resolution_percentage=100; scene.render.image_settings.file_format="PNG"; scene.view_settings.look="AgX - Medium High Contrast"
    scene.render.film_transparent=False
    camera_data=bpy.data.cameras.new("production-review-camera"); camera=bpy.data.objects.new("production-review-camera",camera_data)
    scene.collection.objects.link(camera); scene.camera=camera; camera.data.lens=52
    wire=bpy.data.materials.new("review-wireframe"); wire.use_nodes=True; nodes=wire.node_tree.nodes; links=wire.node_tree.links
    for node in list(nodes): nodes.remove(node)
    out=nodes.new("ShaderNodeOutputMaterial"); emission=nodes.new("ShaderNodeEmission"); wire_node=nodes.new("ShaderNodeWireframe")
    ramp=nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color=(.015,.02,.025,1); ramp.color_ramp.elements[1].color=(.7,.9,1,1)
    wire_node.inputs["Size"].default_value=.8; links.new(wire_node.outputs[0],ramp.inputs[0]); links.new(ramp.outputs[0],emission.inputs[0]); links.new(emission.outputs[0],out.inputs[0])
    return camera,wire


def render_views(output,objects,bounds,size=1920):
    output=Path(output); output.mkdir(parents=True,exist_ok=True); scene=bpy.context.scene; camera,wire=setup(size)
    dimensions=bounds["dimensions"]; center=[(bounds["min"][i]+bounds["max"][i])/2 for i in range(3)]
    radius=max(dimensions[0],dimensions[1],dimensions[2]); results=[]
    original_override=scene.view_layers[0].material_override
    for name,position,target_offset,lighting in VIEWS:
        for obj in list(bpy.data.objects):
            if obj.type=="LIGHT": bpy.data.objects.remove(obj,do_unlink=True)
        target=(center[0]+target_offset[0]*dimensions[0],center[1]+target_offset[1]*dimensions[1],bounds["min"][2]+target_offset[2]*dimensions[2])
        camera.location=(center[0]+position[0]*radius,center[1]+position[1]*radius,bounds["min"][2]+position[2]*radius); _look(camera,target)
        if lighting=="dusk": scene.world.color=(.055,.08,.13); scene.view_settings.exposure=.55; energy=(1300,700,900)
        else: scene.world.color=(.55,.62,.7) if lighting=="day" else (.42,.45,.48); scene.view_settings.exposure=.7; energy=(2600,1300,1500)
        _area("key",(center[0]+radius*.6,center[1]-radius*.7,bounds["max"][2]+radius*.45),energy[0],radius*.28,target)
        _area("fill",(center[0]-radius*.65,center[1]-radius*.2,bounds["max"][2]*.65),energy[1],radius*.3,target)
        _area("rim",(center[0],center[1]+radius*.65,bounds["max"][2]),energy[2],radius*.22,target)
        scene.view_layers[0].material_override=wire if lighting=="wire" else original_override
        path=output/f"{name}.png"; scene.render.filepath=str(path); started=time.monotonic(); bpy.ops.render.render(write_still=True)
        results.append({"view":name,"file":path.name,"bytes":path.stat().st_size,"seconds":round(time.monotonic()-started,3),"pngSignature":path.read_bytes()[:8].hex(),"resolution":[size,size]})
    scene.view_layers[0].material_override=original_override
    return results
