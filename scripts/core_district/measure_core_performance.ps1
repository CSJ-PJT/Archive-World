param(
  [string]$Url = 'http://127.0.0.1:4176/?mode=core3d',
  [string]$Output = 'C:\ArchiveData\World\Generated\v9\core-district-visual-performance-rework\performance',
  [int]$DurationSeconds = 30,
  [int]$Port = 9339
)
$ErrorActionPreference='Stop'
$chrome='C:\Program Files\Google\Chrome\Application\chrome.exe'
if(!(Test-Path $chrome)){throw 'Chrome executable missing'}
New-Item -ItemType Directory -Force $Output|Out-Null
$profile=Join-Path $Output 'chrome-profile'
$results=@()
foreach($mode in @('day','night')){
  $target="$Url&camera=0&time=$mode"
  $args=@('--headless=new','--disable-gpu-sandbox','--hide-scrollbars','--window-size=1920,1080',"--remote-debugging-port=$Port","--user-data-dir=$profile",$target)
  $process=Start-Process -FilePath $chrome -ArgumentList $args -WindowStyle Hidden -PassThru
  try{
    $deadline=(Get-Date).AddSeconds(15);$page=$null
    do{Start-Sleep -Milliseconds 500;try{$page=(Invoke-RestMethod "http://127.0.0.1:$Port/json")[0]}catch{}}until($page -or (Get-Date)-gt $deadline)
    if(!$page){throw "Chrome CDP startup timeout: $mode"}
    $samples=@();$until=(Get-Date).AddSeconds($DurationSeconds)
    while((Get-Date)-lt $until){
      Start-Sleep -Seconds 1
      $page=(Invoke-RestMethod "http://127.0.0.1:$Port/json")[0]
      if($page.title -match '^CORE3D\|([0-9.]+)\|([0-9.]+)\|([0-9]+)\|([0-9]+)$'){
        $samples += [pscustomobject]@{fps=[double]$Matches[1];lowFps=[double]$Matches[2];drawCalls=[int]$Matches[3];triangles=[int64]$Matches[4];at=(Get-Date).ToString('o')}
      }
    }
    if(!$samples){throw "No valid performance samples: $mode"}
    $stable=$samples|Select-Object -Last ([Math]::Min(15,$samples.Count))
    $results += [pscustomobject]@{mode=$mode;headless=$true;durationSeconds=$DurationSeconds;sampleCount=$samples.Count;averageFps=[Math]::Round(($stable|Measure-Object fps -Average).Average,1);onePercentLow=[Math]::Round(($stable|Measure-Object lowFps -Minimum).Minimum,1);criticalFps=[Math]::Round(($stable|Measure-Object fps -Minimum).Minimum,1);drawCalls=($stable|Select-Object -Last 1).drawCalls;triangles=($stable|Select-Object -Last 1).triangles;samples=$samples}
  } finally {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
  }
}
$version=(Get-Item $chrome).VersionInfo.FileVersion
$report=[ordered]@{status='PASS';measurement='HEADLESS_CHROME_ACTUAL_WEBGL';chromeVersion=$version;viewport='1920x1080';devicePixelRatio=1;hardwareChrome='UNKNOWN_NOT_MEASURED';results=$results;generatedAt=(Get-Date).ToString('o')}
$report|ConvertTo-Json -Depth 8|Set-Content -Encoding utf8 (Join-Path $Output 'viewer-performance.json')
$report|ConvertTo-Json -Depth 5
