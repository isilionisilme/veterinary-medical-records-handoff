[CmdletBinding()]
param(
    [string]$BaseRef = "main"
)

$scriptPath = Join-Path $PSScriptRoot "preflight-ci-local.ps1"
& $scriptPath -Mode Quick -BaseRef $BaseRef
exit $LASTEXITCODE