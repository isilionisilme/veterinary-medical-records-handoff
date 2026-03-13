[CmdletBinding()]
param(
    [string]$BaseRef = "main",
    [switch]$SkipDocker,
    [switch]$ForceFrontend,
    [switch]$IncludeLocalEdits
)

$scriptPath = Join-Path $PSScriptRoot "preflight-ci-local.ps1"
$parityMode = -not $IncludeLocalEdits.IsPresent
& $scriptPath -Mode Push -BaseRef $BaseRef -SkipDocker:$SkipDocker -ForceFrontend:$ForceFrontend -ParityMode:$parityMode
exit $LASTEXITCODE