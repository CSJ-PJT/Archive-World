param(
  [Parameter(Mandatory)][string]$Service,
  [Parameter(Mandatory)][string]$Task,
  [Parameter(Mandatory)][string]$WorkingDirectory,
  [Parameter(ValueFromRemainingArguments=$true)][string[]]$Command
)
if (-not $Command -or $Command.Count -eq 0) { throw 'Provide the task command after the named parameters.' }
& node (Join-Path $PSScriptRoot 'archive-task-runner.mjs') --service $Service --task $Task --cwd $WorkingDirectory -- @Command
exit $LASTEXITCODE
