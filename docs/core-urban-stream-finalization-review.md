# Core + Urban Stream Finalization V1

## Scope and status

This branch produces a generated-only ArchiveOS–Ledger review district. It does not mutate canonical data, the V3 layout, runtime repositories, or the frozen Office V5 anchor. The V10 output remains the immutable comparison baseline; V11 is written under `C:/ArchiveData/World/Generated/v11/core-urban-stream-finalization`.

The final engineering result is reproducible and validator-clean, but the PO gate remains evidence-driven: visual and performance failures cannot be offset by technical checks.

## Concept direction boundary

Concept reference is used only for abstract spatial and visual-quality guidance. No direct reproduction of identifiable architecture, waterway design, bridge design, lighting arrangement, or urban plan is permitted.

The reference informed hierarchy, active frontage, stream/building relationships, pedestrian continuity, time-of-day differentiation, material depth and metropolitan density. Every generated mesh, material assignment, bridge section, frontage unit, planting rule and camera is Archive-native and deterministic.

## Implemented finalization

- Seven urban-section grammars distinguish civic plaza, financial terrace, transit, green, mixed active, service and future-gateway conditions.
- Eleven non-anchor support families have rebuilt bodies, three-part podiums, lower-floor grammars, stream entrances, terraces, rear service masses and roof equipment. Office V5 remains frozen.
- Forty-one occupied frontage units include shallow interiors, glazing, frames, doors, canopies, tactile thresholds and night states.
- Seven bridges retain distinct roles, approaches, railings, drainage, lights and accessibility/service contracts.
- Twenty-two tree families and thirty-eight low-planting families replace single-variant repetition. A material defect that accidentally made `foliage-light` emissive was found in the actual render and fixed.
- Twelve activity-cluster contracts place 81 human proxies and seven functional vehicles around arrival, lunch, transit, bridge, café and service conditions.
- Seventeen light-family contracts and bounded Viewer lights define four night hierarchy levels without illuminating every window.
- The actual 785.88 m stream GLB contains water, bed, retaining, stepped/ramped access, frontages, nodes, bridges, vegetation, activity and lighting geometry.

## Actual build contract

- Actual families: 12
- Actual blocks: 22
- Building instances: 220
- Planning proxy ratio: 0%
- Actual GLBs: 38
- Stream section types: 7
- Bridges/crossings: 7
- Access points: 8
- Major/pocket nodes: 3 / 4
- Active frontage: Archive 82%, Ledger 78%, Transit 77%, mixed corridor 67%, core boulevard 62%
- Viewer cameras: 36, captured in day/dusk/night for 108 actual WebGL screenshots
- Khronos validator: `gltf-validator@2.0.0-dev.3.10`, strict 38 files, errors/warnings/infos 0/0/0

## Measured performance

Headless Chrome 150 at 1920×1080 is an actual WebGL measurement, not a Hardware Chrome substitute.

| Profile | Day avg / 1% low / critical | Night avg / 1% low / critical | Draw calls | Triangles |
| --- | --- | --- | ---: | ---: |
| LOD1 review | 25.2 / 13.3 / 15.9 | 26.6 / 14.0 / 22.5 | 341 | 1,487,020 |
| LOD2 bounded | 25.3 / 12.3 / 16.6 | 24.9 / 16.1 / 13.4 | 339 | 660,152 |

The 55.6% triangle reduction changed day average by only +0.1 FPS. Within this headless environment, main-thread/timer constraints or non-triangle submission cost dominate. Draw-call policy passes; average, 1% low and critical-camera gates do not. A Hardware Chrome attempt produced no valid samples, so Hardware performance is `UNKNOWN`, not inferred.

## Honest visual gate

The V11 review remains a C-grade procedural city scene. The material hierarchy, occupied frontages, urban sections and Archive-native civic identity improve the V10 baseline, but near-camera vegetation, human activity, façade repetition, water legibility, lighting depth and foreground composition do not yet support a B claim. The evidence-linked score is generated at `reports/final-visual-quality-gate.json`.

Therefore:

- PO approval: not eligible
- New district expansion: not eligible
- Actual V3 application: not eligible
- Canonical promotion: not eligible

## Reproduction

```powershell
powershell -ExecutionPolicy Bypass -File scripts/urban_stream/build_final_stream.ps1 -Stage all
powershell -ExecutionPolicy Bypass -File scripts/urban_stream/capture_final_stream_review.ps1
```

The runner uses atomic checkpoints, skips completed stages, accepts only Windows-style Blender paths, isolates failures, and preserves V10. Generated GLBs, high-resolution PNGs, logs and packages remain outside Git.

## Next approval gate

No application gate is requested. A future rework would need a true near-camera asset pass: authored human silhouettes, non-primitive tree crowns, deeper occupied interiors, more differentiated support façades, more legible water material, better street camera blocking, and profiling on an authenticated Hardware Chrome session. Only after Visual 80+, Stream 10/12 and all FPS thresholds pass should PO review be requested.
