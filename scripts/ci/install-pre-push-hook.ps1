$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'lib\repo-root.ps1')
$repoRoot = Get-RepoRoot -ScriptRoot $PSScriptRoot
$sourceHook = Join-Path $repoRoot '.githooks/pre-push'

$hooksDir = (& git -C $repoRoot rev-parse --git-path hooks).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($hooksDir)) {
    throw "Unable to resolve git hooks directory via 'git rev-parse --git-path hooks'."
}

$targetHook = Join-Path $hooksDir 'pre-push'

if (-not (Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
}

if (-not (Test-Path $sourceHook)) {
    throw "Source hook not found: $sourceHook"
}

Copy-Item -Path $sourceHook -Destination $targetHook -Force
Write-Host "Installed pre-push hook at: $targetHook"
Write-Host "This hook runs scripts/ci/test-remote-mirror.ps1 before every push."
