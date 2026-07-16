# Archive World generated output pipeline

## Contract

Git holds source code, canonical inputs, regression fixtures, documentation,
and approved metadata.  An official Blender build must not write any generated
runtime GLB, Blend, preview, render, report, cache, or Viewer bundle back into
the working tree.

The default generated root is `C:\ArchiveData\World\Generated` on Windows
(` /mnt/c/ArchiveData/World/Generated` from WSL).  Its location is selected in
this order:

1. `--output-root` supplied to `scripts/run-world-build-v3.ps1` or Blender.
2. `ARCHIVE_WORLD_OUTPUT_ROOT`.
3. The documented default above.

Absolute machine paths are never written to generated manifests.  Generated
manifests use logical paths such as `v3/runtime/archiveos.glb` relative to the
selected output root.

## Layout

```text
Generated/
  v2/runtime/                 # copied read-only V2 runtime inputs
  v2/metadata/
  v3/runtime/                 # GLB, textures, generated libraries
  v3/scenes/                  # master, districts, canonical generated libraries
  v3/previews/
  v3/renders/
  v3/metadata/                # generated layout and manifests
  v3/viewer/                  # production Viewer bundle
  logs/
  reports/
  cache/
```

V2 Meshy checksums are copied unchanged into the external V2 runtime manifest.
The tracked V2/V3 fixture data remains read-only regression input.

## Official build

```powershell
$env:BLENDER_PATH = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\run-world-build-v3.ps1
```

The entry point passes the resolved output root to every V3 Blender stage and
to output-aware V3 validators.  The generated Viewer bundle is emitted below
`v3/viewer`; it is not `web/dist`.

## Viewer modes

- **SOURCE MODE** is the default regression-fixture experience.
- **GENERATED MODE** fetches `v3/metadata/archive-city-v3-layout.json` and
  `v3/metadata/archive-city-v3-manifest.json` from the generated root and
  loads previews/GLB from that same root.

Build a generated Viewer with `npm.cmd run build:generated`.  Serve it locally
only with:

```powershell
$env:ARCHIVE_WORLD_OUTPUT_ROOT = 'C:\ArchiveData\World\Generated'
node.exe scripts\serve-world-generated.mjs --host 127.0.0.1 --port 4173
```

The server deliberately binds to localhost and maps `/generated/` to the
external output root.  It is a local inspection helper, not a deployment path.

## Acceptance gate

After an official build, the repository must show no tracked or untracked
generated output.  Required evidence lives below `Generated/reports/`.
Run V2 regression, V3 layout/spatial/distribution, linked Blend validation,
GLB checks, Viewer typecheck/test/build, and Git LFS fsck before calling the
output separation complete.
