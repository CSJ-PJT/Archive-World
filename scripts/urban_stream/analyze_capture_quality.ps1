param(
  [Parameter(Mandatory=$true)][string]$InputDirectory,
  [string]$OutputReport='capture-quality.json',
  [int]$SampleStride=8
)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$records=@()
foreach($file in Get-ChildItem -LiteralPath $InputDirectory -Filter '*.png' | Sort-Object Name){
  $bitmap=[Drawing.Bitmap]::FromFile($file.FullName)
  try{
    $values=[Collections.Generic.List[double]]::new()
    for($y=0;$y -lt $bitmap.Height;$y+=$SampleStride){
      for($x=0;$x -lt $bitmap.Width;$x+=$SampleStride){
        $pixel=$bitmap.GetPixel($x,$y)
        $luma=(0.2126*$pixel.R+0.7152*$pixel.G+0.0722*$pixel.B)/255.0
        $values.Add($luma)
      }
    }
    $sorted=$values.ToArray();[Array]::Sort($sorted)
    $count=$sorted.Count
    $mean=($sorted|Measure-Object -Average).Average
    $p05=$sorted[[Math]::Min($count-1,[Math]::Floor($count*.05))]
    $p50=$sorted[[Math]::Min($count-1,[Math]::Floor($count*.50))]
    $p95=$sorted[[Math]::Min($count-1,[Math]::Floor($count*.95))]
    $black=($sorted|Where-Object{$_ -lt .025}).Count/[double]$count
    $white=($sorted|Where-Object{$_ -gt .975}).Count/[double]$count
    $variance=(($sorted|ForEach-Object{($_-$mean)*($_-$mean)}|Measure-Object -Average).Average)
    $signature=[IO.File]::ReadAllBytes($file.FullName)[0..7] -join ','
    $pass=($file.Length -gt 10000 -and $signature -eq '137,80,78,71,13,10,26,10' -and
      $mean -ge .12 -and $mean -le .88 -and ($p95-$p05) -ge .12 -and
      $black -le .20 -and $white -le .10 -and $variance -ge .002)
    $records += [pscustomobject]@{
      file=$file.Name;width=$bitmap.Width;height=$bitmap.Height;bytes=$file.Length
      mean=[Math]::Round($mean,4);p05=[Math]::Round($p05,4);p50=[Math]::Round($p50,4);p95=[Math]::Round($p95,4)
      blackClip=[Math]::Round($black,5);whiteClip=[Math]::Round($white,5)
      contrast=[Math]::Round($p95-$p05,4);variance=[Math]::Round($variance,5)
      pngSignature=($signature -eq '137,80,78,71,13,10,26,10');blankFrame=($variance -lt .002);pass=$pass
    }
  } finally {$bitmap.Dispose()}
}
if($records.Count -eq 0){throw 'No PNG captures found'}
$report=[ordered]@{
  status=if(($records|Where-Object{-not $_.pass}).Count -eq 0){'PASS'}else{'FAIL'}
  input=(Resolve-Path -LiteralPath $InputDirectory).Path
  count=$records.Count;sampleStride=$SampleStride;records=$records
  generatedAt=(Get-Date).ToUniversalTime().ToString('o')
}
$target=if([IO.Path]::IsPathRooted($OutputReport)){$OutputReport}else{Join-Path $InputDirectory $OutputReport}
$temporary="$target.tmp"
$report|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 -LiteralPath $temporary
Move-Item -Force -LiteralPath $temporary -Destination $target
$report|ConvertTo-Json -Depth 4
if($report.status -ne 'PASS'){exit 2}
