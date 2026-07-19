# Procedural Material Guide

Procedural mode forbids `bpy.data.images.load`, `bpy.data.images.save`, Image Texture nodes, packed images, and external image references. The 20-material foundation uses deterministic node graphs with physically plausible Principled BSDF values, metre-scale mapping, base variation, roughness variation, and bump.

The calibration report must prove 20 materials, zero image datablocks, zero external image references, and no duplicate material signatures. Glass, metal, concrete, stone, ground, and water remain separate functional classes. A procedural material technical pass is not a substitute for daylight visual review.
