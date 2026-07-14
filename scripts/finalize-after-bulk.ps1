param(
  [string]$Repo = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $Repo
$env:BLENDER_PATH = [Environment]::GetEnvironmentVariable('BLENDER_PATH', 'User')
$log = Join-Path $Repo '.work\finalize-after-bulk.log'
function Write-Stage([string]$Message) { "$(Get-Date -Format o) $Message" | Tee-Object -FilePath $log -Append }

Write-Stage 'Waiting for the single-concurrency bulk Blender process.'
while (Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'node(\.exe)?' -and $_.CommandLine -match 'bulk-process\.mjs' }) { Start-Sleep -Seconds 30 }
Write-Stage 'Bulk process exited. Generating catalog and validating layout.'
& node src\generate-catalog.mjs
& node src\validate-world.mjs
& npm.cmd run bulk:verify
if (-not (Test-Path -LiteralPath $env:BLENDER_PATH)) { throw 'BLENDER_PATH is unavailable for world scene generation.' }
Write-Stage 'Building archive-city-v1 Blender scene and GLB.'
& $env:BLENDER_PATH --background --python scripts\blender\build_city.py -- --layout assets\world\archive-city-v1-layout.json --output-blend scenes\archive-city-v1.blend --output-glb assets\world\archive-city-v1.glb --preview assets\previews\archive-city-v1.png --screenshots-dir assets\previews\districts
if ($LASTEXITCODE -ne 0) { throw "World Blender build failed with exit code $LASTEXITCODE" }
Write-Stage 'World scene created. Running viewer production build.'
Push-Location web
try { & npm.cmd run build } finally { Pop-Location }
Write-Stage 'Finalize after bulk complete. No git, OCI, commit, or push action was performed.'
