# Backward-compatible wrapper for the packaged research-router skill.
$target = Join-Path $PSScriptRoot "..\skills\research-router\scripts\transcribe-windows.ps1"
& $target @args
exit $LASTEXITCODE
