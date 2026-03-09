[CmdletBinding()]
param(
    [string]$BaseRef = "main",
    [switch]$SkipDocker,
    [switch]$SkipE2E,
    [switch]$ForceFrontend,
    [switch]$ForceFull
)

if ($PSVersionTable.PSVersion -lt [Version]"5.0") {
    Write-Error "This script must be run in PowerShell 5.0 or later."
    exit 1
}

$scriptPath = Join-Path $PSScriptRoot "preflight-ci-local.ps1"
if (-not (Test-Path $scriptPath)) {
    Write-Error "Expected preflight script not found: $scriptPath"
    exit 1
}
& "$scriptPath" -Mode Full -BaseRef $BaseRef -SkipDocker:$SkipDocker -SkipE2E:$SkipE2E -ForceFrontend:$ForceFrontend -ForceFull:$ForceFull
exit $LASTEXITCODE
