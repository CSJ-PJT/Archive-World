param([Parameter(Mandatory=$true)][string]$InputDirectory)
$chrome=@('C:\Program Files\Google\Chrome\Application\chrome.exe','C:\Program Files (x86)\Google\Chrome\Application\chrome.exe')|Where-Object{Test-Path $_}|Select-Object -First 1
if(-not $chrome){throw 'Chrome not installed; PNG conversion is BLOCKED.'}
$png=Join-Path $InputDirectory 'png';New-Item -ItemType Directory -Force $png|Out-Null
Get-ChildItem -LiteralPath $InputDirectory -Filter *.svg|ForEach-Object{
 $target=Join-Path $png ($_.BaseName+'.png');$uri='file:///'+($_.FullName -replace '\\','/')
 & $chrome --headless --disable-gpu --hide-scrollbars --window-size=1920,1080 --screenshot=$target $uri 2>$null|Out-Null
 if(!(Test-Path $target) -or (Get-Item $target).Length -lt 1000){throw "PNG conversion failed: $($_.Name)"}
}
$files=Get-ChildItem $png -Filter *.png;[pscustomobject]@{status='PASS';count=$files.Count;bytes=($files|Measure-Object Length -Sum).Sum}|ConvertTo-Json
