$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
$hooksDir = Join-Path $repoRoot '.git/hooks'
$sourceHook = Join-Path $repoRoot '.githooks/pre-push'
$targetHook = Join-Path $hooksDir 'pre-push'

if (-not (Test-Path $hooksDir)) {
    throw "Git hooks directory not found: $hooksDir"
}

if (-not (Test-Path $sourceHook)) {
    throw "Source hook not found: $sourceHook"
}

Copy-Item -Path $sourceHook -Destination $targetHook -Force
Write-Host "Installed pre-push hook at: $targetHook"
Write-Host "This hook runs scripts/ci/test-L2.ps1 before every push."
