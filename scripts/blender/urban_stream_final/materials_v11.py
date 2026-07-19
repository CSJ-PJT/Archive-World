"""Archive-native procedural material hierarchy for the final stream district."""
from __future__ import annotations

import bpy

SPECS = {
    "archive-warm-stone": ((0.62, 0.53, 0.42, 1), 0.66, 0.0, 2.4),
    "ledger-limestone": ((0.56, 0.54, 0.48, 1), 0.62, 0.0, 1.8),
    "ledger-granite": ((0.10, 0.12, 0.13, 1), 0.48, 0.0, 1.2),
    "wet-stone": ((0.19, 0.22, 0.21, 1), 0.28, 0.0, 0.9),
    "dry-stone": ((0.44, 0.45, 0.42, 1), 0.74, 0.0, 1.5),
    "blue-gray-glass": ((0.10, 0.25, 0.31, 0.45), 0.16, 0.0, 3.0),
    "shallow-water-v11": ((0.025, 0.19, 0.23, 0.68), 0.16, 0.0, 5.5),
    "dark-water-bed": ((0.055, 0.075, 0.07, 1), 0.92, 0.0, 0.7),
    "archive-metal": ((0.10, 0.23, 0.28, 1), 0.31, 0.68, 1.1),
    "ledger-bronze": ((0.24, 0.15, 0.08, 1), 0.34, 0.72, 0.8),
    "service-charcoal": ((0.055, 0.065, 0.072, 1), 0.52, 0.42, 1.0),
    "promenade-paver": ((0.39, 0.40, 0.38, 1), 0.78, 0.0, 0.55),
    "tactile-yellow": ((0.78, 0.56, 0.08, 1), 0.70, 0.0, 0.25),
    "timber-accent": ((0.31, 0.17, 0.07, 1), 0.58, 0.0, 0.38),
    "soil-v11": ((0.10, 0.065, 0.032, 1), 0.95, 0.0, 0.45),
    "foliage-deep": ((0.065, 0.24, 0.10, 1), 0.88, 0.0, 0.65),
    "foliage-mid": ((0.12, 0.36, 0.15, 1), 0.84, 0.0, 0.72),
    "foliage-light": ((0.25, 0.46, 0.18, 1), 0.82, 0.0, 0.80),
    "warm-interior": ((0.52, 0.31, 0.12, 1), 0.38, 0.0, 0.42),
    "archive-cyan-light": ((0.05, 0.42, 0.48, 1), 0.30, 0.0, 0.2),
    "warm-light": ((0.95, 0.52, 0.18, 1), 0.28, 0.0, 0.2),
}


def create_materials():
    result = {}
    for index, (name, (color, roughness, metallic, scale)) in enumerate(SPECS.items()):
        material = bpy.data.materials.new(name)
        material.use_nodes = True
        material.diffuse_color = color
        material["proceduralOnly"] = True
        material["provenance"] = "Archive native procedural V11"
        material["mappingScaleM"] = scale
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        bsdf = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 3.0 / scale
        noise.inputs["Detail"].default_value = 3.0
        noise.inputs["Roughness"].default_value = 0.62
        noise.inputs["Distortion"].default_value = (index % 4) * 0.08
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12 if "glass" not in name and "water" not in name else 0.035
        bump.inputs["Distance"].default_value = 0.08
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        if "glass" in name or "water-v11" in name:
            bsdf.inputs["Alpha"].default_value = color[3]
            bsdf.inputs["Transmission Weight"].default_value = 0.28 if "water" in name else 0.18
            bsdf.inputs["IOR"].default_value = 1.333 if "water" in name else 1.47
            material.surface_render_method = "DITHERED"
        if name in ("archive-cyan-light", "warm-light", "warm-interior"):
            bsdf.inputs["Emission Color"].default_value = color
            bsdf.inputs["Emission Strength"].default_value = 5.0 if name in ("archive-cyan-light", "warm-light") else 1.6
        result[name] = material
    assert len(bpy.data.images) == 0
    assert not any(node.type == "TEX_IMAGE" for material in result.values() for node in material.node_tree.nodes)
    return result
