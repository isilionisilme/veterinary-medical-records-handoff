[CmdletBinding()]
param(
    [string]$BaseRef = "main",
    [switch]$SkipDocker,
    [switch]$SkipE2E,
    [switch]$ForceFrontend,
    [switch]$ForceFull
)

$scriptPath = Join-Path $PSScriptRoot "test-L3.ps1"
& $scriptPath -BaseRef $BaseRef -SkipDocker:$SkipDocker -SkipE2E:$SkipE2E -ForceFrontend:$ForceFrontend -ForceFull:$ForceFull
exit $LASTEXITCODE
