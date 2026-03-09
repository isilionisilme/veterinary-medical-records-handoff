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

# Canonical convention: <category>/<slug>
$categoryPattern = "^(${allowedCategories})/[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"

if ($currentBranch -match $categoryPattern) {
    Write-Host "Branch naming validation passed: '$currentBranch' matches '<category>/<slug>'."
    exit 0
}

Write-Error (
    "Invalid branch name '$currentBranch'. Expected format: '<category>/<slug>' " +
    "with category in [feature, improvement, refactor, chore, ci, docs, fix]. " +
    "See docs/shared/03-ops/way-of-working.md for canonical branch naming rules."
)
exit 1
