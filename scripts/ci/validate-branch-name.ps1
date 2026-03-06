[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$allowedCategories = "feature|fix|docs|chore|refactor|ci|improvement"

$currentBranch = (& git branch --show-current 2>$null).Trim()
if ($LASTEXITCODE -ne 0) {
    Write-Error "Could not detect current branch name using 'git branch --show-current'."
    exit 1
}

# Detached HEAD returns empty branch name; this state is explicitly exempt.
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    Write-Host "Branch naming validation skipped: detached HEAD detected."
    exit 0
}

if ($currentBranch -eq "main") {
    Write-Host "Branch naming validation skipped: 'main' is exempt."
    exit 0
}

$repoTopLevel = (& git rev-parse --show-toplevel 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repoTopLevel)) {
    Write-Error "Could not detect repository top-level path using 'git rev-parse --show-toplevel'."
    exit 1
}

$expectedWorktree = Split-Path -Path $repoTopLevel -Leaf
if ([string]::IsNullOrWhiteSpace($expectedWorktree)) {
    Write-Error "Could not derive expected worktree name from repository path: $repoTopLevel"
    exit 1
}

$escapedWorktree = [Regex]::Escape($expectedWorktree)
$newFormatPattern = "^${escapedWorktree}/(${allowedCategories})/[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
$legacyPattern = "^(${allowedCategories})/.+"

if ($currentBranch -match $newFormatPattern) {
    Write-Host "Branch naming validation passed: '$currentBranch' matches '<worktree>/<category>/<slug>'."
    exit 0
}

if ($currentBranch -match $legacyPattern) {
    Write-Warning "Branch '$currentBranch' matches legacy '<category>/<slug>' format. Allowed temporarily during transition; please migrate to '$expectedWorktree/<category>/<slug>'."
    exit 0
}

Write-Error (
    "Invalid branch name '$currentBranch'. Expected format: '<worktree>/<category>/<slug>' " +
    "with worktree '$expectedWorktree' and category in [feature, fix, docs, chore, refactor, ci, improvement]. " +
    "Legacy '<category>/<slug>' is temporarily allowed with warning only."
)
exit 1
