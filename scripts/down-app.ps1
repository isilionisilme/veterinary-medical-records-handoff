param(
    [int]$DocsPort = 8081
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    $env:DOCS_PORT = "$DocsPort"
    $docsRepoDefault = Join-Path (Split-Path $repoRoot -Parent) "veterinary-medical-records-documentation"
    $docsRepoWorktree = Join-Path (Split-Path (Split-Path $repoRoot -Parent) -Parent) "veterinary-medical-records-documentation"
    if (Test-Path $docsRepoDefault) {
        $env:DOCS_REPO_PATH = $docsRepoDefault
    }
    elseif (Test-Path $docsRepoWorktree) {
        $env:DOCS_REPO_PATH = $docsRepoWorktree
    }
    docker compose -f docker-compose.yml -f docker-compose.evaluators.yml down
}
finally {
    Pop-Location
}
