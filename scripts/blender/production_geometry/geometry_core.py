"""Batched deterministic mesh primitives for meaningful architectural geometry."""
from __future__ import annotations

import math
from collections import defaultdict

import bpy


class MeshBatch:
    """Accumulate architectural primitives into one mesh per role/material pair."""

    def __init__(self, materials):
        self.materials = materials
        self.data = defaultdict(lambda: {"vertices": [], "faces": [], "components": 0})
        self.component_roles = defaultdict(int)

    def _append(self, role, material, vertices, faces):
        key = (role, material)
        bucket = self.data[key]
        offset = len(bucket["vertices"])
        bucket["vertices"].extend(vertices)
        bucket["faces"].extend(tuple(offset + index for index in face) for face in faces)
        bucket["components"] += 1
        self.component_roles[role] += 1

    def add_box(self, role, material, center, dimensions, rotation_z=0.0):
        cx, cy, cz = center; dx, dy, dz = dimensions
        assert dx > 0 and dy > 0 and dz > 0
        local = [
            (-dx/2,-dy/2,-dz/2),(dx/2,-dy/2,-dz/2),(dx/2,dy/2,-dz/2),(-dx/2,dy/2,-dz/2),
            (-dx/2,-dy/2,dz/2),(dx/2,-dy/2,dz/2),(dx/2,dy/2,dz/2),(-dx/2,dy/2,dz/2),
        ]
        cosine, sine = math.cos(rotation_z), math.sin(rotation_z)
        vertices = [(cx+x*cosine-y*sine, cy+x*sine+y*cosine, cz+z) for x,y,z in local]
        faces = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
        self._append(role, material, vertices, faces)

    def add_wedge(self, role, material, center, dimensions, rise_axis="y"):
        cx, cy, cz = center; dx, dy, dz = dimensions
        if rise_axis == "y":
            vertices = [(-dx/2,-dy/2,-dz/2),(dx/2,-dy/2,-dz/2),(dx/2,dy/2,-dz/2),(-dx/2,dy/2,-dz/2),
                        (-dx/2,dy/2,dz/2),(dx/2,dy/2,dz/2)]
        else:
            vertices = [(-dx/2,-dy/2,-dz/2),(dx/2,-dy/2,-dz/2),(dx/2,dy/2,-dz/2),(-dx/2,dy/2,-dz/2),
                        (dx/2,-dy/2,dz/2),(dx/2,dy/2,dz/2)]
        vertices = [(cx+x,cy+y,cz+z) for x,y,z in vertices]
        faces = [(0,2,1),(0,3,2),(3,5,2),(0,1,5),(0,5,4),(1,2,5),(0,4,3),(3,4,5)]
        self._append(role, material, vertices, faces)

    def add_cylinder(self, role, material, center, radius, height, segments=12):
        cx, cy, cz = center; vertices = []
        for z in (-height/2, height/2):
            vertices.extend((cx+radius*math.cos(2*math.pi*i/segments), cy+radius*math.sin(2*math.pi*i/segments), cz+z) for i in range(segments))
        vertices.extend(((cx,cy,cz-height/2),(cx,cy,cz+height/2)))
        bottom, top = 2*segments, 2*segments+1; faces = []
        for i in range(segments):
            n=(i+1)%segments; faces.extend(((i,n,segments+n),(i,segments+n,segments+i),(bottom,n,i),(top,segments+i,segments+n)))
        self._append(role, material, vertices, faces)

    def finalize(self, collection=None):
        collection = collection or bpy.context.scene.collection
        objects = []
        for (role, material_name), bucket in sorted(self.data.items()):
            mesh = bpy.data.meshes.new(f"{role}-{material_name}-mesh")
            mesh.from_pydata(bucket["vertices"], [], bucket["faces"]); mesh.update(calc_edges=True)
            obj = bpy.data.objects.new(f"{role}-{material_name}", mesh); collection.objects.link(obj)
            obj.data.materials.append(self.materials[material_name]); obj["role"] = role
            obj["componentCount"] = bucket["components"]; obj["productionGeometry"] = True
            objects.append(obj)
        return objects

    def statistics(self):
        triangles = sum(len(bucket["faces"]) for bucket in self.data.values())
        vertices = sum(len(bucket["vertices"]) for bucket in self.data.values())
        return {"triangles": triangles, "vertices": vertices, "meshObjects": len(self.data),
                "components": sum(x["components"] for x in self.data.values()), "roles": dict(self.component_roles)}


def validate_geometry(objects):
    empty = [o.name for o in objects if o.type == "MESH" and len(o.data.polygons) == 0]
    loose = []
    for obj in objects:
        if obj.type != "MESH": continue
        used = {index for polygon in obj.data.polygons for index in polygon.vertices}
        if len(used) != len(obj.data.vertices): loose.append(obj.name)
    return {"emptyMeshes": empty, "looseGeometry": loose, "meshCount": sum(o.type == "MESH" for o in objects)}
