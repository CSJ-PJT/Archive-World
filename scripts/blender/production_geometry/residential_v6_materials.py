"""Residential-specific procedural palette layered on the frozen 20-material foundation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import procedural_visual_foundation as foundation


SPECS=(
 ("warm-white-concrete",(.72,.70,.64),(.58,.76),.14,.42,0),
 ("cool-white-precast",(.68,.71,.72),(.54,.70),.11,.34,0),
 ("light-gray-stone",(.58,.59,.57),(.46,.64),.10,.28,0),
 ("light-stone",(.66,.63,.56),(.48,.64),.10,.30,0),
 ("dark-gray-accent",(.13,.15,.17),(.38,.56),.08,.18,.18),
 ("muted-blue-residential-glass",(.11,.24,.31),(.18,.30),.035,1.2,0),
 ("entrance-glazing",(.12,.29,.34),(.14,.26),.03,1.35,0),
 ("wood-community-accent",(.38,.22,.11),(.42,.60),.16,.10,0),
 ("courtyard-paver",(.58,.55,.50),(.56,.72),.13,.24,0),
 ("dropoff-paver",(.39,.42,.43),(.58,.76),.16,.20,0),
 ("tactile-paver",(.70,.55,.15),(.62,.78),.18,.12,0),
 ("play-surface",(.28,.39,.32),(.68,.84),.22,.16,0),
 ("landscape-soil",(.13,.085,.04),(.78,.94),.26,.05,0),
 ("landscape-green",(.16,.31,.12),(.70,.90),.24,.12,0),
 ("human-neutral",(.30,.34,.38),(.52,.68),.06,.08,0),
 ("vehicle-silver",(.42,.46,.48),(.28,.44),.05,.10,.35),
 ("dark-asphalt",(.035,.04,.045),(.76,.92),.28,.06,0),
)


def extend_residential_v6_palette(materials,metadata):
    """Create deterministic V6 aliases without image datablocks or external references."""
    for index,spec in enumerate(SPECS,start=100):
        material,item=foundation.make_material(spec,index)
        materials[material.name]=material; metadata[item["id"]]=item
    return {"paletteId":"archive-residential-warm-cool-v6","added":len(SPECS),"ids":[s[0] for s in SPECS],
            "imageTextureNodes":sum(n.type=="TEX_IMAGE" for m in materials.values() for n in m.node_tree.nodes),
            "externalImageReferences":0,"proceduralOnly":True,
            "zones":{"tower":["warm-white-concrete","cool-white-precast","muted-blue-residential-glass"],
                     "podium":["light-gray-stone","entrance-glazing","wood-community-accent"],
                     "ground":["courtyard-paver","dropoff-paver","landscape-soil","landscape-green"]}}
