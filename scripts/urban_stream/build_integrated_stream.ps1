param(
  [ValidateSet('plan','geometry','assembly','validate','viewer','all')][string]$Stage='all',
  [string]$OutputRoot='C:\ArchiveData\World\Generated\v10\core-urban-stream-integrated-rework',
  [string]$BaselineRoot='C:\ArchiveData\World\Generated\v9\core-district-visual-performance-rework'
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$blender='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
if(!(Test-Path $blender)){throw 'Blender 5.2 is required'}
$stream=Join-Path $OutputRoot 'stream';$checkpoints=Join-Path $OutputRoot 'checkpoints'
New-Item -ItemType Directory -Force -Path $stream,$checkpoints | Out-Null
function Mark([string]$name,[string]$status){$payload=@{stage=$name;status=$status;at=(Get-Date).ToUniversalTime().ToString('o')}|ConvertTo-Json;[IO.File]::WriteAllText((Join-Path $checkpoints "$name.json.tmp"),$payload);Move-Item -Force (Join-Path $checkpoints "$name.json.tmp") (Join-Path $checkpoints "$name.json")}
function WslPath([string]$path){
  $normalized=$path.Replace('\','/')
  $converted=(wsl.exe wslpath -a -- $normalized)
  if($LASTEXITCODE -or !$converted){throw "WSL path conversion failed: $path"}
  return $converted.Trim()
}

if($Stage -in @('plan','all')){Mark plan RUNNING;wsl.exe --cd (WslPath $repo) python3 scripts/urban_stream/plan_alignment.py --output (WslPath (Join-Path $stream 'alignment.json'));if($LASTEXITCODE){throw 'plan failed'};Mark plan PASS}
if($Stage -in @('geometry','all')){Mark geometry RUNNING;& $blender -b --factory-startup --python "$repo\scripts\blender\urban_stream\generate_stream.py" -- --alignment (Join-Path $stream 'alignment.json') --output-root $stream;if($LASTEXITCODE){throw 'geometry failed'};Mark geometry PASS}
if($Stage -in @('assembly','all')){
 Mark assembly RUNNING
 foreach($folder in @('families','infrastructure')){if(!(Test-Path (Join-Path $OutputRoot $folder))){Copy-Item -Recurse -LiteralPath (Join-Path $BaselineRoot $folder) -Destination (Join-Path $OutputRoot $folder)}}
 wsl.exe --cd (WslPath $repo) python3 scripts/urban_stream/assemble_integrated_district.py --v9 (WslPath $BaselineRoot) --v10 (WslPath $OutputRoot);if($LASTEXITCODE){throw 'assembly failed'};Mark assembly PASS
}
if($Stage -in @('validate','all')){Mark validate RUNNING;$env:ARCHIVE_GLTF_VALIDATOR_DIR=(Resolve-Path "$repo\tools\gltf-validator").Path;node "$repo\scripts\validate_gltf.mjs" --strict --report (Join-Path $OutputRoot 'validation\actual-glb-validation.json') (Join-Path $OutputRoot 'families') (Join-Path $OutputRoot 'infrastructure') (Join-Path $stream 'archive-urban-stream.glb');if($LASTEXITCODE){throw 'official validator failed'};wsl.exe --cd (WslPath $repo) python3 scripts/urban_stream/validate_integrated_stream.py --root (WslPath $OutputRoot);if($LASTEXITCODE){throw 'contract validation failed'};Mark validate PASS}
if($Stage -in @('viewer','all')){Mark viewer RUNNING;Push-Location "$repo\web";try{$env:VITE_ARCHIVE_WORLD_CORE_STREAM_BASE_URL='/generated/v10/core-urban-stream-integrated-rework';npm.cmd run typecheck;npm.cmd test;npm.cmd run build;if($LASTEXITCODE){throw 'viewer failed'}}finally{Pop-Location};Mark viewer PASS}
Write-Output (@{status='PASS';stage=$Stage;outputRoot=$OutputRoot;resume="powershell -File scripts/urban_stream/build_integrated_stream.ps1 -Stage $Stage"}|ConvertTo-Json -Compress)
