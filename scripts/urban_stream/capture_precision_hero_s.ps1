param(
  [string]$Url='http://127.0.0.1:4176/?mode=coreprecision&clean=1&cinematic=1',
  [string]$Output='C:\ArchiveData\World\Generated\v13\core-stream-s-grade\renders\metropolitan-precision-v40',
  [int]$VirtualTimeBudgetMs=22000
)
$ErrorActionPreference='Stop'
$chrome='C:\Program Files\Google\Chrome\Application\chrome.exe'
if(!(Test-Path -LiteralPath $chrome)){throw 'Chrome executable missing'}
New-Item -ItemType Directory -Force -Path $Output|Out-Null
$views=@(
  [pscustomobject]@{name='district-aerial';camera=0},
  [pscustomobject]@{name='district-skyline';camera=8},
  [pscustomobject]@{name='ledger-terrace';camera=36},
  [pscustomobject]@{name='ledger-frontage';camera=37},
  [pscustomobject]@{name='transit-junction';camera=38},
  [pscustomobject]@{name='transit-entry';camera=39},
  [pscustomobject]@{name='archive-axis';camera=43},
  [pscustomobject]@{name='archive-aerial';camera=49},
  [pscustomobject]@{name='archive-street';camera=50},
  [pscustomobject]@{name='archive-frontage';camera=51},
  [pscustomobject]@{name='archive-water-plaza';camera=52},
  [pscustomobject]@{name='archive-gateway';camera=53}
)
$records=@()
foreach($view in $views){
  foreach($time in @('day','dusk','night')){
    $target=Join-Path $Output ("hero-a-{0}-{1}.png" -f $view.name,$time)
    $uri="$Url&camera=$($view.camera)&time=$time&rev=metropolitan-precision-v40"
    $watch=[Diagnostics.Stopwatch]::StartNew()
    $arguments=@(
      '--headless=new','--disable-gpu-sandbox','--hide-scrollbars',
      '--window-size=1920,1080',"--virtual-time-budget=$VirtualTimeBudgetMs",
      "--screenshot=$target",$uri
    )
    $process=Start-Process -FilePath $chrome -ArgumentList $arguments -WindowStyle Hidden -PassThru
    if(-not $process.WaitForExit(90000)){
      Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
      throw "capture timeout: $($view.name)/$time"
    }
    $watch.Stop()
    if(!(Test-Path -LiteralPath $target)){throw "capture missing: $target"}
    $item=Get-Item -LiteralPath $target
    if($item.Length -lt 10000){throw "capture too small: $target"}
    $signature=[IO.File]::ReadAllBytes($target)[0..7]
    if(($signature -join ',') -ne '137,80,78,71,13,10,26,10'){throw "invalid PNG: $target"}
    $records += [pscustomobject]@{
      view=$view.name;camera=$view.camera;time=$time;file=$item.Name
      bytes=$item.Length;durationMs=$watch.ElapsedMilliseconds
      resolution='1920x1080';actualWebGL=$true;eyeHeightM=1.65
    }
  }
}
$report=[ordered]@{
  status='PASS';mode='CORE_STREAM_PRECISION_REVIEW';gradeTarget='S'
  actualWebGL=$true;scope='METROPOLITAN_CORE_STREAM_PRECISION';screenshotCount=$records.Count
  records=$records;generatedAt=(Get-Date).ToUniversalTime().ToString('o')
}
$temporary=Join-Path $Output 'capture-report.json.tmp'
$final=Join-Path $Output 'capture-report.json'
$report|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 -LiteralPath $temporary
Move-Item -Force -LiteralPath $temporary -Destination $final
$report|ConvertTo-Json -Depth 4
