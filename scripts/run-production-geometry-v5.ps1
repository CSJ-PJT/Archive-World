[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$BlenderPath,
    [string]$OutputRoot = 'C:/ArchiveData/World/Generated/v5/production-geometry-deep-build',
    [ValidateRange(1920, 4096)][int]$RenderSize = 1920,
    [switch]$SkipRender
)
$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $PSScriptRoot
$Generator = Join-Path $Repo 'scripts/blender/production_geometry'
$Validator = Join-Path $Repo 'scripts/validate_gltf.mjs'
$ValidatorDir = Join-Path $Repo 'tools/gltf-validator'
if (-not (Test-Path -LiteralPath $BlenderPath)) { throw "Blender executable not found" }

$jobs = @(
    @{ Mode = 'residential'; Script = 'residential_pq_v5.py'; LOD = 'LOD2'; Render = $false },
    @{ Mode = 'office'; Script = 'office_pq_v5.py'; LOD = 'LOD2'; Render = $false },
    @{ Mode = 'residential'; Script = 'residential_pq_v5.py'; LOD = 'LOD1'; Render = $false },
    @{ Mode = 'office'; Script = 'office_pq_v5.py'; LOD = 'LOD1'; Render = $false },
    @{ Mode = 'residential'; Script = 'residential_pq_v5.py'; LOD = 'LOD0'; Render = -not $SkipRender },
    @{ Mode = 'office'; Script = 'office_pq_v5.py'; LOD = 'LOD0'; Render = -not $SkipRender }
)
foreach ($job in $jobs) {
    $arguments = @('-b', '--python', (Join-Path $Generator $job.Script), '--', '--lod', $job.LOD, '--output-root', $OutputRoot)
    if ($job.Render) { $arguments += @('--render', '--render-size', $RenderSize) }
    & $BlenderPath @arguments
    if ($LASTEXITCODE -ne 0) { throw "Blender generation failed: $($job.Mode) $($job.LOD)" }
}

$glbs = @(
    "$OutputRoot/residential/LOD0/residential-courtyard-piloti-pq-v5-lod0.glb",
    "$OutputRoot/residential/LOD1/residential-courtyard-piloti-pq-v5-lod1.glb",
    "$OutputRoot/residential/LOD2/residential-courtyard-piloti-pq-v5-lod2.glb",
    "$OutputRoot/office/LOD0/archive-cbd-twin-atrium-pq-v5-lod0.glb",
    "$OutputRoot/office/LOD1/archive-cbd-twin-atrium-pq-v5-lod1.glb",
    "$OutputRoot/office/LOD2/archive-cbd-twin-atrium-pq-v5-lod2.glb"
)
$env:ARCHIVE_GLTF_VALIDATOR_DIR = $ValidatorDir
& node $Validator '--strict' '--report' "$OutputRoot/validation-all-lods.json" @glbs
if ($LASTEXITCODE -ne 0) { throw 'Official glTF validation failed' }
Write-Output "Production Geometry V5 build and strict validation PASS: $OutputRoot"
