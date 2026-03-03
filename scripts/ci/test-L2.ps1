[CmdletBinding()]
param(
    [string]$BaseRef = "main",
    [switch]$SkipDocker,
    [switch]$ForceFrontend
)

$scriptPath = Join-Path $PSScriptRoot "preflight-ci-local.ps1"
& $scriptPath -Mode Push -BaseRef $BaseRef -SkipDocker:$SkipDocker -ForceFrontend:$ForceFrontend
exit $LASTEXITCODE