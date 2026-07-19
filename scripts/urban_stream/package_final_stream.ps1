param(
  [string]$OutputRoot='C:\ArchiveData\World\Generated\v11\core-urban-stream-finalization',
  [string]$TransferRoot='C:\ArchiveTransfer',
  [string]$ConceptTarget='C:\Users\dan18\OneDrive\문서\Archive\.codex-remote-attachments\019f66d4-9743-77f2-a4b1-066f5f7dd81d\713decf8-a672-4215-ad14-2081dbe89d97\1-Photo-1.jpg'
)
$ErrorActionPreference='Stop'
if(!(Test-Path $OutputRoot)){throw 'V11 output root missing'}
if(!(Test-Path $ConceptTarget)){throw 'Concept target missing'}
$repo=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$reference=Join-Path $OutputRoot 'references';New-Item -ItemType Directory -Force $reference|Out-Null
Copy-Item -LiteralPath $ConceptTarget -Destination (Join-Path $reference 'concept-target-reference-only.jpg') -Force
$head=(git -C $repo rev-parse HEAD).Trim();$branch=(git -C $repo branch --show-current).Trim()
$manifest=[ordered]@{
  title='Archive Core + Urban Stream Finalization V1'
  status='PARTIAL'
  branch=$branch
  head=$head
  outputRoot=$OutputRoot
  conceptTarget='REFERENCE_ONLY_NOT_IMPLEMENTATION_OUTPUT'
  originality='ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY'
  canonical=$false
  v3Applied=$false
  runtimeChanged=$false
  contents=@('38 actual GLBs','manifest and chunks','108 actual WebGL screenshots','headless performance traces','strict validator report','evidence-linked visual gate','known limitations')
  generatedAt=(Get-Date).ToUniversalTime().ToString('o')
}
$manifest|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 (Join-Path $OutputRoot 'package-manifest.json')
$files=Get-ChildItem -LiteralPath $OutputRoot -Recurse -File|Where-Object {$_.Extension -ne '.zip'}
$checksums=$files|ForEach-Object {[pscustomobject]@{path=$_.FullName.Substring($OutputRoot.Length+1).Replace('\','/');sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant();bytes=$_.Length}}
$checksums|ConvertTo-Json -Depth 4|Set-Content -Encoding utf8 (Join-Path $OutputRoot 'checksums.json')
New-Item -ItemType Directory -Force $TransferRoot|Out-Null
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss';$zip=Join-Path $TransferRoot "Archive-Core-Urban-Stream-Final-V1-$stamp.zip"
Compress-Archive -LiteralPath $OutputRoot -DestinationPath $zip -CompressionLevel Optimal
$zipHash=(Get-FileHash -Algorithm SHA256 -LiteralPath $zip).Hash.ToLowerInvariant()
$result=[ordered]@{status='PASS';zip=$zip;sha256=$zipHash;bytes=(Get-Item $zip).Length;fileCount=$files.Count;branch=$branch;head=$head}
$result|ConvertTo-Json -Depth 4|Set-Content -Encoding utf8 (Join-Path $OutputRoot 'package-result.json')
$result|ConvertTo-Json -Depth 4
