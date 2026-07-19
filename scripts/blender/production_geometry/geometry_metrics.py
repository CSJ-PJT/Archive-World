"""Geometry, completeness and material metrics for production pilots."""
from __future__ import annotations

from mathutils import Vector


def bounds(objects):
    minimum=[float("inf")]*3; maximum=[float("-inf")]*3
    for obj in objects:
        if obj.type!="MESH": continue
        for corner in obj.bound_box:
            point=obj.matrix_world@Vector(corner)
            for axis in range(3): minimum[axis]=min(minimum[axis],point[axis]); maximum[axis]=max(maximum[axis],point[axis])
    return {"min":[round(v,4) for v in minimum],"max":[round(v,4) for v in maximum],
            "dimensions":[round(maximum[i]-minimum[i],4) for i in range(3)]}


def collect(objects,batch_stats,facade,entrance,roof,ground,material_report):
    roles={}
    for obj in objects:
        role=obj.get("role","unclassified"); roles[role]=roles.get(role,0)+int(obj.get("componentCount",1))
    facade_components=sum(value for key,value in roles.items() if any(word in key for word in ("window","facade","mullion","transom","balcony","spandrel","fin","band","slab-edge","blind")))
    dominant=max((value for key,value in roles.items() if any(word in key for word in ("window","facade","mullion","transom","balcony","spandrel","fin","band","slab-edge","blind"))),default=0)
    result={**batch_stats,"bounds":bounds(objects),"origin":[0,0,0],"emptyMeshes":[],"looseGeometry":[],
            "materialSlots":sorted({slot.material.name for obj in objects if obj.type=="MESH" for slot in obj.material_slots if slot.material}),
            "roleComponents":roles,"facadePatternCount":len(facade.get("patterns",[])),
            "facadeRepetitionRatio":round(dominant/max(1,facade_components),4),"visibleDepthRangeMeters":facade["depthRangeMeters"],
            "sideFacadeComplete":any("side" in key for key in roles),"rearFacadeComplete":any("rear" in key for key in roles),
            "entranceCount":entrance["entranceCount"],"serviceAccess":any("service" in key or "loading" in key for key in roles),
            "roofEquipmentCount":roof["equipmentCount"],"groundInterfaceCount":ground["interfaceCount"],
            "humanScaleFeatureCount":entrance["humanScaleFeatures"],"imageTextureNodes":material_report["imageTextureNodes"],
            "externalImageReferences":material_report["externalImageReferences"]}
    return result
