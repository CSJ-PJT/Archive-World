[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$BlenderPath,
    [string]$OutputRoot = 'C:/ArchiveData/World/Generated/v6/residential-visual-quality-rework',
    [ValidateRange(1920, 4096)][int]$RenderSize = 1920,
    [switch]$SkipRender
)
$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $PSScriptRoot
$Generator = Join-Path $Repo 'scripts/blender/production_geometry/residential_pq_v6.py'
$Validator = Join-Path $Repo 'scripts/validate_gltf.mjs'
$ValidatorDir = Join-Path $Repo 'tools/gltf-validator'
if (-not (Test-Path -LiteralPath $BlenderPath)) { throw 'Blender executable not found' }

function Convert-ToWslPath([string]$Path) {
    $normalized = $Path.Replace('\', '/')
    if ($normalized -notmatch '^([A-Za-z]):/(.*)$') { throw "Expected native Windows path: $Path" }
    return "/mnt/$($Matches[1].ToLower())/$($Matches[2])"
}

foreach ($lod in @('LOD2', 'LOD1', 'LOD0')) {
    $arguments = @('-b', '--python', $Generator, '--', '--lod', $lod, '--output-root', $OutputRoot)
    if ($lod -eq 'LOD0' -and -not $SkipRender) { $arguments += @('--render', '--render-size', $RenderSize) }
    & $BlenderPath @arguments
    if ($LASTEXITCODE -ne 0) { throw "Residential V6 generation failed: $lod" }
}

$family = 'residential-courtyard-piloti-pq-v6'
$glbs = @('LOD0', 'LOD1', 'LOD2') | ForEach-Object { "$OutputRoot/residential/$_/$family-$($_.ToLower()).glb" }
$validation = "$OutputRoot/validation-all-lods.json"
$env:ARCHIVE_GLTF_VALIDATOR_DIR = $ValidatorDir
& node $Validator '--strict' '--report' $validation @glbs
if ($LASTEXITCODE -ne 0) { throw 'Official glTF validation failed' }
if (-not $SkipRender) {
    $wslRepo = Convert-ToWslPath $Repo
    $wslOutput = Convert-ToWslPath $OutputRoot
    $wslValidation = Convert-ToWslPath $validation
    & wsl.exe --cd $wslRepo python3 scripts/urban/residential_v6_quality_report.py --root $wslOutput --validator $wslValidation
    if ($LASTEXITCODE -ne 0) { throw 'Residential V6 quality gate failed' }
}
Write-Output "Residential V6 build, strict validation and quality gate PASS: $OutputRoot"
