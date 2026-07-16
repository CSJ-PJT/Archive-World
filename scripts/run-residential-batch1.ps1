param(
  [string]$OutputRoot = $env:ARCHIVE_WORLD_OUTPUT_ROOT,
  [string]$BlenderPath = $env:BLENDER_PATH
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $OutputRoot) { $OutputRoot = 'C:\ArchiveData\World\Generated' }
if (-not $BlenderPath) { $BlenderPath = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' }
if (-not (Test-Path -LiteralPath $BlenderPath)) { throw "Blender not found: $BlenderPath" }

$env:ARCHIVE_WORLD_OUTPUT_ROOT = $OutputRoot
$env:PYTHONDONTWRITEBYTECODE = '1'
& $BlenderPath -b --python (Join-Path $PSScriptRoot 'blender\generate_residential_batch1.py') -- --repo $repo --output-root $OutputRoot
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
