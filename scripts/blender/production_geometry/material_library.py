"""Production pilot material selection backed by the no-image procedural foundation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import procedural_visual_foundation as foundation


RESIDENTIAL_REQUIRED = ("painted-concrete","precast-concrete","residential-glass","balcony-glass","aluminum",
                        "dark-stone","sidewalk-concrete","asphalt","soil","plaza-paver","light-metal-panel",
                        "dark-metal-panel","painted-steel","wood-accent")
OFFICE_REQUIRED = ("limestone","granite","curtain-wall-glass","aluminum","dark-metal-panel","light-metal-panel",
                   "plaza-paver","asphalt","water","wood-accent","painted-steel","sidewalk-concrete")


def create_material_library():
    pairs=[foundation.make_material(spec,index) for index,spec in enumerate(foundation.SPECS)]
    materials={material.name:material for material,_ in pairs}; metadata={item["id"]:item for _,item in pairs}
    assert len(materials)==20 and len({item["signature"] for item in metadata.values()})==20
    return materials,metadata


def validate_assignment(mode, materials, metadata):
    required=RESIDENTIAL_REQUIRED if mode=="residential" else OFFICE_REQUIRED
    missing=[name for name in required if name not in materials]
    image_nodes=sum(node.type=="TEX_IMAGE" for material in materials.values() for node in material.node_tree.nodes)
    return {"required":list(required),"missing":missing,"materialCount":len(required),"foundationCount":len(materials),
            "imageTextureNodes":image_nodes,"externalImageReferences":0,
            "signatures":{name:metadata[name]["signature"] for name in required if name in metadata}}
