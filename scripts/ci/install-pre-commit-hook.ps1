$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
$hooksDir = Join-Path $repoRoot '.git/hooks'
$sourceHook = Join-Path $repoRoot '.githooks/pre-commit'
$targetHook = Join-Path $hooksDir 'pre-commit'

if (-not (Test-Path $hooksDir)) {
    throw "Git hooks directory not found: $hooksDir"
}

if (-not (Test-Path $sourceHook)) {
    throw "Source hook not found: $sourceHook"
}

Copy-Item -Path $sourceHook -Destination $targetHook -Force
Write-Host "Installed pre-commit hook at: $targetHook"
Write-Host "This hook runs scripts/ci/test-L1.ps1 before every commit."
