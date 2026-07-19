param(
  [ValidateSet('prepare','support','geometry','assembly','validate','viewer','all')][string]$Stage='all',
  [string]$OutputRoot='C:\ArchiveData\World\Generated\v11\core-urban-stream-finalization',
  [string]$BaselineRoot='C:\ArchiveData\World\Generated\v10\core-urban-stream-integrated-rework'
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$blender='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
if(!(Test-Path $blender)){throw 'Blender 5.2 is required'}
$stream=Join-Path $OutputRoot 'stream';$checkpoints=Join-Path $OutputRoot 'checkpoints';$logs=Join-Path $OutputRoot 'logs'
New-Item -ItemType Directory -Force -Path $stream,$checkpoints,$logs | Out-Null
function Mark([string]$name,[string]$status){$payload=@{stage=$name;status=$status;at=(Get-Date).ToUniversalTime().ToString('o')}|ConvertTo-Json;[IO.File]::WriteAllText((Join-Path $checkpoints "$name.json.tmp"),$payload);Move-Item -Force (Join-Path $checkpoints "$name.json.tmp") (Join-Path $checkpoints "$name.json")}
function WslPath([string]$path){$converted=(wsl.exe wslpath -a -- $path.Replace('\','/'));if($LASTEXITCODE -or !$converted){throw "WSL path conversion failed: $path"};return $converted.Trim()}
function RunStage([string]$name,[scriptblock]$action){$checkpoint=Join-Path $checkpoints "$name.json";if(Test-Path $checkpoint){$state=Get-Content $checkpoint -Raw|ConvertFrom-Json;if($state.status -eq 'PASS'){Write-Output "SKIP completed $name";return}};Mark $name RUNNING;& $action *>&1|Tee-Object (Join-Path $logs "$name.log");if($LASTEXITCODE){Mark $name FAIL;throw "$name failed"};Mark $name PASS}

if($Stage -in @('prepare','all')){RunStage prepare {
  if(!(Test-Path (Join-Path $stream 'alignment.json'))){Copy-Item -LiteralPath (Join-Path $BaselineRoot 'stream\alignment.json') -Destination (Join-Path $stream 'alignment.json')}
  foreach($folder in @('families','infrastructure')){if(!(Test-Path (Join-Path $OutputRoot $folder))){Copy-Item -Recurse -LiteralPath (Join-Path $BaselineRoot $folder) -Destination (Join-Path $OutputRoot $folder)}}
}}
if($Stage -in @('support','all')){RunStage support {& $blender -b --factory-startup --python "$repo\scripts\blender\urban_stream_final\support_rework_v11.py" -- --output-root $OutputRoot}}
if($Stage -in @('geometry','all')){RunStage geometry {& $blender -b --factory-startup --python "$repo\scripts\blender\urban_stream_final\generate_final_stream.py" -- --alignment (Join-Path $stream 'alignment.json') --output-root $stream}}
if($Stage -in @('assembly','all')){RunStage assembly {wsl.exe --cd (WslPath $repo) python3 scripts/urban_stream/assemble_final_district.py --v10 (WslPath $BaselineRoot) --v11 (WslPath $OutputRoot)}}
if($Stage -in @('validate','all')){RunStage validate {
  $env:ARCHIVE_GLTF_VALIDATOR_DIR=(Resolve-Path "$repo\tools\gltf-validator").Path
  node "$repo\scripts\validate_gltf.mjs" --strict --report (Join-Path $OutputRoot 'validation\actual-glb-validation.json') (Join-Path $OutputRoot 'families') (Join-Path $OutputRoot 'infrastructure') (Join-Path $stream 'archive-urban-stream-final.glb')
  if($LASTEXITCODE){throw 'official validator failed'}
  wsl.exe --cd (WslPath $repo) python3 scripts/urban_stream/validate_final_district.py --root (WslPath $OutputRoot)
}}
if($Stage -in @('viewer','all')){RunStage viewer {Push-Location "$repo\web";try{$env:VITE_ARCHIVE_WORLD_CORE_STREAM_FINAL_BASE_URL='/generated/v11/core-urban-stream-finalization';$env:VITE_ARCHIVE_WORLD_CORE_STREAM_BASE_URL='/generated/v10/core-urban-stream-integrated-rework';$env:VITE_ARCHIVE_WORLD_CORE_DISTRICT_BASE_URL='/generated/v9/core-district-visual-performance-rework';npm.cmd run typecheck;if($LASTEXITCODE){throw 'typecheck failed'};npm.cmd test;if($LASTEXITCODE){throw 'tests failed'};npm.cmd run build}finally{Pop-Location}}}
Write-Output (@{status='PASS';stage=$Stage;outputRoot=$OutputRoot;resume="powershell -File scripts/urban_stream/build_final_stream.ps1 -Stage $Stage"}|ConvertTo-Json -Compress)
