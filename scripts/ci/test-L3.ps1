[CmdletBinding()]
param(
    [string]$BaseRef = "main",
    [switch]$SkipDocker,
    [switch]$SkipE2E,
    [switch]$ForceFrontend,
    [switch]$ForceFull
)

$scriptPath = Join-Path $PSScriptRoot "preflight-ci-local.ps1"
& $scriptPath -Mode Full -BaseRef $BaseRef -SkipDocker:$SkipDocker -SkipE2E:$SkipE2E -ForceFrontend:$ForceFrontend -ForceFull:$ForceFull
exit $LASTEXITCODE