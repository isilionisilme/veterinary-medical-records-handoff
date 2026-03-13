[CmdletBinding()]
param(
    [string]$BaseRef = "origin/main",
    [switch]$SkipDocker,
    [switch]$SkipE2E,
    [switch]$ForceFrontend,
    [switch]$IncludeLocalEdits
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "lib\repo-root.ps1")
$repoRoot = Get-RepoRoot -ScriptRoot $PSScriptRoot
Set-Location $repoRoot

function Resolve-RemoteRefParts {
    param([Parameter(Mandatory = $true)][string]$Ref)

    $normalized = $Ref.Trim()
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        throw "BaseRef cannot be empty."
    }

    if ($normalized.StartsWith("refs/heads/", [System.StringComparison]::OrdinalIgnoreCase)) {
        $normalized = $normalized.Substring("refs/heads/".Length)
    }

    if ($normalized.StartsWith("refs/remotes/", [System.StringComparison]::OrdinalIgnoreCase)) {
        $normalized = $normalized.Substring("refs/remotes/".Length)
    }

    if ($normalized -match '^(?<remote>[^/]+)/(?<branch>.+)$') {
        return @{
            Remote = $Matches.remote
            Branch = $Matches.branch
            Canonical = "$($Matches.remote)/$($Matches.branch)"
        }
    }

    return @{
        Remote = "origin"
        Branch = $normalized
        Canonical = "origin/$normalized"
    }
}

$remoteRef = Resolve-RemoteRefParts -Ref $BaseRef
Write-Host "pre-push remote mirror: ensuring sync with $($remoteRef.Canonical)"

& git fetch --quiet $remoteRef.Remote $remoteRef.Branch
if ($LASTEXITCODE -ne 0) {
    throw "Remote mirror failed: could not fetch $($remoteRef.Canonical). Push blocked."
}

& git show-ref --verify --quiet ("refs/remotes/{0}/{1}" -f $remoteRef.Remote, $remoteRef.Branch)
if ($LASTEXITCODE -ne 0) {
    throw "Remote mirror failed: missing refs/remotes/$($remoteRef.Remote)/$($remoteRef.Branch). Push blocked."
}

& git merge-base --is-ancestor $remoteRef.Canonical HEAD
if ($LASTEXITCODE -ne 0) {
    throw (
        "Remote mirror failed: current branch does not contain the latest $($remoteRef.Canonical). " +
        "Rebase or merge $($remoteRef.Canonical) before pushing."
    )
}

$scriptPath = Join-Path $PSScriptRoot "test-CI.ps1"
& $scriptPath -BaseRef $remoteRef.Canonical -SkipDocker:$SkipDocker -SkipE2E:$SkipE2E -ForceFrontend:$ForceFrontend -IncludeLocalEdits:$IncludeLocalEdits
if (-not $?) {
    exit 1
}
exit 0
