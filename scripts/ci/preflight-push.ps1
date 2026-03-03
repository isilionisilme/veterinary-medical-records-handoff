[CmdletBinding()]
param(
    [string]$BaseRef = "main",
    [switch]$SkipDocker,
    [switch]$ForceFrontend
)

$scriptPath = Join-Path $PSScriptRoot "test-L2.ps1"
& $scriptPath -BaseRef $BaseRef -SkipDocker:$SkipDocker -ForceFrontend:$ForceFrontend
exit $LASTEXITCODE
