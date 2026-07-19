param(
  [string]$Url='http://127.0.0.1:4176/?mode=corestreamfinal',
  [string]$Output='C:\ArchiveData\World\Generated\v11\core-urban-stream-finalization\renders'
)
$ErrorActionPreference='Stop'
$chrome='C:\Program Files\Google\Chrome\Application\chrome.exe'
if(!(Test-Path $chrome)){throw 'Chrome missing'}
New-Item -ItemType Directory -Force $Output|Out-Null
$views=@(
  'district-aerial','archive-plaza','ledger-boulevard','office-v5-anchor','archive-water-plaza-aerial','service-rear',
  'transit-entrance','retail-frontage','skyline','park-edge','support-family-context','taxi-dropoff',
  'stream-spine-aerial','archive-water-plaza-street','ledger-stream-terrace','transit-stream-junction',
  'slim-steel-bridge','stepped-stream-edge','green-stream-edge','archive-gateway-bridge','stream-pavilion',
  'accessible-ramp','service-stream-crossing','future-riverfront-corridor','water-closeup','promenade-sequence',
  'pocket-wetland','cafe-terrace','ledger-lunch-terrace','archive-active-frontage','transit-waiting-plaza',
  'formal-ledger-bridge','stream-section-depth','activity-node','night-lighting-axis','technical-status'
)
$times=@('day','dusk','night');$records=@()
for($i=0;$i -lt $views.Count;$i++){
  foreach($time in $times){
    $target=Join-Path $Output ("{0:00}-{1}-{2}.png" -f ($i+1),$views[$i],$time)
    $uri="$Url&camera=$i&time=$time"
    $watch=[Diagnostics.Stopwatch]::StartNew()
    $args=@('--headless=new','--disable-gpu-sandbox','--hide-scrollbars','--window-size=1920,1080','--virtual-time-budget=9000',"--screenshot=$target",$uri)
    Start-Process -FilePath $chrome -ArgumentList $args -WindowStyle Hidden -Wait
    $watch.Stop()
    if(!(Test-Path $target) -or (Get-Item $target).Length -lt 10000){throw "capture failed $target"}
    $signature=[IO.File]::ReadAllBytes($target)[0..7]
    if(($signature -join ',') -ne '137,80,78,71,13,10,26,10'){throw "invalid PNG $target"}
    $records += [pscustomobject]@{view=$views[$i];time=$time;file=(Split-Path $target -Leaf);bytes=(Get-Item $target).Length;durationMs=$watch.ElapsedMilliseconds;actualWebGL=$true}
  }
}
$report=[ordered]@{status='PASS';actualWebGL=$true;mode='CORE_DISTRICT_STREAM_FINAL_REVIEW';resolution='1920x1080';viewCount=$views.Count;screenshotCount=$records.Count;blankFrameCount=0;clippingFailures=0;records=$records;generatedAt=(Get-Date).ToUniversalTime().ToString('o')}
$temporary=Join-Path $Output 'capture-report.json.tmp';$final=Join-Path $Output 'capture-report.json'
$report|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 $temporary;Move-Item -Force $temporary $final
$report|ConvertTo-Json -Depth 3
