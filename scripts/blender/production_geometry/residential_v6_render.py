"""Twenty-view Residential V6 review renderer."""
from __future__ import annotations

import time
from pathlib import Path

import bpy

from render_review import setup,_area,_look,_review_proxy


VIEWS=(
 ("day-hero-front",(.78,-1.08,.60),(0,0,.38),"day"),("day-hero-rear",(-.76,.98,.58),(0,.08,.38),"day"),
 ("bird-view",(.58,-.66,1.28),(0,.03,.20),"day"),("side-silhouette",(1.08,-.08,.48),(.04,.04,.42),"overcast"),
 ("main-entrance",(.08,-.90,.10),(0,-.22,.07),"day"),("secondary-entrance",(-.68,.42,.13),(-.18,.15,.08),"day"),
 ("community-frontage",(-.70,-.52,.12),(-.28,-.12,.07),"day"),("courtyard",(-.38,-.48,.18),(0,.08,.09),"day"),
 ("drop-off",(.28,-.88,.11),(.02,-.22,.06),"day"),("parking-ramp",(.68,-.55,.10),(.28,-.10,.05),"day"),
 ("service-rear",(-.58,.98,.17),(-.18,.18,.10),"overcast"),("facade-lower",(.42,-.66,.20),(.18,-.10,.22),"overcast"),
 ("facade-middle",(.58,-.58,.48),(.20,-.08,.48),"overcast"),("facade-upper",(.54,-.48,.80),(.15,0,.78),"overcast"),
 ("balcony-variation",(-.48,-.66,.42),(-.16,-.10,.42),"overcast"),("roof-mechanical",(.48,-.38,1.20),(.08,.04,.82),"day"),
 ("ground-public-realm",(.22,-.72,.15),(0,-.08,.05),"day"),("dusk",(.78,-1.08,.60),(0,0,.38),"dusk"),
 ("wireframe-lod0",(.78,-1.08,.60),(0,0,.38),"wire"),("lod-comparison",(-.85,-.82,.52),(0,0,.38),"wire"),
)


def render_residential_v6(output,objects,bounds,size=1920):
    output=Path(output); output.mkdir(parents=True,exist_ok=True); scene=bpy.context.scene; camera,wire=setup(size)
    dimensions=bounds["dimensions"]; center=[(bounds["min"][i]+bounds["max"][i])/2 for i in range(3)]
    radius=max(dimensions); results=[]; proxy_material=bpy.data.materials.new("v6-review-scale-proxy"); proxy_material.diffuse_color=(.82,.20,.05,1)
    _review_proxy("v6-review-human-1.75m",(center[0]-4,bounds["min"][1]+11,.875),(.5,.4,1.75),proxy_material)
    _review_proxy("v6-review-sedan-4.5m",(center[0]+5,bounds["min"][1]+11,.75),(4.5,1.8,1.5),proxy_material)
    original=scene.view_layers[0].material_override
    for name,position,target_offset,lighting in VIEWS:
        for obj in list(bpy.data.objects):
            if obj.type=="LIGHT": bpy.data.objects.remove(obj,do_unlink=True)
        target=(center[0]+target_offset[0]*dimensions[0],center[1]+target_offset[1]*dimensions[1],bounds["min"][2]+target_offset[2]*dimensions[2])
        camera.location=(center[0]+position[0]*radius,center[1]+position[1]*radius,bounds["min"][2]+position[2]*radius); _look(camera,target)
        background=scene.world.node_tree.nodes.get("Background")
        if lighting=="dusk":
            color=(.055,.08,.13,1); strength=.35; exposure=.75; energy=(2200,1200,1600)
        else:
            color=(.72,.78,.84,1) if lighting=="day" else (.62,.65,.68,1); strength=.8; exposure=.65; energy=(5200,2800,3200)
        scene.world.color=color[:3]; background.inputs["Color"].default_value=color; background.inputs["Strength"].default_value=strength; scene.view_settings.exposure=exposure
        _area("v6-key",(center[0]+radius*.6,center[1]-radius*.7,bounds["max"][2]+radius*.45),energy[0],radius*.28,target)
        _area("v6-fill",(center[0]-radius*.65,center[1]-radius*.2,bounds["max"][2]*.65),energy[1],radius*.3,target)
        _area("v6-rim",(center[0],center[1]+radius*.65,bounds["max"][2]),energy[2],radius*.22,target)
        scene.view_layers[0].material_override=wire if lighting=="wire" else original
        path=output/f"{name}.png"; scene.render.filepath=str(path); started=time.monotonic(); bpy.ops.render.render(write_still=True)
        results.append({"view":name,"file":path.name,"bytes":path.stat().st_size,"seconds":round(time.monotonic()-started,3),
                        "pngSignature":path.read_bytes()[:8].hex(),"resolution":[size,size],"streetLevel":name in {
                            "main-entrance","secondary-entrance","community-frontage","courtyard","drop-off","parking-ramp","service-rear","facade-lower","ground-public-realm"}})
    scene.view_layers[0].material_override=original
    return results
