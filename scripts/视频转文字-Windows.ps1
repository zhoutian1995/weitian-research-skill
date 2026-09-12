# Backward-compatible wrapper for the packaged research-router skill.
$target = Join-Path $PSScriptRoot "..\skills\research-router\scripts\视频转文字-Windows.ps1"
& $target @args
exit $LASTEXITCODE
