param([switch]$SkipRuntimePreparation)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not $SkipRuntimePreparation) { node src/prepare-runtime-v2.mjs }
if (-not $env:BLENDER_PATH) { $env:BLENDER_PATH = [Environment]::GetEnvironmentVariable('BLENDER_PATH','User') }
if (-not $env:BLENDER_PATH -or -not (Test-Path $env:BLENDER_PATH)) { throw 'BLENDER_PATH is required.' }
& $env:BLENDER_PATH --background --python scripts/blender/build_city_v2.py -- --repo $root
if ($LASTEXITCODE -ne 0) { throw "Archive City v2 Blender build failed: $LASTEXITCODE" }
node src/validate-world-v2.mjs
Push-Location web
try { npm.cmd run typecheck; npm.cmd test; npm.cmd run build } finally { Pop-Location }
