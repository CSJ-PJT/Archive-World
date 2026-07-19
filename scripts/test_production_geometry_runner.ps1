$ErrorActionPreference = 'Stop'
$Source = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'run-production-geometry-v5.ps1')
$Tokens = $null
$Errors = $null
[void][System.Management.Automation.Language.Parser]::ParseInput($Source, [ref]$Tokens, [ref]$Errors)
if ($Errors.Count -ne 0) { throw ($Errors | Out-String) }
foreach ($Required in @('LOD0', 'LOD1', 'LOD2', '--strict', 'ARCHIVE_GLTF_VALIDATOR_DIR')) {
    if (-not $Source.Contains($Required)) { throw "Missing runner contract: $Required" }
}
if ($Source.Contains('dan18') -or $Source.Contains('csj1116')) { throw 'User path leaked into runner' }
Write-Output 'production geometry runner contract PASS'
