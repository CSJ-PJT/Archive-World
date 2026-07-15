param()
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not $env:BLENDER_PATH) { $env:BLENDER_PATH = [Environment]::GetEnvironmentVariable('BLENDER_PATH','User') }
if (-not $env:BLENDER_PATH -or -not (Test-Path $env:BLENDER_PATH)) { throw 'BLENDER_PATH is required.' }

& $env:BLENDER_PATH --background --python-exit-code 1 --python scripts/blender/create_geography_v3_kit.py -- --repo $root
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 geography kit failed: $LASTEXITCODE" }
& $env:BLENDER_PATH --background --python-exit-code 1 --python scripts/blender/build_asset_libraries_v3.py -- --repo $root
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 asset library build failed: $LASTEXITCODE" }
& $env:BLENDER_PATH --background --python-exit-code 1 --python scripts/blender/build_city_v3.py -- --repo $root
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 build failed: $LASTEXITCODE" }
& $env:BLENDER_PATH --background scenes/archive-city-v3.blend --python-exit-code 1 --python scripts/blender/render_geography_v3_views.py -- --repo $root
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 geography render failed: $LASTEXITCODE" }
& $env:BLENDER_PATH --background scenes/archive-city-v3.blend --python-exit-code 1 --python scripts/blender/render_metropolitan_v3_views.py -- --repo $root
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 metropolitan render failed: $LASTEXITCODE" }
& $env:BLENDER_PATH --background --python-exit-code 1 --python scripts/blender/validate_v3_blend_links.py -- --repo $root
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 linked resource validation failed: $LASTEXITCODE" }
node src/validate-world-v3.mjs
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 layout validation failed: $LASTEXITCODE" }
node src/validate-world-v3-spatial.mjs
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 spatial validation failed: $LASTEXITCODE" }
node src/validate-world-v3-distribution.mjs
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 distribution validation failed: $LASTEXITCODE" }
node src/validate-world-v2.mjs
if ($LASTEXITCODE -ne 0) { throw "Archive City v2 regression validation failed: $LASTEXITCODE" }
Push-Location web
try {
  npm.cmd run typecheck; if ($LASTEXITCODE -ne 0) { throw "Viewer typecheck failed: $LASTEXITCODE" }
  npm.cmd test; if ($LASTEXITCODE -ne 0) { throw "Viewer test failed: $LASTEXITCODE" }
  npm.cmd run build; if ($LASTEXITCODE -ne 0) { throw "Viewer build failed: $LASTEXITCODE" }
} finally { Pop-Location }
