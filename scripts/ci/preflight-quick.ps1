[CmdletBinding()]
param(
    [string]$BaseRef = "main"
)

$scriptPath = Join-Path $PSScriptRoot "test-L1.ps1"
& $scriptPath -BaseRef $BaseRef
exit $LASTEXITCODE
