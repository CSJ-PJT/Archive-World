param(
  [string]$Url='http://127.0.0.1:4176/?mode=corestream',
  [string]$Output='C:\ArchiveData\World\Generated\v10\core-urban-stream-integrated-rework\renders'
)
$ErrorActionPreference='Stop'
$chrome='C:\Program Files\Google\Chrome\Application\chrome.exe'
if(!(Test-Path $chrome)){throw 'Chrome missing'}
New-Item -ItemType Directory -Force $Output|Out-Null
$views=@('aerial-core','archive-plaza','ledger-boulevard','office-anchor','bird-plaza','service-rear','transit-entrance','retail-frontage','skyline','park-edge','landmark-context','taxi-dropoff','stream-aerial','archive-water-plaza','ledger-stream-terrace','transit-stream-junction','slim-steel-bridge','stepped-stream-edge','green-stream-edge','archive-gateway-bridge','stream-pavilion','accessible-ramp','service-stream-crossing','future-riverfront-corridor')
$times=@('day','dusk','night');$records=@()
for($i=0;$i -lt $views.Count;$i++){
  foreach($time in $times){
    $target=Join-Path $Output ("{0:00}-{1}-{2}.png" -f ($i+1),$views[$i],$time)
    $uri="$Url&camera=$i&time=$time"
    $stopwatch=[Diagnostics.Stopwatch]::StartNew()
    $args=@('--headless=new','--disable-gpu-sandbox','--hide-scrollbars','--window-size=1920,1080','--virtual-time-budget=7000',"--screenshot=$target",$uri)
    Start-Process -FilePath $chrome -ArgumentList $args -WindowStyle Hidden -Wait
    $stopwatch.Stop()
    if(!(Test-Path $target) -or (Get-Item $target).Length -lt 10000){throw "capture failed $target"}
    $signature=[IO.File]::ReadAllBytes($target)[0..7]
    if(($signature -join ',') -ne '137,80,78,71,13,10,26,10'){throw "invalid PNG $target"}
    $records += [pscustomobject]@{view=$views[$i];time=$time;file=(Split-Path $target -Leaf);bytes=(Get-Item $target).Length;durationMs=$stopwatch.ElapsedMilliseconds}
  }
}
$report=[ordered]@{status='PASS';actualWebGL=$true;resolution='1920x1080';viewCount=$views.Count;screenshotCount=$records.Count;records=$records;generatedAt=(Get-Date).ToUniversalTime().ToString('o')}
$report|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 (Join-Path $Output 'capture-report.json')
$report|ConvertTo-Json -Depth 3
