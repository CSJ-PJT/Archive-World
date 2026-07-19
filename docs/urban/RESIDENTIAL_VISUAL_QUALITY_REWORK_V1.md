# Residential Visual Quality Rework V1

## Scope and frozen baseline

This pass changes only `residential-courtyard-piloti-pq-v6`. The Office V5 baseline remains frozen at 82/B with status `PO_REVIEW_CANDIDATE`; its geometry, materials, renders, score, canonical state, and city-applied state are not changed. Canonical assets, V3 layout, runtime manifests, and `main` remain outside this work.

## Evidence-backed changes

- Three non-cloned masses now read as slab, point and courtyard edge, with three height tiers, independent upper setbacks and distinct crowns.
- Five vertical facade zones, seven bay families, five balcony families, three corner families, independent side/rear patterns and three horizontal bands replace the dominant full-height repetition.
- Main, secondary, community, service and parking entries form an explicit hierarchy. The active base also includes piloti, community frontage, parcel/security, bicycle and recycling functions.
- Seven paving/landscape zones, pedestrian spine, fire route, service lane, varied tree proxies, seating, planters, lighting, bicycles, people and vehicles clarify public-realm use. These remain unbranded procedural review proxies.
- Seventeen Residential-specific procedural materials extend the no-image foundation. The output remains `procedural-only`, with zero Image Texture nodes and zero external image references.
- Roofs use terraced, glass-lantern and offset-screen crowns plus machine rooms, HVAC screens, maintenance routes, solar zones and communications proxies.

## Reproduction

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run-residential-v6.ps1 `
  -BlenderPath 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
```

The runner generates LOD2, LOD1 and LOD0 in the external Generated root, renders the 20-view 1920×1920 package, runs pinned official `gltf-validator@2.0.0-dev.3.10` in strict mode, and produces the evidence-linked quality report. It never runs the Office generator.

## Gate result

Residential V6 reaches 82/B as a `PO_REVIEW_CANDIDATE`, not canonical approval. LOD0/1/2 are 140,544 / 44,864 / 17,072 triangles. Facade repetition is 1.47%, official validator errors/warnings/infos are 0/0/0, and all 20 review images pass signature, 1920×1920, luminance and blank-frame checks. The score retains explicit limitations: procedural-only materials and abstract landscape/human/vehicle proxies.

Actual city application remains prohibited. The next Gate is PO visual review of the frozen Office V5 and Residential V6 pair; approval would permit proposing, not automatically performing, canonical promotion or city placement.
