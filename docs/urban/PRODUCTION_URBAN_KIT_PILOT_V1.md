# Production Urban Kit Pilot V1 — Quality Gate

## Scope

The pilot generator creates ten candidate Building Family assets (five Residential and five ArchiveOS/Ledger), three LODs each, thirty Street/Public Realm candidates and a thirty-item environment scale kit. All output is external-only and candidate status. No asset is canonical, no V3 layout/runtime manifest is changed, and no reference mesh is used.

## Non-negotiable visual gate

Structural GLB/header checks, metadata and LOD counts are not visual approval. The initial generated blocks are expected to be reviewed under daylight for facade depth, PBR readability, entrance/ground detail, public realm, service rear, material differentiation and city-scale credibility. A score below 80 in Building or Family blocks city application.

## Current execution outcome

The first generated Residential hero exposed insufficient presentation quality: dark/default lighting, procedural material treatment without visible texture richness, incomplete public-realm/street detail and overly repetitive facade language. It is therefore **not production-ready**. Do not create more districts, promote these assets or apply them to the city layout. The correct next action is a bounded rework of the shared lighting/material/facade/public-realm modules, followed by a new visual review.

## Tooling caveat

The Khronos validator CLI was not available through the current reproducible Node toolchain. The pilot records this explicitly; GLB header checks are not substituted as an official validator PASS.
