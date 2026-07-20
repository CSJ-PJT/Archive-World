"""Create a non-destructive performance LOD from a validated Hero GLB."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


def triangle_count(objects):
    return sum(len(obj.data.loop_triangles) if obj.data.loop_triangles else
               (obj.data.calc_loop_triangles() or len(obj.data.loop_triangles))
               for obj in objects if obj.type == "MESH")


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ratio", type=float, default=.28)
    parser.add_argument("--report", required=True)
    parsed = parser.parse_args(args)
    source = Path(parsed.input)
    target = Path(parsed.output)
    report_path = Path(parsed.report)
    assert source.exists() and source.resolve() != target.resolve()
    assert .08 <= parsed.ratio <= .55
    target.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    assert meshes
    before = triangle_count(meshes)
    material_slots = sum(len(obj.material_slots) for obj in meshes)
    for obj in meshes:
        if len(obj.data.polygons) < 80:
            continue
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        modifier = obj.modifiers.new("archive-performance-lod", "DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = parsed.ratio
        modifier.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        obj.select_set(False)
    after = triangle_count(meshes)
    assert 0 < after < before
    assert after / before <= parsed.ratio + .08
    assert sum(len(obj.material_slots) for obj in meshes) == material_slots
    bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB",
                              export_yup=True, export_normals=True,
                              export_texcoords=False, export_materials="EXPORT",
                              export_apply=True)
    report = {
        "status": "TECHNICAL_PASS_VISUAL_GATE_PENDING",
        "source": str(source), "output": str(target),
        "ratioTarget": parsed.ratio, "trianglesBefore": before,
        "trianglesAfter": after, "ratioActual": after / before,
        "meshObjects": len(meshes), "materialSlots": material_slots,
        "sourceUnchanged": True, "officeV5Changed": False,
        "canonical": False, "v3Applied": False,
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
