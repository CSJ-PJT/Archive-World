# Residential Batch 1 candidate metadata schema

Batch 1 records are **candidate-only**. They cannot be consumed by the V3
canonical manifest or layout until a separate human image review and canonical
promotion decision.

Each generated record follows `archive-world.residential-candidate-result/v1`.

|Field|Meaning|
|---|---|
|`assetId`|Stable candidate identifier from the committed Batch 1 configuration.|
|`family`, `form`, `floors`, `footprint`|The intended residential use and geometry contract. `form` must differ materially between accepted families.|
|`runtimePath`, `previewPaths`|Logical paths below the external Generated output root only.|
|`sha256`, `bytes`|The exported candidate GLB identity.|
|`bounds`, `triangleCount`, `materialCount`, `textureCount`|Measured Blender export statistics. The procedural candidates intentionally use no bitmap texture.|
|`groundAligned`|True only when the measured minimum Z is within 1 mm of ground and no geometry is below it.|
|`geometryFingerprint`, `nearDuplicate`|Structural duplicate-review evidence. A near duplicate is never recommended for canonical promotion.|
|`canonicalRecommendation`|`review-recommended` or `exclude-pending-regeneration`; it is not a canonical promotion.|

The manifest also records the Blender version, validator summary, and the
headless EEVEE sandbox measurement. It contains no machine-specific path,
credential, token, or V2/V3 canonical-manifest update.
