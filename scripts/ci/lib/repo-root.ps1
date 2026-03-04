function Get-RepoRoot {
    param(
        [Parameter(Mandatory = $true)][string]$ScriptRoot
    )

    return Split-Path -Parent (Split-Path -Parent $ScriptRoot)
}
