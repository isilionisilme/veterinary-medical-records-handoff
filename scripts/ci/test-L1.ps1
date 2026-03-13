[CmdletBinding()]
param(
    [string]$BaseRef = "main",
    [switch]$AllowNonParityBaseRef
)

$normalizedBaseRef = $BaseRef.Trim().ToLowerInvariant()
$isHeadRef = $normalizedBaseRef -eq "head" -or $normalizedBaseRef -eq "refs/heads/head"

if ($isHeadRef -and -not $AllowNonParityBaseRef.IsPresent) {
    Write-Error "test-L1.ps1 with BaseRef=HEAD is a quick local check only and does not mirror CI. Use scripts/ci/test-L2.ps1 for CI-parity before push, or pass -AllowNonParityBaseRef to acknowledge this explicitly."
    exit 2
}

$scriptPath = Join-Path $PSScriptRoot "preflight-ci-local.ps1"
& $scriptPath -Mode Quick -BaseRef $BaseRef
exit $LASTEXITCODE