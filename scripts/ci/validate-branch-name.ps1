[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$slugPattern = "[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
$featurePattern = "^feature/[a-z]+-[0-9]+-${slugPattern}$"
$improvementPattern = "^improvement/${slugPattern}$"
$technicalPattern = "^(fix|docs|chore|refactor|ci)/${slugPattern}$"

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

# Canonical conventions:
# - feature/<id>-<slug> where <id> is like us-42
# - improvement/<slug>
# - (fix|docs|chore|refactor|ci)/<slug>
if (
    ($currentBranch -match $featurePattern) -or
    ($currentBranch -match $improvementPattern) -or
    ($currentBranch -match $technicalPattern)
) {
    Write-Host "Branch naming validation passed: '$currentBranch' matches canonical branch conventions."
    exit 0
}

Write-Error (
    "Invalid branch name '$currentBranch'. Expected one of: " +
    "'feature/<id>-<slug>' (for example 'feature/us-42-visit-summary-export'), " +
    "'improvement/<slug>', or '(fix|docs|chore|refactor|ci)/<slug>'. " +
    "See docs/shared/03-ops/way-of-working.md for canonical branch naming rules."
)
exit 1
