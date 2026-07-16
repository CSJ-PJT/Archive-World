# Residential Batch 1 candidate validation report

This report records a candidate-only procedural generation pass from
`ec82266`. None of these models are in the V2/V3 canonical manifest or layout,
and no candidate has been promoted.

## Result

- Candidates: 20 / 20 GLB generated below the external Generated root.
- Previews: 40 / 40 PNG (Asset and District Context for every candidate).
- Structural GLB validator: 0 errors; SHA-256, header, mesh/accessor and
  metadata checks passed.
- Ground alignment: 20 / 20; candidate minimum Z is 0 within the 1 mm rule.
- Near-duplicate fingerprints: 0. Each record has a different form,
  dimensions/component fingerprint, and its asset/context previews were
  visually checked.
- Geometry: 96–840 triangles per candidate; 4–6 materials; 0 bitmap textures.
- Candidate GLB size: 12,820–105,368 bytes; no candidate approaches the
  2 GiB policy limit.

## Sandbox measurement

The sandbox imported all 20 candidate GLBs, created 60 mesh-data-sharing
instances, then rendered one 1280×720 EEVEE frame.

|Measurement|Observed value|
|---|---:|
|GLB load time|0.8599 s|
|60-instance construction|0.0549 s|
|EEVEE frame time|0.9356 s|
|EEVEE frame-equivalent rate|1.07 FPS|
|Blender working set before / after|610.14 / 684.18 MiB|

The frame-equivalent figure is a reproducible headless Blender render measure,
not an interactive Viewer FPS claim. Viewer frame rate and device memory must
be measured only after a separately approved integration pass.

## Canonical decision

All 20 have `review-recommended` candidate status because no structural
duplicate was detected. This is a recommendation for human image review only;
it changes neither the canonical library nor the city layout. Batch 2 is not
started by this pass.

The external manifest contains every per-model floor count, footprint,
triangle/material/texture statistic, checksum, bounds and preview path:
`v3/metadata/candidates/residential-batch1-manifest.json` under the configured
Generated root.
