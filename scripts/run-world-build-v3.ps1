param(
  [string]$OutputRoot
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not $env:BLENDER_PATH) { $env:BLENDER_PATH = [Environment]::GetEnvironmentVariable('BLENDER_PATH','User') }
if (-not $env:BLENDER_PATH -or -not (Test-Path $env:BLENDER_PATH)) { throw 'BLENDER_PATH is required.' }

# Generated Blender artifacts never write into the Git working tree.  The
# command-line argument takes precedence over the environment, followed by the
# documented new-PC default.
if (-not $OutputRoot) { $OutputRoot = $env:ARCHIVE_WORLD_OUTPUT_ROOT }
if (-not $OutputRoot) { $OutputRoot = 'C:\ArchiveData\World\Generated' }
$OutputRoot = [IO.Path]::GetFullPath($OutputRoot)
$env:ARCHIVE_WORLD_OUTPUT_ROOT = $OutputRoot
$env:PYTHONDONTWRITEBYTECODE = '1'

$folders = @(
  'v2\runtime', 'v2\metadata',
  'v3\runtime', 'v3\scenes', 'v3\previews', 'v3\renders', 'v3\metadata', 'v3\viewer',
  'logs', 'reports', 'cache'
)
foreach ($folder in $folders) { New-Item -ItemType Directory -Force -Path (Join-Path $OutputRoot $folder) | Out-Null }

function Invoke-WorldBlender([string]$Script, [string[]]$Extra = @()) {
  & $env:BLENDER_PATH --background --python-exit-code 1 --python $Script -- --repo $root --output-root $OutputRoot @Extra
  if ($LASTEXITCODE -ne 0) { throw "Archive City v3 Blender step failed: $Script ($LASTEXITCODE)" }
}

Invoke-WorldBlender 'scripts/blender/create_geography_v3_kit.py'
Invoke-WorldBlender 'scripts/blender/build_asset_libraries_v3.py'
Invoke-WorldBlender 'scripts/blender/build_city_v3.py'

$master = Join-Path $OutputRoot 'v3\scenes\archive-city-v3.blend'
& $env:BLENDER_PATH --background $master --python-exit-code 1 --python scripts/blender/render_geography_v3_views.py -- --repo $root --output-root $OutputRoot
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 geography render failed: $LASTEXITCODE" }
& $env:BLENDER_PATH --background $master --python-exit-code 1 --python scripts/blender/render_metropolitan_v3_views.py -- --repo $root --output-root $OutputRoot
if ($LASTEXITCODE -ne 0) { throw "Archive City v3 metropolitan render failed: $LASTEXITCODE" }
Invoke-WorldBlender 'scripts/blender/validate_v3_blend_links.py'

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
  $env:ARCHIVE_WORLD_VIEWER_OUT_DIR = Join-Path $OutputRoot 'v3\viewer'
  npm.cmd run typecheck; if ($LASTEXITCODE -ne 0) { throw "Viewer typecheck failed: $LASTEXITCODE" }
  npm.cmd test; if ($LASTEXITCODE -ne 0) { throw "Viewer test failed: $LASTEXITCODE" }
  npm.cmd run build:generated; if ($LASTEXITCODE -ne 0) { throw "Generated Viewer build failed: $LASTEXITCODE" }
} finally { Pop-Location }

Write-Output "ARCHIVE_WORLD_OUTPUT_ROOT=$OutputRoot"
