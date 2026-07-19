# Production Geometry Deep Build V1

## Scope

This pass replaces the preserved V4 LOD2 composition proofs with two deterministic, procedural-only V5 review pilots. Generated GLB, Blend, PNG, logs, and packages stay outside Git. No canonical library, V3 layout, runtime, or main-branch changes are authorized.

Families:

- `residential-courtyard-piloti-pq-v5`
- `archive-cbd-twin-atrium-pq-v5`

## Geometry architecture

`scripts/blender/production_geometry/` separates batched primitive construction, facade systems, entrances/podiums, roof systems, ground/public realm, procedural material assignment, LOD contracts, metrics, rendering, and family generation. A box contributes geometry only when it represents an architectural component; artificial subdivision, hidden duplicates, and triangle padding are prohibited.

The residential pilot includes three height tiers, semi-courtyard massing, independent front/side/rear rules, balcony geometry, piloti, lobby, parking and service access, community pavilion, roof equipment, fire access, and landscape/sidewalk transitions. The office pilot includes asymmetric towers, a sky-lobby bridge, articulated curtain-wall bays, podium/atrium, storefronts, drop-off, parking/loading/service routes, distinct crowns, public plaza, water feature, and security/public-realm elements.

## Reproduction

From Windows PowerShell, with repository-relative source and an explicit Blender executable:

```powershell
./scripts/run-production-geometry-v5.ps1 `
  -BlenderPath $env:BLENDER_PATH `
  -OutputRoot 'C:/ArchiveData/World/Generated/v5/production-geometry-deep-build'
```

The runner generates LOD2 before LOD1 and LOD0, renders LOD0 review views, then invokes the pinned official Khronos validator in strict mode. Windows Blender must receive a native `C:/...` path, not `/mnt/c/...`.

## Quality gate

Every LOD must pass its triangle target, keep origin and ground alignment, preserve bounds and primary silhouette, contain no empty/loose geometry, and pass official validation with zero errors and warnings. Review evidence contains sixteen 1920×1920 images per family. Image checks cover PNG signature, dimensions, blank-frame rejection, luminance and clipping.

Visual scoring is independent of technical validation. In the initial V5 gate, Office reached a B review-candidate grade while Residential remained C; therefore actual city application and canonical promotion remain blocked. PO/user review is required before any city integration.

## Lifecycle

The V4 proof remains `FAILED_BASELINE_PRESERVED`. V5 outputs are `Generated` review artifacts, not canonical assets. Promotion order remains: technical validation → visual review → PO/user approval → explicit canonical proposal → separate city-layout approval.
