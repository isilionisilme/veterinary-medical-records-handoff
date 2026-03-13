[CmdletBinding()]
param(
    [string]$BaseRef = "main",
    [switch]$SkipDocker,
    [switch]$SkipE2E,
    [switch]$ForceFrontend,
    [switch]$IncludeLocalEdits
)

$scriptPath = Join-Path $PSScriptRoot "preflight-ci-local.ps1"
$parityMode = -not $IncludeLocalEdits.IsPresent
& $scriptPath -Mode CI -BaseRef $BaseRef -SkipDocker:$SkipDocker -SkipE2E:$SkipE2E -ForceFrontend:$ForceFrontend -ParityMode:$parityMode
if (-not $?) {
    exit 1
}
exit 0
