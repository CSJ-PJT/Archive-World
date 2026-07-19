$ErrorActionPreference = 'Stop'
$path = Join-Path $PSScriptRoot 'run-residential-v6.ps1'
$tokens = $null; $errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors) | Out-Null
if ($errors.Count -ne 0) { throw ($errors | Out-String) }
$source = Get-Content -LiteralPath $path -Raw
foreach ($required in @('LOD2', 'LOD1', 'LOD0', 'residential_pq_v6.py', '--strict', 'residential_v6_quality_report.py')) {
    if (-not $source.Contains($required)) { throw "Missing runner contract: $required" }
}
if ($source.Contains('office_pq_v5.py')) { throw 'Office V5 must remain frozen' }
Write-Output 'Residential V6 runner contract PASS'
